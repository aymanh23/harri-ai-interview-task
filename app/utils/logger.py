import json
from datetime import datetime
from pathlib import Path
from app.config.settings import settings


class Logger:
    @staticmethod
    def log_query(entry: dict):
        entry["timestamp"] = datetime.utcnow().isoformat()
        with open(settings.query_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    @staticmethod
    def log_feedback(entry: dict):
        entry["timestamp"] = datetime.utcnow().isoformat()
        with open(settings.feedback_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    @staticmethod
    def log_error(err: dict):
        err["timestamp"] = time.time()
        with open(settings.error_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(err) + "\n")
    
