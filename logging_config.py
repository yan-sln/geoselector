import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

def configure_logging(cfg: Dict[str, Any]) -> logging.Logger:
    """Configure le logger racine à partir du dictionnaire de config."""
    log_cfg = cfg.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
    fmt   = log_cfg.get("format", "%(levelname)s:%(name)s:%(message)s")
    handlers: List[logging.Handler] = []

    if log_cfg.get("file"):
        file_handler = logging.FileHandler(log_cfg["file"], encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(fmt))
        handlers.append(file_handler)

    # toujours garder un handler console
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt))
    handlers.append(console)

    logging.basicConfig(level=level, handlers=handlers)
    logger = logging.getLogger("geoselector")
    logger.debug("Logging configuré à partir de %s", cfg.get("logging"))
    return logger