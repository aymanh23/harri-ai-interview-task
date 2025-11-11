# app/config/settings.py
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parents[2]  # repo root

class Settings(BaseModel):
    app_name: str = "Harri AI Assistant"
    version: str = "1.0.0"

    # model artifacts
    # model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline.joblib"
    model_path: Path = BASE_DIR / "app" / "ml" / "models" / "intent_pipeline_calibrated.joblib"

    # data sources
    kb_dir: Path = BASE_DIR / "app" / "data" / "kb"
    employees_json: Path = BASE_DIR / "app" / "data" / "employees.json"
    deployments_json: Path = BASE_DIR / "app" / "data" / "deployments.json"
    jira_json: Path = BASE_DIR / "app" / "data" / "jira_tickets.json"

    # thresholds
    min_confidence: float = 0.55  # below → clarification/out_of_scope

settings = Settings()
