import json
import os

class Settings:
    def __init__(self):
        self.config_file = "src/configs/bg-config.json"
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print("Config file not found!")
            self.config = {}

    def get_backgrounds_directory(self):
        return self.config.get("backgrounds_directory", "")

    def get_default_background(self):
        return self.config.get("default_background", "")

    def get_available_backgrounds(self):
        return self.config.get("available_backgrounds", [])
