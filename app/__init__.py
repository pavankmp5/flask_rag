import os
import sys
import logging

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from dotenv import load_dotenv
from app.config import config_by_name

def create_app(config_name=None):
    load_dotenv(override=True)
    app = Flask(__name__)
    config_name = config_name or "development"
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))
    configure_logging(app)

    from .routes import main
    app.register_blueprint(main)

    return app


def configure_logging(app):
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    app.logger.setLevel(log_level)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )

    app.logger.info("App initialized in %s mode", "debug" if app.config.get("DEBUG") else "production")
