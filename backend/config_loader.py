import json
import os
from typing import Dict


class ConfigLoader:
    """
    Responsible for loading and providing access
    to the application configuration.
    """

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """
        Load configuration from config.json
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

        return config

    def get(self) -> Dict:
        """
        Return the full configuration dictionary
        """
        return self._config

    def get_section(self, section: str) -> Dict:
        """
        Retrieve a specific section of the config
        """
        if section not in self._config:
            raise KeyError(f"Config section '{section}' not found")

        return self._config[section]