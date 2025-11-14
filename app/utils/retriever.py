from typing import List, Dict, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.settings import settings
from app.mock_api import get_employee_info, get_jira_tickets , get_deployments


class KBRetriever:
    def __init__(self):
        self.persist_dir = str(settings.chroma_dir)
        model_name = settings.kb_model_name
        self.embeddings = SentenceTransformerEmbeddings(model_name=model_name)
        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
        )

    def search(self, query: str, intent: str ) -> List[Dict]:
        """
        Fetches from chromadb kb based on intent.
        Returns similiar chunks.
        """
        k = settings.kb_k
        
        
        results = self.db.similarity_search(query, k=k, filter={"intent": intent})
        out = []
        for r in results:
            out.append({
                "content": r.page_content,
                "source": r.metadata.get("source"),
                "section": r.metadata.get("section"),
                "chunk_id": r.metadata.get("chunk_id"),
            })
        return out

class DynamicRetriever:
    def __init__(self):
        self.intent_to_source = {
            "employees": get_employee_info,
            "jira_tickets": get_jira_tickets,
            "deployments": get_deployments,
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