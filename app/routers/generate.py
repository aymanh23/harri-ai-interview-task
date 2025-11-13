from fastapi import APIRouter
from typing import Dict, Any, List
from app.utils.intent_classifier import classifier
from app.utils.retriever import KBRetriever, DynamicRetriever
from app.config.settings import settings
from pydantic import BaseModel, Field
from app.core.llm.llm import LLM

router = APIRouter()
retriever = None
llm = LLM()

class QueryIn(BaseModel):
    query: str

class Output(BaseModel):
    llm: Any
    intents: List[str]
    probabilities: List[float]
    retrievals: List[Any]
    

@router.post("/")
def generate(body: QueryIn) -> Output:
    pred = classifier.predict(body.query, prob_threshold=settings.min_confidence)
    intents = pred.get("intents", [])
    probs = pred.get("probabilities", [])


    
    # if out of scope, skip the retrieval process and directly generate a response with the llm
    if intents and intents[0] == "out_of_scope":
        llm_result = llm.generate(body.query,intents,[])
        return Output(
            llm=llm_result,
            intents=intents,
            probabilities=probs,
            retrievals=[]
            )

    # retrieve per intent and merge
    all_hits: List[Dict[str, Any]] = []
    for it in intents:

        if it in settings.static_data_intents:
            retriever = KBRetriever()
        else:
            retriever = DynamicRetriever()

        hits = retriever.search(body.query, intent=it)
        all_hits.extend(hits)

    # call llm 
    llm_result = llm.generate(body.query,intents,all_hits)


    return Output(
        llm=llm_result,
        intents=intents,
        probabilities=probs,
        retrievals=all_hits
        )

