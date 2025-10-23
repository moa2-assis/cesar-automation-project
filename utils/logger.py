import logging
import sys
from pathlib import Path
from typing import Optional, Union

_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
_DATEFMT = '%Y-%m-%d %H:%M:%S'

def setup_logger(log_file: Optional[Union[str, Path]] = None) -> logging.Logger:
    logger = logging.getLogger("automation_tests")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # evita logs duplicados

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter(_FMT, datefmt=_DATEFMT))
        logger.addHandler(ch)

    if log_file:
        log_path = Path(log_file)
        fh_key = f"file::{log_path.resolve()}"
        if fh_key not in getattr(logger, "_handler_keys", set()):
            log_path.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setFormatter(logging.Formatter(_FMT, datefmt=_DATEFMT))
            logger.addHandler(fh)
            if not hasattr(logger, "_handler_keys"):
                logger._handler_keys = set()
            logger._handler_keys.add(fh_key)

    return logger

log = setup_logger()