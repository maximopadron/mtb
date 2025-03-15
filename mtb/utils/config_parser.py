import yaml
import os
from mtb.utils import logger

log = logger.get_logger()

# CONFIG_DIR is set relative to this file. Since this file is at mtb/mtb/utils,
# "../etc" will resolve to mtb/mtb/etc.
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "../etc")

def load_config(filename):
    filepath = os.path.join(CONFIG_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        log.info(f"Configuration loaded from {filepath}")
        return config
    except Exception as e:
        log.error(f"Error loading config file {filepath}: {e}")
        return {}
