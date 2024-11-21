from typing import Callable, Any
import functools
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler


def logger_manager(
        name: str,
        log_level: int = logging.INFO,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        max_bytes: int = 1_000_000,
        backup_count: int = 3
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to configure a logger for a function, injecting it as `log`.

    Args:
        name (str): Logger name (and base name of the log file).
        log_level (int, optional): Logging level. Defaults to logging.INFO.
        log_format (str, optional): Log message format. Defaults to a standard time-based format.
        max_bytes (int, optional): Maximum size of a log file before rotation. Defaults to 1,000,000 bytes.
        backup_count (int, optional): Number of rotated log files to retain. Defaults to 3.

    Returns:
        Callable: The decorated function with a logger injected as `log`.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            logger: Logger = logging.getLogger(name)

            if not logger.handlers:
                logger.setLevel(log_level)

                file_handler = RotatingFileHandler(
                    filename=f"{name}.log", maxBytes=max_bytes, backupCount=backup_count
                )
                file_formatter = logging.Formatter(log_format)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

                console_handler = logging.StreamHandler()
                console_formatter = logging.Formatter(log_format)
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)

            kwargs['log'] = logger
            logger.info(f"Starting {func.__name__}")
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                raise
            finally:
                logger.info(f"Finishing {func.__name__}")

        return wrapper

    return decorator
