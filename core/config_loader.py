"""Configuration loader for the geoselector package.

Provides a singleton‑style loader that reads the YAML configuration file
once and exposes an immutable mapping.  The loader can be re‑used by any
module that needs configuration without re‑reading the file on each import.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Any

# The path is defined in the package root ``__init__`` as ``CONFIG_PATH``.
# Importing it here avoids circular imports because ``__init__`` does not
# import ``config_loader``.
from .. import CONFIG_PATH

class ConfigLoader:
    """Singleton configuration loader.

    The first call reads the YAML file and stores a read‑only mapping.
    Subsequent calls return the same mapping, ensuring that the configuration
    is loaded only once during the interpreter lifetime.
    """

    _config: Mapping[str, Any] | None = None

    @classmethod
    def load(cls) -> Mapping[str, Any]:
        """Load the configuration file if not already loaded.

        Returns
        -------
        Mapping[str, Any]
            An immutable view of the configuration dictionary.
        """
        if cls._config is None:
            # ``CONFIG_PATH`` is a ``Path`` object pointing to ``config/config.yaml``.
            raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
            # ``MappingProxyType`` provides a read‑only wrapper.
            cls._config = MappingProxyType(raw)
        return cls._config

    @classmethod
    def get_section(cls, section: str) -> Mapping[str, Any]:
        """Convenient accessor for a top‑level section of the config.

        Parameters
        ----------
        section: str
            The top‑level key (e.g. ``"api"`` or ``"endpoints"``).
        """
        config = cls.load()
        if section not in config:
            raise KeyError(f"Configuration section '{section}' not found")
        return config[section]
