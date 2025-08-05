"""
settings.py - Application configuration module.

Defines:
- Entity mapping for french menus.
- Database configurations for different environments.
- Application port settings.
- Sentry DSN for error tracking.
- Logging configuration with console and Sentry handlers.

Provides:
- setup_logging() function to initialize logging.
"""

import logging
import logging.config


ENTITIES = ["collaborator", "client", "contract", "event"]


# to display names in French in the menus
translate_entity = {
    "collaborator": "collaborateur",
    "client": "client",
    "contract": "contrat",
    "event": "événement"
}

DATABASES = {
    "main": "epic_events.db",
    "demo": "demo_epic_event.db",
    "test": "test_epic_event.db"
}

SENTRY_DSN = "https://422a046974326b3d65c42157b707bdc2@o4509643092721664.ingest.de.sentry.io/4509643095146576"

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'sentry': {
            'level': 'INFO',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['console', 'sentry'],
        'level': 'INFO',
    },
}

DB_PATH = "sqlite:///epic_events.db"

SERVICES = ["gestion", "commercial", "support"]
SESSION = {"show_archived": False}

TITLE_STYLE = "bold blue"
LINE_STYLE = "blue"
ERROR_STYLE = "red"
SUCCESS_STYLE = "green"
TEXT_STYLE = "#77DFFE"
REQUEST_STYLE = "yellow"
INFORMATION_STYLE = "magenta"

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)