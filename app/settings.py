from pathlib import Path
from pydantic import BaseModel
from typing import Set

BASE_DIR = Path(__file__).resolve().parents[1]  # repo root

class Settings(BaseModel):
    app_name: str = "Harri AI Assistant"
    version: str = "1.0.0"

    # model artifacts
    # model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline.joblib"
    model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline_calibrated.joblib"
    kb_model_name: str = "all-MiniLM-L6-v2"

    # data sources
    data_path : Path = BASE_DIR / "app" / "data"
    kb_dir: Path = data_path / "kb_md_files"
    chroma_dir : Path = data_path / "chroma"

    # log directory and files 
    log_dir : Path = BASE_DIR / "app" / "logs"
    query_log_file : Path = log_dir / "query_logs.jsonl"
    feedback_log_file : Path = log_dir / "feedback_logs.jsonl"
    error_log_file : Path = log_dir / "error_logs.jsonl"

    # retrieval config
    kb_chunk_size: int = 500
    kb_chunk_overlap: int = 80
    kb_k: int = 5  # how many chunks to retrieve per intent

    # router thresholds

    # intents with probability less than this value will not be considered
    min_confidence: float = 0.55        # below this → probably OOS
    oos_min_prob: float = 0.35          # min prob to trust "out_of_scope"
    oos_min_margin: float = 0.15        # how much higher than 2nd-best it must be

    # mapping of intents to data files
    static_data_intents: Set[str] = {"deployment_process","code_review_policy","escalation_policy","onboarding_guide","team_structure"}
    dynamic_data_intent: Set[str]= {"deployment_history","employees_info","jira_ticket_status"}


    # llm config

    

settings = Settings()
