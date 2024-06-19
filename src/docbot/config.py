# -*- coding: utf-8 -*-
"""
    docbot.config
    ~~~~~~~~~~~~~

    Set up the project constants here.
    Load credentials file if `DEPLOYMENT` is local.

    :copyright: © 2024 by Jiri
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from docbot.constants import DEFAULT_LOG_FORMAT, LOGGER_NAME


def setup(
    logger_name: str, log_level: str | int = logging.DEBUG, fmt: logging.Formatter | None = None
) -> logging.Logger:
    """Setup logging into console with defined name."""

    logger_ = logging.getLogger(logger_name)

    # set up logging handler
    handler = logging.StreamHandler(sys.stdout)
    handler.name = "h_console"
    handler.setFormatter(fmt or logging.Formatter(DEFAULT_LOG_FORMAT))
    handler.setLevel(log_level)
    logger_.addHandler(handler)

    # set logging level
    logger_.setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

    logger_.info("Logger %s setup finished for console", logger_name)
    return logger_


class Config(BaseSettings):
    """Environment variables and their settings."""

    DEPLOYMENT: str = Field("local", validation_alias="DEPLOYMENT")
    LOG_LEVEL: str = Field("DEBUG", validation_alias="DOCBOT_LOG_LEVEL")

    OPENAI_API_KEY: SecretStr | None = None

    PINECONE_INDEX_NAME: str | None = None
    PINECONE_API_KEY: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        case_sensitive=True,
        extra="allow",
    )


def load_dotenv_validate():
    """Load and validate config."""
    load_dotenv()
    Config()


setup(LOGGER_NAME)
_config = Config()

DEPLOYMENT = _config.DEPLOYMENT
LOG_LEVEL = _config.LOG_LEVEL
OPENAI_API_KEY = _config.OPENAI_API_KEY and _config.OPENAI_API_KEY.get_secret_value()

PINECONE_INDEX_NAME = _config.PINECONE_INDEX_NAME
PINECONE_API_KEY = _config.PINECONE_API_KEY and _config.PINECONE_API_KEY.get_secret_value()
