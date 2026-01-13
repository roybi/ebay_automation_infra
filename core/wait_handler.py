"""
Provides intelligent wait mechanisms for handling dynamic page loads and element states.
"""

import logging
import time
from enum import Enum
from typing import Callable, TypeVar

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from config.settings import settings

T = TypeVar("T")


class WaitCondition(Enum):
    """Enumeration of wait conditions."""

    VISIBLE = "visible"
    HIDDEN = "hidden"
    ATTACHED = "attached"
    DETACHED = "detached"
    ENABLED = "enabled"
    DISABLED = "disabled"
    EDITABLE = "editable"
    CLICKABLE = "clickable"


class WaitHandler:
    """
    Handles intelligent waiting for various conditions on web elements and pages.
    """

    def __init__(
        self,
        page: Page,
        default_timeout: int = None,
        polling_interval: int = None,
        logger: logging.Logger = None,
    ):
        self.page = page
        self.default_timeout = default_timeout or settings.WAIT.default_timeout
        self.polling_interval = polling_interval or settings.WAIT.polling_interval
        self.logger = logger or logging.getLogger(__name__)

    def wait_for_element(
        self,
        locator: Locator,
        condition: WaitCondition = WaitCondition.VISIBLE,
        timeout: int = None,
    ) -> bool:
        """
        Wait for an element to reach a specific state.


        """
        timeout = timeout or self.default_timeout

        self.logger.debug(
            f"Waiting for element to be {condition.value} (timeout: {timeout}ms)"
        )

        try:
            match condition:
                case WaitCondition.VISIBLE:
                    locator.wait_for(state="visible", timeout=timeout)
                case WaitCondition.HIDDEN:
                    locator.wait_for(state="hidden", timeout=timeout)
                case WaitCondition.ATTACHED:
                    locator.wait_for(state="attached", timeout=timeout)
                case WaitCondition.DETACHED:
                    locator.wait_for(state="detached", timeout=timeout)
                case WaitCondition.ENABLED:
                    locator.wait_for(state="visible", timeout=timeout)
                    self._wait_until(
                        lambda: locator.is_enabled(),
                        timeout=timeout,
                        description="element to be enabled",
                    )
                case WaitCondition.DISABLED:
                    locator.wait_for(state="visible", timeout=timeout)
                    self._wait_until(
                        lambda: locator.is_disabled(),
                        timeout=timeout,
                        description="element to be disabled",
                    )
                case WaitCondition.EDITABLE:
                    locator.wait_for(state="visible", timeout=timeout)
                    self._wait_until(
                        lambda: locator.is_editable(),
                        timeout=timeout,
                        description="element to be editable",
                    )
                case WaitCondition.CLICKABLE:
                    locator.wait_for(state="visible", timeout=timeout)
                    self._wait_until(
                        lambda: locator.is_visible() and locator.is_enabled(),
                        timeout=timeout,
                        description="element to be clickable",
                    )

            self.logger.debug(f"Element is now {condition.value}")
            return True

        except PlaywrightTimeout:
            self.logger.warning(f"Timeout waiting for element to be {condition.value}")
            return False

    def _wait_until(
        self,
        condition: Callable[[], bool],
        timeout: int = None,
        description: str = "condition",
    ) -> bool:
        """
        Wait until a custom condition is met.

        Args:
            condition: Callable that returns True when condition is met
            timeout: Maximum wait time in milliseconds
            description: Description for logging

        Returns:
            True if condition met, raises TimeoutError if not
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        end_time = start_time + (timeout / 1000)

        while time.time() < end_time:
            try:
                if condition():
                    return True
            except Exception:
                pass  # Ignore errors and keep polling

            time.sleep(self.polling_interval / 1000)

        raise PlaywrightTimeout(f"Timeout waiting for {description}")

    def wait_until(
        self,
        condition: Callable[[], bool],
        timeout: int = None,
        description: str = "condition",
        raise_on_timeout: bool = True,
    ) -> bool:
        """
        Public method to wait for a custom condition.

        Args:
            condition: Callable that returns True when condition is met
            timeout: Maximum wait time in milliseconds
            description: Description for logging
            raise_on_timeout: Whether to raise exception on timeout

        Returns:
            True if condition met, False if timeout (when raise_on_timeout=False)
        """
        try:
            return self._wait_until(condition, timeout, description)
        except PlaywrightTimeout:
            if raise_on_timeout:
                raise
            self.logger.warning(f"Timeout waiting for {description}")
            return False

    def wait_for_page_load(self, timeout: int = None) -> None:
        """Wait for page to complete loading."""
        timeout = timeout or settings.WAIT.page_load_timeout
        self.logger.debug(f"Waiting for page load (timeout: {timeout}ms)")
        self.page.wait_for_load_state("load", timeout=timeout)
        self.logger.debug("Page load complete")

    def wait_for_network_idle(self, timeout: int = None) -> None:
        """Wait for network to be idle."""
        timeout = timeout or settings.WAIT.page_load_timeout
        self.logger.debug(f"Waiting for network idle (timeout: {timeout}ms)")
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.logger.debug("Network is idle")

    def wait_for_dom_ready(self, timeout: int = None) -> None:
        """Wait for DOM content to be loaded."""
        timeout = timeout or settings.WAIT.page_load_timeout
        self.logger.debug(f"Waiting for DOM ready (timeout: {timeout}ms)")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.logger.debug("DOM content loaded")

    def wait_for_url(self, url_pattern: str, timeout: int = None) -> bool:
        """
        Wait for URL to match a pattern.

        Args:
            url_pattern: URL pattern (can be regex or glob)
            timeout: Maximum wait time in milliseconds

        Returns:
            True if URL matches, False if timeout
        """
        timeout = timeout or self.default_timeout
        self.logger.debug(f"Waiting for URL to match: {url_pattern}")

        try:
            self.page.wait_for_url(url_pattern, timeout=timeout)
            self.logger.debug(f"URL matched: {self.page.url}")
            return True
        except PlaywrightTimeout:
            self.logger.warning(f"Timeout waiting for URL: {url_pattern}")
            return False

    def wait_for_element_count(
        self,
        locator: Locator,
        expected_count: int,
        timeout: int = None,
        comparison: str = "equals",
    ) -> bool:
        """
        Wait for element count to meet expectation.


            True if count matches expectation
        """
        timeout = timeout or self.default_timeout

        def check_count() -> bool:
            count = locator.count()
            match comparison:
                case "equals":
                    return count == expected_count
                case "greater_than":
                    return count > expected_count
                case "less_than":
                    return count < expected_count
                case "at_least":
                    return count >= expected_count
                case _:
                    return count == expected_count

        return self.wait_until(
            check_count,
            timeout=timeout,
            description=f"element count {comparison} {expected_count}",
            raise_on_timeout=False,
        )

    def wait_for_text(
        self,
        locator: Locator,
        expected_text: str,
        timeout: int = None,
        exact: bool = False,
    ) -> bool:
        """
        Wait for element to contain specific text.

        Args:
            locator: Playwright Locator object
            expected_text: Text to wait for
            timeout: Maximum wait time in milliseconds
            exact: Whether to match exactly or just contain

        Returns:
            True if text found
        """
        timeout = timeout or self.default_timeout

        def check_text() -> bool:
            try:
                actual_text = locator.text_content() or ""
                if exact:
                    return actual_text.strip() == expected_text
                return expected_text in actual_text
            except Exception:
                return False

        return self.wait_until(
            check_text,
            timeout=timeout,
            description=f"text '{expected_text}'",
            raise_on_timeout=False,
        )

    def smart_wait(
        self, locator: Locator, action: str = "click", timeout: int = None
    ) -> None:
        """
        Smart wait that determines the best wait strategy based on action.

        Args:
            locator: Playwright Locator object
            action: The action to be performed ("click", "fill", "select", etc.)
            timeout: Maximum wait time in milliseconds
        """
        timeout = timeout or self.default_timeout

        # First wait for element to be visible
        self.wait_for_element(locator, WaitCondition.VISIBLE, timeout)

        # Then wait for specific state based on action
        match action.lower():
            case "click" | "check" | "uncheck":
                self.wait_for_element(locator, WaitCondition.CLICKABLE, timeout)
            case "fill" | "type" | "clear":
                self.wait_for_element(locator, WaitCondition.EDITABLE, timeout)
            case "select":
                self.wait_for_element(locator, WaitCondition.ENABLED, timeout)
            case _:
                pass  # Visible is enough for other actions


def explicit_wait(
    page: Page,
    condition: Callable[[], bool],
    timeout: int = None,
    polling: int = None,
    message: str = "condition",
) -> bool:
    """
    Standalone function for explicit waits.

    Args:
        page: Playwright Page object
        condition: Callable returning True when condition is met
        timeout: Maximum wait time in milliseconds
        polling: Polling interval in milliseconds
        message: Description for error messages

    Returns:
        True if condition met
    """
    handler = WaitHandler(page, default_timeout=timeout, polling_interval=polling)
    return handler.wait_until(condition, timeout, message)
