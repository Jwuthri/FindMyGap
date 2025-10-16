"""
FindMyGap - FastAPI Backend Package
"""
import logging
import logging.config

from rich.console import Console
from rich.logging import RichHandler
from pythonjsonlogger.jsonlogger import JsonFormatter

console = Console()
__version__ = "0.1.0"
__description__ = "A FastAPI + Next.js AI agent application with OpenRouter and Agno"
__author__ = "Julien Wuthrich"


class RichCustomFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rich_handler = RichHandler(rich_tracebacks=False, tracebacks_suppress=[], tracebacks_show_locals=False)

    def format(self, record):
        return super().format(record)


class NoiseFilter(logging.Filter):
    """Filter out noisy monitoring/healthcheck endpoints from logs."""

    IGNORED_PATHS = {"/healthcheck"}

    def filter(self, record):
        """Return False to filter out the log record."""
        message = record.getMessage()
        for path in self.IGNORED_PATHS:
            if path in message:
                return False
        return True


def get_handler():
    return ["console"]


def get_level():
    # Always respect LOG_LVL environment variable if explicitly set
    return "INFO"


local_env_loggers = {
    "sentence_transformers": {
        "handlers": get_handler(),
        "level": get_level(),
        "propagate": False,
    },
    "uvicorn": {
        "handlers": get_handler(),
        "level": get_level(),
        "propagate": False,
    },
    "openai": {
        "handlers": get_handler(),
        "level": "WARNING",
        "propagate": False,
    },
    "git": {
        "handlers": get_handler(),
        "level": get_level(),
        "propagate": False,
    },
    "ably": {
        "handlers": get_handler(),
        "level": "WARNING",
        "propagate": False,
    },
    "httpx": {
        "handlers": get_handler(),
        "level": "WARNING",
        "propagate": False,
    },
    "httpcore": {
        "handlers": get_handler(),
        "level": "WARNING",
        "propagate": False,
    },
    "sqlalchemy.engine": {
        "handlers": get_handler(),
        "level": get_level(),
        "propagate": False,
    },
    "pydantic": {
        "handlers": get_handler(),
        "level": "ERROR",
        "propagate": False,
    },
}


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "noise_filter": {
            "()": NoiseFilter,
        },
    },
    "formatters": {
        "console": {
            "()": RichCustomFormatter,
            "format": "%(message)s",
            "datefmt": "<%d %b %Y | %H:%M:%S>",
        },
        "json_datadog": {
            "()": JsonFormatter,
            "format": "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] "
            "[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s "
            "dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s",
            "datefmt": "<%d %b %Y | %H:%M:%S>",
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "INFO",
            "formatter": "console",
            "rich_tracebacks": True,
            "tracebacks_show_locals": False,
            "filters": ["noise_filter"],
        },
        "datadog": {
            "class": "logging.StreamHandler",
            "formatter": "json_datadog",
            "filters": ["noise_filter"],
        },
    },
    "loggers": {
        "": {
            "handlers": get_handler(),
            "level": "INFO",
            "propagate": True,
        },
        "uvicorn.access": {
            "handlers": get_handler(),
            "level": "WARNING",
            "propagate": False,
            "filters": ["noise_filter"],
        },
        "gunicorn.access": {
            "handlers": get_handler(),
            "level": "WARNING",
            "propagate": False,
            "filters": ["noise_filter"],
        },
    }
    | local_env_loggers,
}


logging.captureWarnings(True)
logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(f"app.{name}")

    return logging.getLogger("app")
