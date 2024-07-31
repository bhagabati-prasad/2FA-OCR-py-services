import os

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "docs_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/docs.log",
            "formatter": "standard",
        },
        "biometric_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/biometric.log",
            "formatter": "standard",
        },
        "cheque_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/cheque.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "docs_logger": {
            "handlers": ["docs_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "biometric_logger": {
            "handlers": ["biometric_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "cheque_logger": {
            "handlers": ["cheque_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
