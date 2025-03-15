import logging
from pythonjsonlogger import jsonlogger

def get_logger():
    logger = logging.getLogger("mtb")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


import logging
import sys
from pythonjsonlogger import jsonlogger
import colorlog
from mtb.utils import config_parser

def get_global_log_level():
    """
    Loads the global configuration using config_parser and returns the corresponding logging level.
    Defaults to INFO if not set.
    """
    config = config_parser.load_config("config.yaml")
    level_str = config.get("log_level", "INFO")
    return getattr(logging, level_str.upper(), logging.INFO)

def get_logger():
    """
    Configures and returns a logger that writes:
      - JSON-formatted log messages to a file (mtb.log)
      - Plain text messages with colored output to stdout.
    The logger's level is determined by the global configuration (config.yaml) using config_parser.
    """
    logger = logging.getLogger("mtb")
    logger.setLevel(get_global_log_level())
    
    # Only add handlers if they haven't been added yet.
    if not logger.handlers:
        # Console handler with colored output.
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s%(message)s%(reset)s",
            log_colors={
                "DEBUG": "grey",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            }
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with JSON formatting.
        file_handler = logging.FileHandler("mtb.log")
        json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
        
    return logger
