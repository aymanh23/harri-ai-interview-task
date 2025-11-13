from fastapi import APIRouter
from pydantic import BaseModel
import time, json, os
from app.config.settings import settings

router = APIRouter()

class FeedbackIn(BaseModel):
    query: str
    answer: str
    helpful: bool
    details: str | None = None
    timestamp: float = time.time()


@router.post("/")
def save_feedback(body: FeedbackIn):
    log = body.dict()

    with open(settings.feedback_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")

    return {"status": "ok", "saved": True}
