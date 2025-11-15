from fastapi import APIRouter
from pydantic import BaseModel
import time, json, os
from app.settings import settings
from app.utils.logger import Logger

router = APIRouter()

class FeedbackIn(BaseModel):
    query: str
    answer: str
    helpful: bool
    details: str | None = None
    timestamp: float = time.time()

class FeedbackOut(BaseModel):
    status : str
    saved : bool


@router.post("/")
def save_feedback(body: FeedbackIn):
    Logger.log_feedback(body.model_dump())

    return FeedbackOut(status = "ok", saved = True)
