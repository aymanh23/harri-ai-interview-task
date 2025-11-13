from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routers import classify, generate, feedback

app = FastAPI(title=settings.app_name, version=settings.version)

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