# app/config/settings.py
from pathlib import Path
from pydantic import BaseModel
from typing import Set


BASE_DIR = Path(__file__).resolve().parents[2]  # repo root

class Settings(BaseModel):
    app_name: str = "Harri AI Assistant"
    version: str = "1.0.0"

    # model artifacts
    # model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline.joblib"
    model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline_calibrated.joblib"
    kb_model_name: str = "all-MiniLM-L6-v2"
    # data sources
    kb_dir: Path = BASE_DIR / "app" / "data" / "kb"
    data_path : Path = BASE_DIR / "app" / "data" 
    chroma_dir : Path = BASE_DIR / "app" / "data" / "chroma"




    # retrieval knobs
    kb_chunk_size: int = 500
    kb_chunk_overlap: int = 80
    kb_k: int = 4  # how many chunks to retrieve per intent

    # thresholds
    # intents with probability less than this value will not be considered
    min_confidence: float = 0.1  


    static_data_intents: Set[str] = {"deployment_process","code_review_policy","escalation_policy","onboarding_guide","team_structure"}
    dynamic_data_intent: Set[str]= {"deployment_history","employees_info","jira_ticket_status"}


 
settings = Settings()
