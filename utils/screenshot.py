"""
Provides screenshot capture and management functionality.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import Locator, Page

from config.settings import settings


class ScreenshotManager:
    """
    Manages screenshot capture, naming, and organization.
    """

    def __init__(self, output_dir: Path = None, logger: logging.Logger = None):
        self.output_dir = output_dir or settings.SCREENSHOTS_DIR
        self.logger = logger or logging.getLogger(__name__)
        self._counter = 0

        # Ensure directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(
        self, name: str = None, prefix: str = "", suffix: str = ""
    ) -> str:
        """Generate unique filename for screenshot."""
        self._counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        parts = []
        if prefix:
            parts.append(prefix)
        if name:
            parts.append(name)
        parts.append(timestamp)
        parts.append(str(self._counter))
        if suffix:
            parts.append(suffix)

        return "_".join(parts) + ".png"

    def capture_page(
        self,
        page: Page,
        name: str = None,
        full_page: bool = False,
        prefix: str = "",
        suffix: str = "",
    ) -> str:
        """
        Capture screenshot of the entire page.

        Returns:
            Path to saved screenshot
        """
        filename = self._generate_filename(name, prefix, suffix)
        filepath = self.output_dir / filename

        page.screenshot(path=str(filepath), full_page=full_page)
        self.logger.info(f"Page screenshot saved: {filepath}")

        return str(filepath)

    def capture_element(
        self, element: Locator, name: str = None, prefix: str = "", suffix: str = ""
    ) -> str:
        """
        Capture screenshot of a specific element.

        Returns:
            Path to saved screenshot
        """
        filename = self._generate_filename(name or "element", prefix, suffix)
        filepath = self.output_dir / filename

        element.screenshot(path=str(filepath))
        self.logger.info(f"Element screenshot saved: {filepath}")

        return str(filepath)

    def capture_on_failure(
        self, page: Page, test_name: str, error: Optional[Exception] = None
    ) -> str:
        """

        Path to saved screenshot
        """
        # Sanitize test name for filename
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in test_name)

        filepath = self.capture_page(
            page, name=safe_name, prefix="FAILURE", full_page=True
        )

        if error:
            self.logger.error(f"Test failed: {test_name} - {str(error)}")

        return filepath

    def capture_step(self, page: Page, step_name: str, step_number: int = None) -> str:
        """

        Args:
            page: Playwright Page object
            step_name: Name of the step
            step_number: Optional step number

        """
        prefix = f"step_{step_number}" if step_number else "step"
        return self.capture_page(page, name=step_name, prefix=prefix)

    def get_screenshots_dir(self) -> Path:
        """Get the screenshots directory path."""
        return self.output_dir

    def cleanup_old_screenshots(self, max_age_days: int = 7) -> int:
        """
        Number of deleted files
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        for filepath in self.output_dir.glob("*.png"):
            if filepath.stat().st_mtime < cutoff.timestamp():
                filepath.unlink()
                deleted_count += 1

        self.logger.info(f"Cleaned up {deleted_count} old screenshots")
        return deleted_count


# Global screenshot manager
_screenshot_manager: Optional[ScreenshotManager] = None


def get_screenshot_manager() -> ScreenshotManager:
    """Get or create global screenshot manager instance."""
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager


def capture_screenshot(
    page: Page,
    name: str = None,
    full_page: bool = False,
) -> str:
    return get_screenshot_manager().capture_page(page, name, full_page)


def capture_failure_screenshot(
    page: Page, test_name: str, error: Exception = None
) -> str:
    return get_screenshot_manager().capture_on_failure(page, test_name, error)
