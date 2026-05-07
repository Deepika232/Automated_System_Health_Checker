from __future__ import annotations

import logging

from dotenv import load_dotenv
from flask import Flask

from app.config import Settings
from app.logging_setup import setup_logging


def create_app() -> Flask:
    load_dotenv()
    settings = Settings()

    setup_logging(settings.log_path)
    logging.getLogger(__name__).info("Starting Automated System Health Checker")

    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    from app.routes import bp

    app.register_blueprint(bp)
    return app
