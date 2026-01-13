import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BrowserConfig:
    """Configuration for browser settings."""

    name: str
    headless: bool = False
    slow_mo: int = 0
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000  # in milliseconds
    args: List[str] = field(default_factory=list)  # Additional browser launch
    channel: Optional[str] = None  # Chrome channel: 'chrome', 'chrome-beta', 'msedge', etc.
    executable_path: Optional[str] = None  # Custom browser executable path


@dataclass
class RetryConfig:
    """Configuration for retry and backoff configuration."""

    max_retries: int = 3
    initial_delay: float = 1.0  # in seconds
    max_delay: float = 10.0  # in seconds
    backoff_multiplier: float = 2.0
    delay_between_retries: int = 1000  # in milliseconds


@dataclass
class WaitConfig:
    """Configuration for wait times."""

    default_timeout: int = 30000  # in milliseconds
    element_load_timeout: int = 15000  # in milliseconds
    page_load_timeout: int = 60000  # in milliseconds
    polling_interval: int = 500  # in milliseconds


@dataclass
class LocatorConfig:
    """Smart locator configuration."""

    max_locator_retries: int = 3
    locator_timeout: int = 5000  # in milliseconds
    screenshot_on_failure: bool = True


@dataclass
class ReportConfig:
    """Reporting configuration."""

    enable_allure: bool = True
    allure_results_dir: Path = Path("reports/allure-results")
    html_report_path: Path = Path("reports/html-report")
    screenshot_on_failure: bool = True
    generate_unique_report_dir: bool = True


@dataclass
class ParallelConfig:
    """Parallel execution configuration."""

    enable_parallel: bool = True
    max_workers: int = 4
    session_isolation: bool = True


@dataclass
class FrameworkSettings:
    """Main framework settings."""

    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = Path(__file__).parent.parent / "data"
    REPORTS_DIR: Path = Path(__file__).parent.parent / "reports"
    SCREENSHOTS_DIR: Path = Path(__file__).parent.parent / "reports" / "screenshots"

    # Browser configurations for matrix testing
    # Supports multiple Chrome versions via 'channel' parameter
    BROWSER_MATRIX: Dict[str, BrowserConfig] = field(default_factory=lambda: {
        # Chromium (Playwright's bundled version)
        "chromium": BrowserConfig(
            name="chromium",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        ),
        # Chrome Stable (system-installed)
        "chrome": BrowserConfig(
            name="chromium",
            channel="chrome",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        ),
        # Chrome Beta (requires Chrome Beta installed)
        "chrome-beta": BrowserConfig(
            name="chromium",
            channel="chrome-beta",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        ),
        # Chrome Dev (requires Chrome Dev installed)
        "chrome-dev": BrowserConfig(
            name="chromium",
            channel="chrome-dev",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        ),
        # Microsoft Edge (Chromium-based)
        "msedge": BrowserConfig(
            name="chromium",
            channel="msedge",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        ),
        # Firefox
        "firefox": BrowserConfig(
            name="firefox",
            headless=True
        ),
        # WebKit (Safari engine)
        "webkit": BrowserConfig(
            name="webkit",
            headless=True
        ),
    })

    # Default configurations
    RETRY_CONFIG: RetryConfig = field(default_factory=RetryConfig)
    WAIT_CONFIG: WaitConfig = field(default_factory=WaitConfig)
    LOCATOR: LocatorConfig = field(default_factory=LocatorConfig)
    REPORT: ReportConfig = field(default_factory=ReportConfig)
    PARALLEL: ParallelConfig = field(default_factory=ParallelConfig)

    # url
    BASE_URL: str = "https://www.ebay.com"

    # lOGGING
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_PATH: Path = BASE_DIR / "logs" / "framework.log"
    LOG_FILE_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB

    # Aliasesfor backwards compatibility
    @property
    def WAIT(self) -> WaitConfig:
        """Alias for WAIT_CONFIG."""
        return self.WAIT_CONFIG

    @property
    def RETRY(self) -> RetryConfig:
        """Alias for RETRY_CONFIG."""
        return self.RETRY_CONFIG

    def get_browser_config(self, browser_name: str) -> Optional[BrowserConfig]:
        """Get browser configuration by name."""
        matrix = self.BROWSER_MATRIX if isinstance(self.BROWSER_MATRIX, dict) else {}
        return matrix.get(browser_name.lower(), matrix.get("chromium"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure that necessary directories exist."""
        for directory in [cls.DATA_DIR, cls.REPORTS_DIR, cls.SCREENSHOTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = FrameworkSettings()
