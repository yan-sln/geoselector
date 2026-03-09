"""Simple logging configuration for the geoselector package.

This module is imported automatically from the package's ``__init__`` and sets up a
basic logger with a console handler (development) and a rotating file handler
(production). The log level can be overridden with the ``LOG_LEVEL`` environment
variable. Duplicate handlers are avoided when the module is re‑imported.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Log level configurable via environment (default INFO)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Root logger for the package
logger = logging.getLogger()
logger.setLevel(getattr(logging, log_level, logging.INFO))

# Add handlers only once
if not logger.handlers:
    # Common formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (production)
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "geoselector.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MiB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent propagation to parent loggers to avoid duplicate output
    logger.propagate = False

# Optional: enable DEBUG for the ``api.ign`` module via environment variable
if os.getenv("LOG_DEBUG_IGN"):
    logging.getLogger("api.ign").setLevel(logging.DEBUG)
