# app/routers/classify.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.utils.intent_classifier import classifier
from app.config.settings import settings

router = APIRouter()

class ClassifyRequest(BaseModel):
    query: str = Field(..., min_length=2, description="User message")

class ClassifyResponse(BaseModel):
    intents: list
    probabilities: list


@router.post("/", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    try:
        result = classifier.predict(req.query)
        intents = result["intents"]
        probabilities = result["probabilities"]

        return ClassifyResponse(intents=intents, probabilities=probabilities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"classification error: {e}")
