import logging
from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


LOGGER = logging.getLogger(__name__)


@contextmanager
def timed_step(step_name: str, **context: object) -> Iterator[None]:
    """Log elapsed time for a named processing step."""
    start = perf_counter()
    try:
        yield
    finally:
        duration = perf_counter() - start
        details = " ".join(
            f"{key}={value}" for key, value in context.items() if value is not None
        )
        if details:
            LOGGER.info("%s completed in %.3fs (%s)", step_name, duration, details)
        else:
            LOGGER.info("%s completed in %.3fs", step_name, duration)
