import yaml
import os

CONFIG_FILE = os.path.join(os.getcwd(), "config.yaml")

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

DATA_PATH = os.path.abspath(config.get("data_path", "./data"))
DEFAULT_EXPIRY = config.get("default_expiry", "")
LOG_LEVEL = config.get("log_level", "INFO")
