# imports stdlib
from typing import Callable, Any
import asyncio
import functools
import os

# imports external libs
import logging
from logging.handlers import RotatingFileHandler

# imports local
from logging import Logger


class LogLevelFilter(logging.Filter):
    """
    Custom filter to allow only specific log levels.
    """

    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


def logger_manager(
    name: str,
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
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

    def setup_logger() -> Logger:
        logger: Logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(log_level)

            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            file_handler_info = RotatingFileHandler(
                filename=os.path.join(log_dir, f"{name}.info.log"),
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler_info.setLevel(logging.INFO)
            file_handler_info.addFilter(LogLevelFilter(logging.INFO))
            file_formatter_info = logging.Formatter(log_format)
            file_handler_info.setFormatter(file_formatter_info)
            logger.addHandler(file_handler_info)

            file_handler_error = RotatingFileHandler(
                filename=os.path.join(log_dir, f"{name}.error.log"),
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler_error.setLevel(logging.ERROR)
            file_handler_error.addFilter(LogLevelFilter(logging.ERROR))
            file_formatter_error = logging.Formatter(log_format)
            file_handler_error.setFormatter(file_formatter_error)
            logger.addHandler(file_handler_error)

            console_handler_info = logging.StreamHandler()
            console_handler_info.setLevel(logging.INFO)
            console_handler_info.addFilter(LogLevelFilter(logging.INFO))
            console_formatter_info = logging.Formatter(log_format)
            console_handler_info.setFormatter(console_formatter_info)
            logger.addHandler(console_handler_info)

            console_handler_error = logging.StreamHandler()
            console_handler_error.setLevel(logging.ERROR)
            console_handler_error.addFilter(LogLevelFilter(logging.ERROR))
            console_formatter_error = logging.Formatter(log_format)
            console_handler_error.setFormatter(console_formatter_error)
            logger.addHandler(console_handler_error)

        return logger

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                logger = setup_logger()
                kwargs["log"] = logger
                logger.info(f"Starting {func.__name__}")
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                    raise
                finally:
                    logger.info(f"Finishing {func.__name__}")

        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                logger = setup_logger()
                kwargs["log"] = logger
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
