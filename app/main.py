from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings
from app.routers import classify, generate, feedback, logs
from app.chromaKB_build import build_kb
import os 

app = FastAPI(title=settings.app_name, version=settings.version)

@app.on_event("startup")
def initialize_kb_and_logs():
    chroma_dir = settings.chroma_dir
    # Run only if DB is empty / missing
    if not os.path.exists(chroma_dir) or len(os.listdir(chroma_dir)) == 0:
        build_kb()

    # create query log file doesnt exist 
    if not os.path.exists(settings.query_log_file):
        with open(settings.query_log_file, "w", encoding="utf-8") as f:
            pass  # create empty file

    # create error log file if it doesnt exist 
    if not os.path.exists(settings.error_log_file):
        with open(settings.error_log_file, "w", encoding="utf-8") as f:
            pass  # create empty file
        


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "version": settings.version}

# include routers
app.include_router(classify.router, prefix="/classify", tags=["classify"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])