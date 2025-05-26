import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.defaults = {
            "priorities": {"security": 1, "performance": 1, "readability": 1},
            "style": {
                "python": {"line_length": 88, "indent": 4},
                "javascript": {"printWidth": 80, "tabWidth": 2},
                "java": {"maxLineLength": 100}
            },
            "exclude": [],
            "aggressiveness": "moderate",
            "languages": ["python", "javascript", "java"]
        }
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = {**self.defaults, **json.load(f)}
        else:
            self.config = self.defaults
    
    def get(self, key):
        return self.config.get(key)
    
    def get_style(self, language):
        return self.config["style"].get(language, {})