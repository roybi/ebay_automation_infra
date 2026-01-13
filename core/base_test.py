"""
Foundation for all test classes with common functionality.
"""

from datetime import datetime

import pytest

from core.browser_factory import BrowserSession
from utils.allure_helper import AllureHelper
from utils.screenshot import capture_failure_screenshot


class BaseTest:
    """
    Base class for all test classes.
    Provides common setup, teardown, and utility methods.
    """

    # Override in child classes
    TEST_SUITE_NAME: str = "BaseTests"

    @pytest.fixture(autouse=True)
    def setup_test(self, browser_session: BrowserSession, request, logger):
        """
        Setup for each test.
        Runs automatically before each test method.
        """
        self.session = browser_session
        self.page = browser_session.page
        self.context = browser_session.context
        self.browser = browser_session.browser
        self.logger = logger
        self.test_name = request.node.name
        self._step_counter = 0

        self.logger.info(f"Starting test: {self.test_name}")
        self.logger.info(f"Browser: {browser_session.browser_config.name}")

        yield

        # Teardown
        self.logger.info(f"Finished test: {self.test_name}")

    @pytest.fixture(autouse=True)
    def capture_screenshot_on_failure(self, request):
        """Capture screenshot if test fails."""
        yield

        if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
            if hasattr(self, "page") and self.page:
                screenshot_path = capture_failure_screenshot(self.page, self.test_name)
                self.logger.error(f"Test failed. Screenshot: {screenshot_path}")
                AllureHelper.attach_screenshot(screenshot_path, "Failure Screenshot")

    # ==================== Step Logging ====================

    def step(self, description: str):
        """
        Create a test step with logging and Allure integration.

        Usage:
            with self.step("Login to application"):
                self.login_page.login(user, password)
        """
        self._step_counter += 1
        self.logger.info(f"Step {self._step_counter}: {description}")
        return AllureHelper.step(f"Step {self._step_counter}: {description}")

    def log_step(self, description: str) -> None:
        """Log a test step without creating Allure step."""
        self._step_counter += 1
        self.logger.info(f"Step {self._step_counter}: {description}")

    # ==================== Screenshot Methods ====================

    def capture_screenshot(self, name: str = None) -> str:
        """Capture screenshot and attach to Allure report."""
        if not name:
            name = f"{self.test_name}_{datetime.now().strftime('%H%M%S')}"

        screenshot_path = self.page.screenshot(path=f"screenshots/{name}.png")

        AllureHelper.attach_screenshot(str(screenshot_path), name)
        return str(screenshot_path)

    # ==================== Assertion Helpers ====================

    def assert_url_contains(self, expected: str, message: str = None) -> None:
        """Assert current URL contains expected string."""
        actual_url = self.page.url
        assert expected in actual_url, (
            message or f"Expected URL to contain '{expected}', got '{actual_url}'"
        )

    def assert_title_contains(self, expected: str, message: str = None) -> None:
        """Assert page title contains expected string."""
        actual_title = self.page.title()
        assert expected in actual_title, (
            message or f"Expected title to contain '{expected}', got '{actual_title}'"
        )

    def assert_element_visible(
        self, selector: str, message: str = None, timeout: int = 5000
    ) -> None:
        """Assert element is visible on page."""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
        except Exception:
            self.capture_screenshot("element_not_visible")
            raise AssertionError(message or f"Element '{selector}' is not visible")

    def assert_element_not_visible(
        self, selector: str, message: str = None, timeout: int = 5000
    ) -> None:
        """Assert element is not visible on page."""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
        except Exception:
            self.capture_screenshot("element_still_visible")
            raise AssertionError(message or f"Element '{selector}' is still visible")

    def assert_text_present(
        self, text: str, message: str = None, timeout: int = 5000
    ) -> None:
        """Assert text is present on page."""
        try:
            self.page.get_by_text(text).wait_for(state="visible", timeout=timeout)
        except Exception:
            self.capture_screenshot("text_not_found")
            raise AssertionError(message or f"Text '{text}' not found on page")

    # ==================== Navigation Helpers ====================

    def navigate_to(self, url: str) -> None:
        """Navigate to URL with logging."""
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("load")

    def refresh_page(self) -> None:
        """Refresh current page."""
        self.logger.debug("Refreshing page")
        self.page.reload()
        self.page.wait_for_load_state("load")

    # ==================== Wait Helpers ====================

    def wait_for_page_load(self, timeout: int = None) -> None:
        """Wait for page to complete loading."""
        self.page.wait_for_load_state("load", timeout=timeout)

    def wait_for_network_idle(self, timeout: int = None) -> None:
        """Wait for network to be idle."""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
