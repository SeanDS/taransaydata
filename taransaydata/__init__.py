import os
from configparser import ConfigParser
from pathlib import Path

# Get package version.
try:
    from ._version import version as __version__
except ImportError:
    # Packaging resources are not installed.
    __version__ = "?.?.?"

CONFIG = ConfigParser()

try:
    CONFIG.read(os.getenv("TARANSAY_CONFIG_PATH"))
except TypeError:
    raise Exception("No configuration path found. Set TARANSAY_CONFIG_PATH.")

DATA_DIR = Path(CONFIG["data"]["directory"])
INFO_FILENAME = "info.yaml"
