"""
Manages browser instances, contexts, and pages with support for parallel execution.
Ensures session isolation and proper resource cleanup.
"""

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Generator, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    sync_playwright,
)

from config.settings import BrowserConfig, settings


@dataclass
class BrowserSession:
    """Represents an isolated browser session."""

    session_id: str
    browser: Browser
    context: BrowserContext
    page: Page
    browser_config: BrowserConfig
    created_at: datetime = field(default_factory=datetime.now)

    def close(self) -> None:
        """Close the session and release resources."""
        try:
            if self.page and not self.page.is_closed():
                self.page.close()
        except Exception:
            pass

        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        try:
            if self.browser and self.browser.is_connected():
                self.browser.close()
        except Exception:
            pass


class BrowserFactory:
    """
    Factory for creating and managing browser instances.
    Supports multiple browsers, session isolation, and parallel execution.
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self._playwright: Optional[Playwright] = None
        self._sessions: Dict[str, BrowserSession] = {}
        self._session_counter = 0

    def _get_playwright(self) -> Playwright:
        """Get or create Playwright instance."""
        if self._playwright is None:
            settings.ensure_directories()
            logs_dir = settings.BASE_DIR / "logs"
            logs_dir.mkdir(exist_ok=True)

            os.environ["DEBUG"] = "pw:api"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            playwright_log_file = logs_dir / f"playwright_{timestamp}.log"

            log_handler = logging.FileHandler(playwright_log_file, mode='a', encoding='utf-8')
            log_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            log_handler.setFormatter(formatter)

            pw_logger = logging.getLogger("playwright")
            pw_logger.setLevel(logging.DEBUG)
            pw_logger.addHandler(log_handler)

            self.logger.info(f"Playwright logs will be written to: {playwright_log_file}")
            self._playwright = sync_playwright().start()
        return self._playwright

    def _get_browser_type(self, browser_name: str) -> BrowserType:
        """Get Playwright browser type by name."""
        playwright = self._get_playwright()
        browser_map = {
            "chromium": playwright.chromium,
            "chrome": playwright.chromium,
            "firefox": playwright.firefox,
            "webkit": playwright.webkit,
            "safari": playwright.webkit,
            "edge": playwright.chromium,
        }
        return browser_map.get(browser_name.lower(), playwright.chromium)

    def _generate_session_id(self, browser_name: str) -> str:
        """Generate unique session ID."""
        self._session_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{browser_name}_{timestamp}_{self._session_counter}"

    def create_session(
        self,
        browser_name: str = "chromium",
        headless: bool = None,
        viewport: Dict[str, int] = None,
        extra_args: list = None,
        storage_state: Optional[str] = None,
        record_video: bool = False,
        record_har: bool = False,
        **context_options,
    ) -> BrowserSession:
        """
        Create a new isolated browser session.

        Args:
            browser_name: Name of browser (chromium, firefox, webkit)
            headless: Run browser in headless mode
            viewport: Custom viewport dimensions
            extra_args: Additional browser launch arguments
            storage_state: Path to storage state file
            record_video: Whether to record video
            record_har: Whether to record HAR file
            **context_options: Additional context options

        Returns:
            BrowserSession with isolated browser, context, and page
        """
        # Get browser configuration
        config = settings.get_browser_config(browser_name)

        # Override with provided options
        if headless is not None:
            config.headless = headless

        browser_type = self._get_browser_type(browser_name)

        # Prepare launch options
        launch_options = {
            "headless": config.headless,
            "slow_mo": config.slow_mo,
        }

        # Add channel for Chrome versions (chrome, chrome-beta, chrome-dev, msedge)
        if config.channel:
            launch_options["channel"] = config.channel

        # Add custom executable path if specified
        if config.executable_path:
            launch_options["executable_path"] = config.executable_path

        # Add browser arguments
        args = config.args.copy()
        if extra_args:
            args.extend(extra_args)
        if args:
            launch_options["args"] = args

        # Launch browser
        self.logger.info(
            f"Launching {browser_name} browser (headless={config.headless})"
        )
        browser = browser_type.launch(**launch_options)

        # Prepare context options
        ctx_options = {
            "viewport": viewport
            or {"width": config.viewport_width, "height": config.viewport_height},
            **context_options,
        }

        # Add storage state if provided
        if storage_state:
            ctx_options["storage_state"] = storage_state

        # Setup video recording
        if record_video:
            settings.ensure_directories()
            video_dir = settings.REPORTS_DIR / "videos"
            video_dir.mkdir(exist_ok=True)
            ctx_options["record_video_dir"] = str(video_dir)

        # Setup HAR recording
        if record_har:
            settings.ensure_directories()
            temp_session_id = self._generate_session_id(browser_name)
            har_path = settings.REPORTS_DIR / "har" / f"{temp_session_id}.har"
            har_path.parent.mkdir(exist_ok=True)
            ctx_options["record_har_path"] = str(har_path)

        # Create context
        context = browser.new_context(**ctx_options)
        context.set_default_timeout(config.timeout)

        # Create page
        page = context.new_page()

        # Setup browser logging
        logs_dir = settings.BASE_DIR / "logs"
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = self._generate_session_id(browser_name)
        console_log_file = logs_dir / f"browser_console_{session_id}_{timestamp}.log"
        network_log_file = logs_dir / f"browser_network_{session_id}_{timestamp}.log"

        def log_console_message(msg):
            try:
                with open(console_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{msg.type.upper()}] {msg.text}\n")
                    if msg.location:
                        f.write(f"  Location: {msg.location.get('url', 'unknown')}:{msg.location.get('lineNumber', '?')}\n")
            except Exception as e:
                self.logger.warning(f"Failed to write console log: {e}")

        def log_page_error(error):
            try:
                with open(console_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [PAGE ERROR] {error}\n")
            except Exception as e:
                self.logger.warning(f"Failed to write page error: {e}")

        def log_request(request):
            try:
                with open(network_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [REQUEST] {request.method} {request.url}\n")
            except Exception as e:
                self.logger.warning(f"Failed to write request log: {e}")

        def log_response(response):
            try:
                with open(network_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [RESPONSE] {response.status} {response.url}\n")
            except Exception as e:
                self.logger.warning(f"Failed to write response log: {e}")

        def log_request_failed(request):
            try:
                with open(network_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [REQUEST FAILED] {request.url}\n")
            except Exception as e:
                self.logger.warning(f"Failed to write request failed log: {e}")

        page.on("console", log_console_message)
        page.on("pageerror", log_page_error)
        page.on("request", log_request)
        page.on("response", log_response)
        page.on("requestfailed", log_request_failed)

        self.logger.info(f"Browser console logs: {console_log_file}")
        self.logger.info(f"Browser network logs: {network_log_file}")

        # Create session object
        session = BrowserSession(
            session_id=session_id,
            browser=browser,
            context=context,
            page=page,
            browser_config=config,
        )

        # Track session
        self._sessions[session_id] = session

        self.logger.info(f"Created browser session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)

    def close_session(self, session_id: str) -> None:
        """Close and cleanup a specific session."""
        session = self._sessions.pop(session_id, None)
        if session:
            self.logger.info(f"Closing browser session: {session_id}")
            session.close()

    def close_all_sessions(self) -> None:
        """Close all active sessions."""
        self.logger.info(f"Closing all {len(self._sessions)} browser sessions")
        for session_id in list(self._sessions.keys()):
            self.close_session(session_id)

    def shutdown(self) -> None:
        """Shutdown factory and release all resources."""
        self.close_all_sessions()
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self.logger.info("Browser factory shutdown complete")

    @contextmanager
    def session(
        self, browser_name: str = "chromium", **kwargs
    ) -> Generator[BrowserSession, None, None]:
        session = self.create_session(browser_name, **kwargs)
        try:
            yield session
        finally:
            self.close_session(session.session_id)

    def create_parallel_sessions(
        self, browsers: list = None, **kwargs
    ) -> Dict[str, BrowserSession]:
        if browsers is None:
            browsers = list(settings.BROWSER_MATRIX.keys())

        sessions = {}
        for browser_name in browsers:
            try:
                session = self.create_session(browser_name, **kwargs)
                sessions[browser_name] = session
            except Exception as e:
                self.logger.error(f"Failed to create {browser_name} session: {e}")

        return sessions


# Global factory instance (can be used or replaced)
_global_factory: Optional[BrowserFactory] = None


def get_browser_factory() -> BrowserFactory:
    """Get or create global browser factory instance."""
    global _global_factory
    if _global_factory is None:
        _global_factory = BrowserFactory()
    return _global_factory


def reset_browser_factory() -> None:
    """Reset the global browser factory."""
    global _global_factory
    if _global_factory:
        _global_factory.shutdown()
        _global_factory = None


@contextmanager
def browser_session(
    browser_name: str = "chromium", **kwargs
) -> Generator[BrowserSession, None, None]:
    factory = get_browser_factory()
    with factory.session(browser_name, **kwargs) as session:
        yield session
