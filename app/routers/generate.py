from fastapi import APIRouter
from typing import Dict, Any, List
from app.utils.intent_classifier import classifier
from app.utils.retriever import KBRetriever, DynamicRetriever
from app.config.settings import settings
from pydantic import BaseModel, Field
from app.config.settings import settings

router = APIRouter()
retriever = None

class QueryIn(BaseModel):
    query: str

@router.post("/")
def generate(body: QueryIn) -> Dict[str, Any]:
    pred = classifier.predict(body.query, prob_threshold=settings.min_confidence)
    intents = pred.get("intents", [])
    probs = pred.get("probabilities", [])

    
    if intents and intents[0] == "out_of_scope":
        return {
            "intents": intents, "probabilities": probs,
            "decision": "clarify",
            "answer": "This seems outside my scope. Could you clarify what you need?",
            "sources": []
        }

    # retrieve per intent and merge
    all_hits: List[Dict[str, Any]] = []
    for it in intents:

        if it in settings.static_data_intents:
            retriever = KBRetriever()
        else:
            retriever = DynamicRetriever()

        hits = retriever.search(body.query, intent=it)
        all_hits.extend(hits)

    return {
        "intents": intents,
        "probabilities": probs,
        "retrievals": all_hits,
    }
