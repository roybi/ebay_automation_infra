import logging
from datetime import datetime
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from core.browser_factory import BrowserFactory, BrowserSession
from utils.logger import init_logging, setup_logger
from utils.screenshot import capture_failure_screenshot


def pytest_configure(config):
    """Configure pytest environment."""
    # Initialize logging
    init_logging()

    # Ensure directories exist
    settings.ensure_directories()

    # Setup unique report directory for this run
    if settings.REPORT.generate_unique_report_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        allure_dir = settings.REPORTS_DIR / f"allure-results_{timestamp}"
        allure_dir.mkdir(parents=True, exist_ok=True)
        config.option.allure_report_dir = str(allure_dir)

    # Register custom markers
    config.addinivalue_line("markers", "browser(name): specify browser for test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")


def pytest_addoption(parser):
    """Add custom command line options."""
    # Note: --browser is provided by pytest-playwright, so we don't add it here
    # parser.addoption("--browser", ...) - conflicts with pytest-playwright

    # Add custom slow-mo option if needed
    try:
        parser.addoption(
            "--slow-mo",
            action="store",
            default=0,
            type=int,
            help="Slow down operations by specified milliseconds",
        )
    except ValueError:
        # Option already exists
        pass


@pytest.fixture(scope="session")
def browser_factory() -> Generator[BrowserFactory, None, None]:
    """
    Creates a single factory instance for the entire test session.
    """
    factory = BrowserFactory()
    yield factory
    factory.shutdown()


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """Get base URL for tests."""
    return getattr(request.config.option, "base_url", settings.BASE_URL)


@pytest.fixture
def browser_name(request) -> str:
    """Get browser name from command line or marker."""
    # Check for browser marker first
    marker = request.node.get_closest_marker("browser")
    if marker:
        return marker.args[0]
    # Use pytest-playwright's browser_name or default to chromium
    return getattr(request.config.option, "browser_name", "chromium")


@pytest.fixture
def headless(request) -> bool:
    """Determine if browser should run headless."""
    # Check pytest-playwright's headed option
    headed = getattr(request.config.option, "headed", False)
    if headed:
        return False
    return True  # Default to headless


@pytest.fixture
def browser_session(
    browser_factory: BrowserFactory, browser_name: str, headless: bool, request
) -> Generator[BrowserSession, None, None]:
    """
    Function-scoped browser session.
    Each test gets an isolated browser session.
    """
    slow_mo = getattr(request.config.option, "slow_mo", 0)

    session = browser_factory.create_session(
        browser_name=browser_name,
        headless=headless,
        extra_args=[] if slow_mo == 0 else None,
    )

    # Update slow_mo if needed
    if slow_mo > 0:
        session.context.set_default_timeout(settings.WAIT.default_timeout)

    yield session

    browser_factory.close_session(session.session_id)


@pytest.fixture
def page(browser_session: BrowserSession) -> Page:
    """
    Get the page from browser session.
    Most tests will use this fixture directly.
    """
    return browser_session.page


@pytest.fixture
def context(browser_session: BrowserSession) -> BrowserContext:
    """Get the browser context from session."""
    return browser_session.context


@pytest.fixture
def browser(browser_session: BrowserSession) -> Browser:
    """Get the browser from session."""
    return browser_session.browser


@pytest.fixture
def logger(request) -> logging.Logger:
    """Get a logger for the current test."""
    return setup_logger(request.node.name)


@pytest.fixture
def screenshot_on_failure(page: Page, request):
    """
    Fixture to capture screenshot on test failure.
    """
    yield

    # Capture screenshot if test failed
    if request.node.rep_call and request.node.rep_call.failed:
        capture_failure_screenshot(page, request.node.name)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result for use in fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_collection_modifyitems(config, items):
    """Add markers for parallel execution."""
    for item in items:
        # Add browser markers if not present
        if not any(marker.name == "browser" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.browser("chromium"))
