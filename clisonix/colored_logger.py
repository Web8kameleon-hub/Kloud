"""
kloud Colored Logger
Business: Ledjan Ahmati - WEB8euroweb GmbH
Logs with real color-coded output for ERROR (red) and WARNING (yellow).
"""

from __future__ import annotations

import logging
import sys
from typing import Dict

try:  # pragma: no cover - optional dependency handling
    from colorama import Fore, Style, init as colorama_init
except ImportError:  # pragma: no cover - graceful fallback
    Fore = Style = None  # type: ignore

    def colorama_init(autoreset: bool = True) -> None:  # type: ignore
        """Fallback when colorama is not installed."""

        return None


colorama_init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Formatter that applies color sequences based on record level."""

    COLORS: Dict[int, str] = {
        logging.DEBUG: (Fore.CYAN + Style.DIM) if Fore and Style else "",
        logging.INFO: Fore.GREEN if Fore else "",
        logging.WARNING: Fore.YELLOW if Fore else "",
        logging.ERROR: (Fore.RED + Style.BRIGHT) if Fore and Style else "",
        logging.CRITICAL: (Fore.RED + Style.BRIGHT) if Fore and Style else "",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        reset = Style.RESET_ALL if Style else ""
        return f"{color}{message}{reset}"


def setup_logger(name: str = "kloud", level: int = logging.INFO) -> logging.Logger:
    """Create or retrieve a color-enabled logger."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    has_stdout_handler = any(
        isinstance(handler, logging.StreamHandler) and getattr(handler, "stream", None) is sys.stdout
        for handler in logger.handlers
    )

    if not has_stdout_handler:
        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(level)
        formatter = ColoredFormatter(
            fmt="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        channel.setFormatter(formatter)
        logger.addHandler(channel)

    return logger


if __name__ == "__main__":
    demo_logger = setup_logger("kloud", logging.DEBUG)
    demo_logger.debug("Debug message (cyan)")
    demo_logger.info("System started successfully (green)")
    demo_logger.warning("Memory usage nearing threshold (yellow)")
    demo_logger.error("Connection to database failed (red)")
    demo_logger.critical("CRITICAL SYSTEM FAILURE (bright red)")


