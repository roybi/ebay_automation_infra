"""
eBay Automation Infrastructure
A robust test automation framework built with Python and Playwright.

"""

__version__ = "1.0.0"
__author__ = "Roy Bichovsky"

from config.settings import settings, FrameworkSettings
from core.base_page import BasePage
from core.base_test import BaseTest
from core.smart_locator import (
    SmartLocator,
    LocatorType,
    create_smart_locator,
    ElementNotFoundError,
)
from core.browser_factory import (
    BrowserFactory,
    BrowserSession,
    browser_session,
)
from core.retry_handler import retry, RetryHandler
from core.wait_handler import WaitHandler, WaitCondition


__all__ = [
    # Version
    "__version__",
    
    # Settings
    "settings",
    "FrameworkSettings",
    
    # Core Classes
    "BasePage",
    "BaseTest",
    
    # Smart Locator
    "SmartLocator",
    "LocatorType",
    "create_smart_locator",
    "ElementNotFoundError",
    
    # Browser Factory
    "BrowserFactory",
    "BrowserSession",
    "browser_session",
    
    # Retry & Wait
    "retry",
    "RetryHandler",
    "WaitHandler",
    "WaitCondition",
]
