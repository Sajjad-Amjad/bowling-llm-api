# app/storage.py

import json
from typing import Dict
import os

class Storage:
    def __init__(self, filename: str):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, 'w') as f:
                json.dump({}, f)

    def load_data(self) -> Dict:
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save_data(self, data: Dict):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
