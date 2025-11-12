from typing import List, Dict, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config.settings import settings
from app.core.mock_api import get_employee_info, get_jira_tickets , get_deployments


class KBRetriever:
    def __init__(self):
        self.persist_dir = str(settings.chroma_dir)
        model_name = settings.kb_model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
        )

    def search(self, query: str, intent: str ) -> List[Dict]:
        k = settings.kb_k
        # Optional metadata filter by intent (aligns with your classifier)
        if intent:
            results = self.db.similarity_search(query, k=k, filter={"intent": intent})
        else:
            results = self.db.similarity_search(query, k=k)
        out = []
        for r in results:
            out.append({
                "content": r.page_content,
                "source": r.metadata.get("source"),
                # "intent": r.metadata.get("intent"),
                "section": r.metadata.get("section"),
                "chunk_id": r.metadata.get("chunk_id"),
            })
        return out

class DynamicRetriever:
    def __init__(self):
        self.intent_to_source = {
            "employees_info": get_employee_info,
            "jira_ticket_status": get_jira_tickets,
            "deployment_history": get_deployments,
        }

    def search(self, query:str, intent: str) -> List[Dict]:
        """
        Fetches from the right mock source based on intent.
        Returns the simulated dynamic data response.
        """
        search_fn = self.intent_to_source.get(intent)
        if not search_fn:
            return {"message": f"No dynamic source found for intent '{intent}'."}

        data = search_fn()
        return [{
            "intent": intent,
            "data": data.get("data"),
            "source": data.get("source"),
            "fetched_at": data.get("fetched_at"),
        }]


