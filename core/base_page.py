"""
Base Page Class
Foundation for Page Object Model (POM) implementation.
Provides common functionality for all page objects.
"""

import logging
from abc import ABC
from datetime import datetime
from typing import Any, List, Optional

from playwright.sync_api import Locator, Page, Response

from config.settings import settings
from core.retry_handler import RetryHandler
from core.smart_locator import (
    LocatorResolutionResult,
    SmartLocator,
    SmartLocatorResolver,
)
from core.wait_handler import WaitCondition, WaitHandler


class BasePage(ABC):
    """
    Base class for all page objects.
    Implements common functionality and smart locator integration.
    """

    # Override in child classes
    PAGE_URL: str = ""
    PAGE_NAME: str = "BasePage"

    def __init__(self, page: Page, logger: logging.Logger = None):
        self.page = page
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # Initialize handlers
        self._locator_resolver = SmartLocatorResolver(page, self.logger)
        self._wait_handler = WaitHandler(page, logger=self.logger)
        self._retry_handler = RetryHandler(logger=self.logger)

        # Screenshot counter for this page instance
        self._screenshot_counter = 0

        self.logger.debug(f"Initialized {self.PAGE_NAME}")

    # ==================== Navigation ====================

    def navigate(self, url: str = None) -> Optional[Response]:
        """

        Args:
            url: URL to navigate to (uses PAGE_URL if not provided)
        """
        target_url = url or self.PAGE_URL
        if not target_url:
            raise ValueError(f"No URL provided for {self.PAGE_NAME}")

        self.logger.info(f"Navigating to: {target_url}")
        response = self.page.goto(target_url)
        self._wait_handler.wait_for_page_load()
        return response

    def navigate_to_base_url(self) -> Optional[Response]:
        """Navigate to the base URL."""
        return self.navigate(settings.BASE_URL)

    def refresh(self) -> None:
        """Refresh the current page."""
        self.logger.debug(f"Refreshing {self.PAGE_NAME}")
        self.page.reload()
        self._wait_handler.wait_for_page_load()

    def go_back(self) -> None:
        """Navigate back in browser history."""
        self.logger.debug("Navigating back")
        self.page.go_back()
        self._wait_handler.wait_for_page_load()

    def go_forward(self) -> None:
        """Navigate forward in browser history."""
        self.logger.debug("Navigating forward")
        self.page.go_forward()
        self._wait_handler.wait_for_page_load()

    # ==================== Smart Locator Methods ====================

    def find_element(
        self, smart_locator: SmartLocator, wait_visible: bool = True
    ) -> Locator:
        """
        Find element using smart locator with automatic fallback.

            Playwright Locator

        """
        return self._locator_resolver.find_element(smart_locator, wait_visible)

    def find_element_safe(
        self, smart_locator: SmartLocator, wait_visible: bool = True
    ) -> Optional[Locator]:
        """
        Find element without raising exception.

        Returns:
            Playwright Locator or None if not found
        """
        result = self._locator_resolver.resolve(smart_locator, wait_visible)
        return result.playwright_locator if result.success else None

    def resolve_locator(
        self, smart_locator: SmartLocator, wait_visible: bool = True
    ) -> LocatorResolutionResult:
        """

        Returns:
            LocatorResolutionResult with all attempt details
        """
        return self._locator_resolver.resolve(smart_locator, wait_visible)

    def is_element_present(
        self, smart_locator: SmartLocator, timeout: int = 5000
    ) -> bool:
        """
        Check if element exists on page.

        Args:
            smart_locator: SmartLocator to check
            timeout: How long to wait before returning False

        Returns:
            True if element exists
        """
        original_timeout = smart_locator.timeout
        smart_locator.timeout = timeout

        result = self._locator_resolver.resolve(smart_locator, wait_for_visible=False)

        smart_locator.timeout = original_timeout
        return result.success

    def is_element_visible(
        self, smart_locator: SmartLocator, timeout: int = 5000
    ) -> bool:
        """
        Check if element is visible on page.

        Returns:
            True if element is visible
        """
        original_timeout = smart_locator.timeout
        smart_locator.timeout = timeout

        result = self._locator_resolver.resolve(smart_locator, wait_for_visible=True)

        smart_locator.timeout = original_timeout
        return result.success

    # ==================== Element Interactions ====================

    def click(
        self, smart_locator: SmartLocator, force: bool = False, timeout: int = None
    ) -> None:
        """
        Click on an element.

        Args:
            smart_locator: SmartLocator for target element
            force: Force click even if element is not actionable
            timeout: Custom timeout
        """
        self.logger.debug(f"Clicking on: {smart_locator.name}")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "click", timeout)
        element.click(force=force, timeout=timeout)

    def double_click(self, smart_locator: SmartLocator, timeout: int = None) -> None:
        """Double-click on an element."""
        self.logger.debug(f"Double-clicking on: {smart_locator.name}")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "click", timeout)
        element.dblclick(timeout=timeout)

    def right_click(self, smart_locator: SmartLocator, timeout: int = None) -> None:
        """Right-click on an element."""
        self.logger.debug(f"Right-clicking on: {smart_locator.name}")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "click", timeout)
        element.click(button="right", timeout=timeout)

    def fill(
        self,
        smart_locator: SmartLocator,
        text: str,
        clear_first: bool = True,
        timeout: int = None,
    ) -> None:
        """
        Fill text into an input element.

        Args:
            smart_locator: SmartLocator for input element
            text: Text to enter
            clear_first: Clear existing text first
            timeout: Custom timeout
        """
        self.logger.debug(f"Filling '{smart_locator.name}' with text")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "fill", timeout)

        if clear_first:
            element.clear()
        element.fill(text, timeout=timeout)

    def type_text(
        self,
        smart_locator: SmartLocator,
        text: str,
        delay: int = 50,
        timeout: int = None,
    ) -> None:
        """
        Type text character by character (simulates real typing).

        Args:
            smart_locator: SmartLocator for input element
            text: Text to type
            delay: Delay between keystrokes in milliseconds
            timeout: Custom timeout
        """
        self.logger.debug(f"Typing in '{smart_locator.name}'")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "fill", timeout)
        element.type(text, delay=delay, timeout=timeout)

    def clear(self, smart_locator: SmartLocator) -> None:
        """Clear text from an input element."""
        self.logger.debug(f"Clearing: {smart_locator.name}")
        element = self.find_element(smart_locator)
        element.clear()

    def select_option(
        self,
        smart_locator: SmartLocator,
        value: str = None,
        label: str = None,
        index: int = None,
        timeout: int = None,
    ) -> List[str]:
        """
        Select option from a dropdown.

        Args:
            smart_locator: SmartLocator for select element
            value: Option value attribute
            label: Option visible text
            index: Option index (0-based)
            timeout: Custom timeout

        Returns:
            List of selected option values
        """
        self.logger.debug(f"Selecting option in: {smart_locator.name}")
        element = self.find_element(smart_locator)
        self._wait_handler.smart_wait(element, "select", timeout)

        if value is not None:
            return element.select_option(value=value, timeout=timeout)
        elif label is not None:
            return element.select_option(label=label, timeout=timeout)
        elif index is not None:
            return element.select_option(index=index, timeout=timeout)
        else:
            raise ValueError("Must provide value, label, or index")

    def check(self, smart_locator: SmartLocator, timeout: int = None) -> None:
        """Check a checkbox or radio button."""
        self.logger.debug(f"Checking: {smart_locator.name}")
        element = self.find_element(smart_locator)
        element.check(timeout=timeout)

    def uncheck(self, smart_locator: SmartLocator, timeout: int = None) -> None:
        """Uncheck a checkbox."""
        self.logger.debug(f"Unchecking: {smart_locator.name}")
        element = self.find_element(smart_locator)
        element.uncheck(timeout=timeout)

    def hover(self, smart_locator: SmartLocator, timeout: int = None) -> None:
        """Hover over an element."""
        self.logger.debug(f"Hovering over: {smart_locator.name}")
        element = self.find_element(smart_locator)
        element.hover(timeout=timeout)

    # ==================== Element Information ====================

    def get_text(self, smart_locator: SmartLocator) -> str:
        """Get text content of an element."""
        element = self.find_element(smart_locator)
        return element.text_content() or ""

    def get_inner_text(self, smart_locator: SmartLocator) -> str:
        """Get inner text of an element."""
        element = self.find_element(smart_locator)
        return element.inner_text()

    def get_attribute(
        self, smart_locator: SmartLocator, attribute: str
    ) -> Optional[str]:
        """Get attribute value of an element."""
        element = self.find_element(smart_locator)
        return element.get_attribute(attribute)

    def get_input_value(self, smart_locator: SmartLocator) -> str:
        """Get value of an input element."""
        element = self.find_element(smart_locator)
        return element.input_value()

    def get_element_count(self, smart_locator: SmartLocator) -> int:
        """Get count of matching elements."""
        locator = self.find_element_safe(smart_locator, wait_visible=False)
        return locator.count() if locator else 0

    # ==================== Wait Methods ====================

    def wait_for_element(
        self,
        smart_locator: SmartLocator,
        condition: WaitCondition = WaitCondition.VISIBLE,
        timeout: int = None,
    ) -> bool:
        """Wait for element to reach a specific state."""
        element = self.find_element_safe(smart_locator, wait_visible=False)
        if not element:
            return False
        return self._wait_handler.wait_for_element(element, condition, timeout)

    def wait_for_page_load(self, timeout: int = None) -> None:
        """Wait for page to complete loading."""
        self._wait_handler.wait_for_page_load(timeout)

    def wait_for_network_idle(self, timeout: int = None) -> None:
        """Wait for network to be idle."""
        self._wait_handler.wait_for_network_idle(timeout)

    def wait_for_url(self, url_pattern: str, timeout: int = None) -> bool:
        """Wait for URL to match pattern."""
        return self._wait_handler.wait_for_url(url_pattern, timeout)

    # ==================== Screenshot & Logging ====================

    def capture_screenshot(self, name: str = None, full_page: bool = False) -> str:
        """
        Path to saved screenshot
        """
        settings.ensure_directories()
        self._screenshot_counter += 1

        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{self.PAGE_NAME}_{timestamp}_{self._screenshot_counter}"

        filepath = settings.SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=str(filepath), full_page=full_page)

        self.logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    def capture_element_screenshot(
        self, smart_locator: SmartLocator, name: str = None
    ) -> str:
        """Capture screenshot of a specific element."""
        settings.ensure_directories()
        self._screenshot_counter += 1

        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{self.PAGE_NAME}_{smart_locator.name}_{timestamp}"

        filepath = settings.SCREENSHOTS_DIR / f"{name}.png"
        element = self.find_element(smart_locator)
        element.screenshot(path=str(filepath))

        self.logger.info(f"Element screenshot saved: {filepath}")
        return str(filepath)

    def log_action(self, action: str, details: str = "") -> None:
        """Log an action with optional details."""
        message = f"[{self.PAGE_NAME}] {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    # ==================== Page Information ====================

    @property
    def current_url(self) -> str:
        """Get current page URL."""
        return self.page.url

    @property
    def title(self) -> str:
        """Get page title."""
        return self.page.title()

    def is_page_loaded(self) -> bool:
        """
        Check if current page matches this page object.
        Override in child classes for specific validation.
        """
        if self.PAGE_URL:
            return self.PAGE_URL in self.current_url
        return True

    # ==================== JavaScript Execution ====================

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript on the page."""
        return self.page.evaluate(script, *args)

    def scroll_to_element(self, smart_locator: SmartLocator) -> None:
        """Scroll element into view."""
        element = self.find_element(smart_locator)
        element.scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        """Scroll to top of page."""
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
