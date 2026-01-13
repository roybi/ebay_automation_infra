"""Configuration package for the automation framework."""

from .settings import (
    BrowserConfig,
    FrameworkSettings,
    LocatorConfig,
    ParallelConfig,
    ReportConfig,
    RetryConfig,
    WaitConfig,
    settings,
)

__all__ = [
    "FrameworkSettings",
    "settings",
    "BrowserConfig",
    "WaitConfig",
    "LocatorConfig",
    "RetryConfig",
    "ReportConfig",
    "ParallelConfig",
]
