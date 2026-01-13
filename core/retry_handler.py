"""
Provides resilient retry mechanisms for handling unstable environments.
"""

import functools
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

from config.settings import settings

T = TypeVar("T")


@dataclass
class RetryResult:
    """Result of a retry operation."""

    success: bool
    result: Any = None
    attempts: int = 0
    total_time: float = 0.0
    last_error: Optional[Exception] = None
    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class RetryHandler:
    """
    Handles retry logic with exponential backoff.
    Provides both decorator and context manager patterns.
    """

    def __init__(
        self,
        max_retries: int = None,
        initial_delay: float = None,
        max_delay: float = None,
        backoff_multiplier: float = None,
        exceptions_to_catch: Tuple[Type[Exception], ...] = (Exception,),
        logger: logging.Logger = None,
    ):
        self.max_retries = max_retries or settings.RETRY.max_retries
        self.initial_delay = initial_delay or settings.RETRY.initial_delay
        self.max_delay = max_delay or settings.RETRY.max_delay
        self.backoff_multiplier = (
            backoff_multiplier or settings.RETRY.backoff_multiplier
        )
        self.exceptions_to_catch = exceptions_to_catch
        self.logger = logger or logging.getLogger(__name__)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for current attempt using exponential backoff."""
        delay = self.initial_delay * (self.backoff_multiplier**attempt)
        return min(delay, self.max_delay)

    def execute_with_retry(
        self, func: Callable[..., T], *args, **kwargs
    ) -> RetryResult:
        """
        Execute a function with retry logic.

        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            RetryResult with success status and result/error details
        """
        result = RetryResult(success=False)
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            result.attempts = attempt + 1

            try:
                self.logger.debug(
                    f"Attempt {attempt + 1}/{self.max_retries + 1} for {func.__name__}"
                )

                result.result = func(*args, **kwargs)
                result.success = True
                result.total_time = time.time() - start_time

                self.logger.info(
                    f"Success on attempt {attempt + 1} for {func.__name__} "
                    f"(total time: {result.total_time:.2f}s)"
                )
                return result

            except self.exceptions_to_catch as e:
                result.last_error = e
                result.errors.append(
                    {
                        "attempt": attempt + 1,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )

                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {func.__name__}: "
                    f"{type(e).__name__}: {str(e)}"
                )

                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    self.logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)

        result.total_time = time.time() - start_time
        self.logger.error(
            f"All {self.max_retries + 1} attempts failed for {func.__name__}. "
            f"Last error: {result.last_error}"
        )
        return result

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator pattern for retry."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            result = self.execute_with_retry(func, *args, **kwargs)
            if not result.success:
                raise result.last_error
            return result.result

        return wrapper


def retry(
    max_retries: int = None,
    initial_delay: float = None,
    max_delay: float = None,
    backoff_multiplier: float = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        handler = RetryHandler(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            exceptions_to_catch=exceptions,
        )
        return handler(func)

    return decorator


class RetryContext:
    def __init__(
        self,
        max_retries: int = None,
        initial_delay: float = None,
        max_delay: float = None,
        backoff_multiplier: float = None,
        logger: logging.Logger = None,
    ):
        self.handler = RetryHandler(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            logger=logger,
        )
        self._attempt = 0
        self._succeeded = False
        self._last_error: Optional[Exception] = None
        self.logger = logger or logging.getLogger(__name__)

    def __enter__(self) -> "RetryContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False  # Don't suppress exceptions

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._succeeded:
            raise StopIteration

        if self._attempt >= self.handler.max_retries + 1:
            if self._last_error:
                raise self._last_error
            raise StopIteration

        if self._attempt > 0 and self._last_error:
            delay = self.handler.calculate_delay(self._attempt - 1)
            self.logger.info(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

        current_attempt = self._attempt
        self._attempt += 1
        return current_attempt

    def success(self) -> None:
        """Mark the current attempt as successful."""
        self._succeeded = True
        self.logger.info(f"Operation succeeded on attempt {self._attempt}")

    def failed(self, error: Exception) -> None:
        """Mark the current attempt as failed."""
        self._last_error = error
        self.logger.warning(
            f"Attempt {self._attempt} failed: {type(error).__name__}: {str(error)}"
        )

    @property
    def current_attempt(self) -> int:
        """Get the current attempt number (1-indexed)."""
        return self._attempt

    @property
    def succeeded(self) -> bool:
        """Check if operation has succeeded."""
        return self._succeeded
