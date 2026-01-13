"""
Handles multiple locators with automatic fallback, retry logic, and detailed logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from config.settings import settings


class LocatorType(Enum):
    """Supported locator types."""

    XPATH = "xpath"
    CSS = "css"
    TEXT = "text"
    ROLE = "role"
    TEST_ID = "test_id"
    LABEL = "label"
    PLACEHOLDER = "placeholder"
    ALT_TEXT = "alt_text"


@dataclass
class LocatorDefinition:
    """Definition of a single locator strategy."""

    locator_type: LocatorType
    value: str
    description: str = ""

    def __str__(self) -> str:
        return f"{self.locator_type.value}: {self.value}"


@dataclass
class SmartLocator:
    """
    Smart locator that holds multiple locator strategies.
    Enables automatic fallback when primary locator fails.
    """

    name: str  # Human-readable name for logging
    locators: List[LocatorDefinition] = field(default_factory=list)
    timeout: int = settings.LOCATOR.locator_timeout

    def add_locator(
        self, locator_type: LocatorType, value: str, description: str = ""
    ) -> "SmartLocator":
        """Add a locator strategy. Returns self for chaining."""
        self.locators.append(LocatorDefinition(locator_type, value, description))
        return self

    def add_xpath(self, xpath: str, description: str = "") -> "SmartLocator":
        """Add an XPath locator."""
        return self.add_locator(LocatorType.XPATH, xpath, description)

    def add_css(self, css: str, description: str = "") -> "SmartLocator":
        """Add a CSS selector locator."""
        return self.add_locator(LocatorType.CSS, css, description)

    def add_text(self, text: str, description: str = "") -> "SmartLocator":
        """Add a text-based locator."""
        return self.add_locator(LocatorType.TEXT, text, description)

    def add_role(self, role: str, description: str = "") -> "SmartLocator":
        """Add a role-based locator."""
        return self.add_locator(LocatorType.ROLE, role, description)

    def add_test_id(self, test_id: str, description: str = "") -> "SmartLocator":
        """Add a test ID locator."""
        return self.add_locator(LocatorType.TEST_ID, test_id, description)


@dataclass
class LocatorAttemptResult:
    """Result of a single locator attempt."""

    locator_definition: LocatorDefinition
    attempt_number: int
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LocatorResolutionResult:
    """Complete result of resolving a smart locator."""

    smart_locator_name: str
    success: bool
    playwright_locator: Optional[Locator] = None
    successful_locator: Optional[LocatorDefinition] = None
    attempts: List[LocatorAttemptResult] = field(default_factory=list)
    total_attempts: int = 0
    screenshot_path: Optional[str] = None


class SmartLocatorResolver:
    """
    Resolves smart locators with automatic fallback and detailed logging.
    This is the core engine that tries multiple locators until one succeeds.
    """

    def __init__(self, page: Page, logger: Optional[logging.Logger] = None):
        self.page = page
        self.logger = logger or logging.getLogger(__name__)
        self._screenshot_counter = 0

    def _get_playwright_locator(self, locator_def: LocatorDefinition) -> Locator:
        """Convert a LocatorDefinition to a Playwright Locator."""
        match locator_def.locator_type:
            case LocatorType.XPATH:
                return self.page.locator(f"xpath={locator_def.value}")
            case LocatorType.CSS:
                return self.page.locator(locator_def.value)
            case LocatorType.TEXT:
                return self.page.get_by_text(locator_def.value)
            case LocatorType.ROLE:
                # Role format: "button[name=Submit]" or just "button"
                parts = locator_def.value.split("[")
                role = parts[0]
                if len(parts) > 1:
                    name = parts[1].rstrip("]").split("=")[1]
                    return self.page.get_by_role(role, name=name)
                return self.page.get_by_role(role)
            case LocatorType.TEST_ID:
                return self.page.get_by_test_id(locator_def.value)
            case LocatorType.LABEL:
                return self.page.get_by_label(locator_def.value)
            case LocatorType.PLACEHOLDER:
                return self.page.get_by_placeholder(locator_def.value)
            case LocatorType.ALT_TEXT:
                return self.page.get_by_alt_text(locator_def.value)
            case _:
                raise ValueError(f"Unknown locator type: {locator_def.locator_type}")

    def _capture_failure_screenshot(self, smart_locator: SmartLocator) -> Optional[str]:
        """Capture screenshot on final locator failure."""
        if not settings.LOCATOR.screenshot_on_failure:
            return None

        try:
            settings.ensure_directories()
            self._screenshot_counter += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"locator_failure_{smart_locator.name}_{timestamp}_{self._screenshot_counter}.png"
            filepath = settings.SCREENSHOTS_DIR / filename
            self.page.screenshot(path=str(filepath))
            self.logger.info(f"Failure screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.warning(f"Failed to capture screenshot: {e}")
            return None

    def resolve(
        self, smart_locator: SmartLocator, wait_for_visible: bool = True
    ) -> LocatorResolutionResult:
        """
        Resolve a smart locator by trying each locator strategy in order.

        Args:
            smart_locator: The SmartLocator containing multiple strategies
            wait_for_visible: Whether to wait for the element to be visible

        Returns:
            LocatorResolutionResult with all attempt details
        """
        result = LocatorResolutionResult(
            smart_locator_name=smart_locator.name, success=False
        )

        if not smart_locator.locators:
            self.logger.error(
                f"SmartLocator '{smart_locator.name}' has no locator definitions"
            )
            return result

        max_attempts = min(
            len(smart_locator.locators), settings.LOCATOR.max_locator_retries
        )

        self.logger.info(
            f"Resolving SmartLocator '{smart_locator.name}' - "
            f"{len(smart_locator.locators)} locators available, "
            f"max {max_attempts} attempts"
        )

        for attempt_num, locator_def in enumerate(
            smart_locator.locators[:max_attempts], 1
        ):
            result.total_attempts = attempt_num
            attempt_result = LocatorAttemptResult(
                locator_definition=locator_def,
                attempt_number=attempt_num,
                success=False,
            )

            self.logger.debug(
                f"Attempt {attempt_num}/{max_attempts}: "
                f"Trying {locator_def.locator_type.value}='{locator_def.value}'"
            )

            try:
                playwright_locator = self._get_playwright_locator(locator_def)

                if wait_for_visible:
                    playwright_locator.wait_for(
                        state="visible", timeout=smart_locator.timeout
                    )
                else:
                    playwright_locator.wait_for(
                        state="attached", timeout=smart_locator.timeout
                    )

                # Verify element count (at least one element found)
                if playwright_locator.count() > 0:
                    attempt_result.success = True
                    result.success = True
                    result.playwright_locator = playwright_locator
                    result.successful_locator = locator_def

                    self.logger.info(
                        f"SUCCESS: SmartLocator '{smart_locator.name}' resolved on "
                        f"attempt {attempt_num} using {locator_def.locator_type.value}='{locator_def.value}'"
                    )
                    result.attempts.append(attempt_result)
                    return result
                else:
                    attempt_result.error_message = "No elements found"

            except PlaywrightTimeout as e:
                attempt_result.error_message = f"Timeout: {str(e)}"
                self.logger.warning(
                    f"Attempt {attempt_num} FAILED for '{smart_locator.name}': "
                    f"{locator_def} - Timeout"
                )
            except Exception as e:
                attempt_result.error_message = str(e)
                self.logger.warning(
                    f"Attempt {attempt_num} FAILED for '{smart_locator.name}': "
                    f"{locator_def} - {str(e)}"
                )

            result.attempts.append(attempt_result)

        # All attempts failed
        self.logger.error(
            f"FAILED: SmartLocator '{smart_locator.name}' could not be resolved "
            f"after {result.total_attempts} attempts"
        )
        result.screenshot_path = self._capture_failure_screenshot(smart_locator)

        return result

    def find_element(
        self, smart_locator: SmartLocator, wait_for_visible: bool = True
    ) -> Optional[Locator]:
        """
        Convenience method to resolve and return just the Playwright locator.
        Raises exception if not found.
        """
        result = self.resolve(smart_locator, wait_for_visible)
        if not result.success:
            raise ElementNotFoundError(
                f"Could not find element '{smart_locator.name}' "
                f"after {result.total_attempts} attempts. "
                f"Screenshot: {result.screenshot_path}"
            )
        return result.playwright_locator


class ElementNotFoundError(Exception):
    """Raised when an element cannot be found using any of the defined locators."""

    pass


# Factory functions for creating common smart locators
def create_smart_locator(
    name: str,
    primary_xpath: str,
    secondary_xpath: str = "",
    css_selector: str = "",
    text: str = "",
) -> SmartLocator:
    """
    Factory function to quickly create a SmartLocator with common patterns.

    Args:
        name: Human-readable name for the element
        primary_xpath: Primary XPath locator
        secondary_xpath: Alternative XPath locator
        css_selector: CSS selector as fallback
        text: Text-based locator as final fallback
    """
    locator = SmartLocator(name=name)

    if primary_xpath:
        locator.add_xpath(primary_xpath, "Primary XPath")
    if secondary_xpath:
        locator.add_xpath(secondary_xpath, "Secondary XPath")
    if css_selector:
        locator.add_css(css_selector, "CSS Selector")
    if text:
        locator.add_text(text, "Text Content")

    return locator
