# import logging
# import logging.handlers
# import logging.config
import datetime
import requests
import json


def save(channels: list[str] = [], modules: list[str] = []):
    with open("config.json", "w") as f:
        configuration["OPTIONS"]["channels"] = channels
        configuration["OPTIONS"]["modules"] = modules
        export = configuration.copy()
        export.pop("LOGGING", None)
        json.dump(export, f, indent="\t")
        # configuration["LOGGING"] = logconf
        # logging.info("Settings saved to config.json")


configuration: dict = {
    "SECRET": {"oauth": "", "client_id": "", "client_secret": ""},
    "OPTIONS": {"prefix": ["!"], "channels": [], "modules": []},
}

try:
    with open("config.json", "r") as f:
        overrides = json.load(f)
        configuration.update(overrides)
except FileNotFoundError:
    with open("config.json", "w") as f:
        # TODO: Interactive first-time setup
        save()
    exit(
        code="Blank config.json generated - edit it to add your authorization \
details and run script again"
    )

if configuration["SECRET"]["oauth"] == "":
    exit(code="Please insert authorization details into config.json")

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
