"""
Registry for API strategy classes.

Allows dynamic discovery of concrete ``ApiStrategy`` implementations without
hard‑coding them in the ``SelectorFactory``. Each strategy registers itself at
import time via ``register_strategy``.
"""

import logging
from typing import Dict, Type
from .strategy import ApiStrategy

logger = logging.getLogger(__name__)

_registry: Dict[str, Type[ApiStrategy]] = {}


def register_strategy(name: str, cls: Type[ApiStrategy]) -> None:
    """Register a concrete ``ApiStrategy`` implementation.

    Parameters
    ----------
    name: str
        Identifier used by the ``SelectorFactory`` (e.g. ``"gouvfr"``).
    cls: Type[ApiStrategy]
        The concrete strategy class.
    """
    _registry[name.lower()] = cls
    logger.info("Strategy '%s' registered: %s", name, cls)


def get_strategy_class(name: str) -> Type[ApiStrategy]:
    """Retrieve a registered strategy class.

    Raises
    ------
    KeyError
        If the name is not registered.
    """
    return _registry[name.lower()]


def clear_registry() -> None:
    """Remove all registered strategies (useful for tests)."""
    _registry.clear()
