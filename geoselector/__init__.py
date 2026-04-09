# Make geoselector a package

from .logging_config import logger
from .core.selector import SelectorFactory


def reset():
    """Reset the internal service cache."""
    SelectorFactory.reset()


__all__ = ["logger", "reset"]
