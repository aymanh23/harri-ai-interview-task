from fastapi import APIRouter
from typing import Dict, Any, List
from app.utils.intent_classifier import classifier
from app.utils.retriever import KBRetriever, DynamicRetriever
from app.config.settings import settings
from pydantic import BaseModel, Field
from app.core.llm.llm import LLM
from app.utils.logger import Logger 

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

    actions = [] # actions to be logged

    try:
        pred = classifier.predict(body.query, prob_threshold=settings.min_confidence)
        intents = pred.get("intents", [])
        probs = pred.get("probabilities", [])

        actions.append({
            "step": "intent_classified",
            "intents": intents,
            "probabilities": probs
        })

        

        # if out of scope, skip the retrieval process and directly generate a response with the llm
        if intents and intents[0] == "out_of_scope":
            actions.append({
                "step": "out_of_scope detected, skipping retrieval",
            })

            llm_result = llm.generate(body.query,intents,[])
            actions.append({
                "step": "llm_generation",
                "llm_response": llm_result.model_dump()
            })

            result = Output(
                    llm=llm_result,
                    intents=intents,
                    probabilities=probs,
                    retrievals=[]
                )

            Logger.log_query({
                "query" : body.query,
                "actions" : actions,
                "result_returned_to_ui" : result.model_dump()
            })
            return result

        

        # retrieve per intent and merge
        all_hits: List[Dict[str, Any]] = []
        actions.append({"step": "retrieval_started"})

        for it in intents:
            source = ""
            if it in settings.static_data_intents:
                retriever = KBRetriever()
                source = "chromaDB kb"
            else:
                retriever = DynamicRetriever()
                source = "dynamic"

            hits = retriever.search(body.query, intent=it)
            all_hits.extend(hits)

            actions.append({
                "step": "retrieval_performed",
                "intent": it,
                "retrieval_type": source,
                "number of hits": len(hits),
                "hits" : hits
            })

        actions.append({
            "step": "retrieval_aggregated",
            "total_hits": len(all_hits)
        })



        # call llm 
        llm_result = llm.generate(body.query,intents,all_hits)
        actions.append({
            "step": "llm_generation",
            "llm_response": llm_result.model_dump()
        })

        result = Output(
                llm=llm_result,
                intents=intents,
                probabilities=probs,
                retrievals=all_hits
            )

        # log the query result 
        Logger.log_query({
            "query" : body.query,
            "actions" : actions,
            "result_returned_to_ui" : result.model_dump()
        })

        return result
    
    except Exception as e:
        Logger.log_error({
            "query": body.query,
            "error": str(e),
            "actions_before_error": actions
        })
        raise HTTPException(status_code=500, detail="Internal server error occurred.")

