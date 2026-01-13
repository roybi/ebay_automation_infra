import functools
from pathlib import Path
from typing import Any, Callable

try:
    import allure
    from allure_commons.types import AttachmentType, Severity

    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

    # Create dummy classes for when Allure is not installed
    class AttachmentType:
        PNG = "image/png"
        JSON = "application/json"
        TEXT = "text/plain"
        HTML = "text/html"

    class Severity:
        BLOCKER = "blocker"
        CRITICAL = "critical"
        NORMAL = "normal"
        MINOR = "minor"
        TRIVIAL = "trivial"


class AllureHelper:
    """Helper class for Allure reporting."""

    @staticmethod
    def is_available() -> bool:
        """Check if Allure is available."""
        return ALLURE_AVAILABLE

    @staticmethod
    def attach_screenshot(screenshot_path: str, name: str = "Screenshot") -> None:
        """Attach a screenshot to the Allure report.
        Args:
            name (str): The name of the attachment.
            screenshot_path (Path): The path to the screenshot file.
        """
        if not ALLURE_AVAILABLE:
            return
        path = Path(screenshot_path)
        if path.exists():
            with open(path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=name,
                    attachment_type=AttachmentType.PNG,
                )

    @staticmethod
    def attach_text(name: str, text: str) -> None:
        """Attach a text content to the Allure report.

        Args:
            name (str): The name of the attachment.
            text (str): The text content to attach.
        """
        if ALLURE_AVAILABLE:
            allure.attach(
                text,
                name=name,
                attachment_type=AttachmentType.TEXT,
            )

    @staticmethod
    def attach_json(data: dict, name: str = "JSON Data") -> None:
        """Attach JSON data to report."""
        if not ALLURE_AVAILABLE:
            return

        import json

        allure.attach(
            json.dumps(data, indent=2), name=name, attachment_type=AttachmentType.JSON
        )

    @staticmethod
    def attach_html(html: str, name: str = "HTML Content") -> None:
        """Attach HTML content to report."""
        if not ALLURE_AVAILABLE:
            return

        allure.attach(html, name=name, attachment_type=AttachmentType.HTML)

    @staticmethod
    def step(name: str):
        """
        Create an Allure step.

        Can be used as decorator or context manager:
            @AllureHelper.step("Click login button")
            def click_login(self):
                ...

            with AllureHelper.step("Fill form"):
                ...
        """
        if ALLURE_AVAILABLE:
            return allure.step(name)

        # Return dummy context manager when Allure not available
        class DummyStep:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def __call__(self, func):
                return func

        return DummyStep()

    @staticmethod
    def feature(name: str):
        """Mark test with feature."""
        if ALLURE_AVAILABLE:
            return allure.feature(name)
        return lambda f: f

    @staticmethod
    def story(name: str):
        """Mark test with story."""
        if ALLURE_AVAILABLE:
            return allure.story(name)
        return lambda f: f

    @staticmethod
    def title(name: str):
        """Set test title."""
        if ALLURE_AVAILABLE:
            return allure.title(name)
        return lambda f: f

    @staticmethod
    def description(text: str):
        """Set test description."""
        if ALLURE_AVAILABLE:
            return allure.description(text)
        return lambda f: f

    @staticmethod
    def severity(level: str):
        """Set test severity."""
        if ALLURE_AVAILABLE:
            severity_map = {
                "blocker": Severity.BLOCKER,
                "critical": Severity.CRITICAL,
                "normal": Severity.NORMAL,
                "minor": Severity.MINOR,
                "trivial": Severity.TRIVIAL,
            }
            return allure.severity(severity_map.get(level.lower(), Severity.NORMAL))
        return lambda f: f

    @staticmethod
    def link(url: str, name: str = None):
        """Add link to test."""
        if ALLURE_AVAILABLE:
            return allure.link(url, name=name)
        return lambda f: f

    @staticmethod
    def issue(url: str):
        """Link test to issue."""
        if ALLURE_AVAILABLE:
            return allure.issue(url)
        return lambda f: f

    @staticmethod
    def testcase(url: str):
        """Link test to test case."""
        if ALLURE_AVAILABLE:
            return allure.testcase(url)
        return lambda f: f

    @staticmethod
    def severity_level(level: Severity) -> Callable:
        """Decorator to set the severity level of a test case.

        Args:
            level (Severity): The severity level to set.

        Returns:
            Callable: The decorated function with severity level set.
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if ALLURE_AVAILABLE:
                    allure.severity(level)
                return func(*args, **kwargs)

            return wrapper

        return decorator


def allure_step(name: str):
    """
    Decorator to create Allure step.

    Usage:
        @allure_step("Login to application")
        def login(self, username, password):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if ALLURE_AVAILABLE:
                with allure.step(name):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def attach_screenshot_on_failure(func: Callable) -> Callable:
    """Decorator to attach a screenshot on test failure.

    Args:
        func (Callable): The test function to decorate.

    Returns:
        Callable: The decorated function with screenshot attachment on failure.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            page = None
            if args:
                if hasattr(args[0], "page"):
                    page = args[0].page
                elif hasattr(args[0], "screenshot"):
                    page = args[0]
            if page:
                try:
                    screenshot = page.screenshot()
                    if ALLURE_AVAILABLE:
                        allure.attach(
                            screenshot,
                            name=f"Failure - {func.__name__}",
                            attachment_type=AttachmentType.PNG,
                        )
                except Exception:
                    pass
            raise

    return wrapper


# Convenience exports
step = AllureHelper.step
feature = AllureHelper.feature
story = AllureHelper.story
title = AllureHelper.title
severity = AllureHelper.severity
