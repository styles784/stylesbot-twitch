# import logging
# import logging.handlers
# import logging.config
import datetime
import json

from userconfig import configuration

with open("config.json", "r") as f:
    configuration["OPTIONS"] = json.load(f)

configuration["LOGGING"] = {
    "version": 1,
    "formatters": {
        "timestamped": {
            "format": "{asctime} - {name} - {levelname} - {message}",
            "style": "{",
        },
        "brief": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "brief",
            "stream": "ext://sys.stdout",
        },
        "console_dbg": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "brief",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "timestamped",
            "filename": "bottrap.log",
            "when": "W3",
            "backupCount": 3,
            "utc": "True",
            "atTime": datetime.time(7),
        },
    },
    "loggers": {
        "detailed": {
            "level": "DEBUG",
            "handlers": ["file", "console"],
            "propagate": "no",
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    },
}
