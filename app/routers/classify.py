# app/routers/classify.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.utils.intent_classifier import classifier
from app.config.settings import settings

router = APIRouter()

class ClassifyRequest(BaseModel):
    query: str = Field(..., min_length=2, description="User message")

class ClassifyResponse(BaseModel):
    intent: str
    confidence: float
    decision: str  # "route" | "clarify" | "out_of_scope"

@router.post("/", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    try:
        result = classifier.predict(req.query)
        intent = result["label"]
        conf = result["confidence"]

        # simple policy: if low confidence -> clarify/out_of_scope bucket
        if conf < settings.min_confidence:
            decision = "clarify" if intent != "out_of_scope" else "out_of_scope"
        else:
            decision = "route" if intent != "out_of_scope" else "out_of_scope"

        return ClassifyResponse(intent=intent, confidence=conf, decision=decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"classification error: {e}")
