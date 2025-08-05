import argparse
import logging
import os
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from epic_event.controllers.main_controller import MainController
from epic_event.models.database import Database
from epic_event.models.utils import load_data_in_database, load_super_user
from epic_event.settings import SENTRY_DSN, setup_logging, DATABASES


sentry_logging = LoggingIntegration(level=logging.INFO,
                                    event_level=logging.INFO)
sentry_sdk.init(dsn=SENTRY_DSN,
                integrations=[
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.INFO
                    )
                ],
                send_default_pii=True)

setup_logging()
logger = logging.getLogger(__name__)
logger.handlers = []

parser = argparse.ArgumentParser(
    description="Lancer le serveur en mode normal ou test.")
parser.add_argument("mode", nargs="?", default="main",
                    choices=["main", "demo"])

args = parser.parse_args()
operating_mode = args.mode
use_null_pool = False

if operating_mode == "demo":
    use_null_pool = True
    path = Path(DATABASES[operating_mode])
    if path.exists():
        os.remove(path)

database = Database(DATABASES[operating_mode], use_null_pool)
database.initialize_database()
session = database.get_session()

main_controller = MainController(session)

if operating_mode == "demo":
    load_data_in_database(session)
else:
    load_super_user(session)

if __name__ == "__main__":
    main_controller.run()
