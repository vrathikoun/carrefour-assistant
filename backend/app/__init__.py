"""Top-level package for carrefour-assistant"""

__author__ = """RATHIKOUN Viphone"""
__email__ = "vrathikoun@gmail.com"
__version__ = "0.1.0"

# logging
from logging import config as logging_config
from pathlib import Path
from .agent import get_carrefour_agent

import yaml

path = "logging.conf.yml"
config = yaml.safe_load(Path(__file__).parent.joinpath(path).read_text())

logging_config.dictConfig(config)

__all__ = ["get_carrefour_agent"]
