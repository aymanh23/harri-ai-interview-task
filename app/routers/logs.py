from fastapi import APIRouter
import json
from pathlib import Path
from app.settings import settings

router = APIRouter()

@router.get("/query")
def get_query_logs(limit: int = 50):
    path = Path(settings.query_log_file)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    logs = [json.loads(l) for l in lines[-limit:]]
    return logs


@router.get("/feedback")
def get_feedback_logs(limit: int = 50):
    path = Path(settings.feedback_log_file)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    logs = [json.loads(l) for l in lines[-limit:]]
    return logs

@router.get("/error")
def get_feedback_logs(limit: int = 50):
    path = Path(settings.error_log_file)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    logs = [json.loads(l) for l in lines[-limit:]]
    return logs


