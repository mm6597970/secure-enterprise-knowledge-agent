from fastapi import FastAPI
from app.api import upload, chat

app = FastAPI(title="AI Knowledge Search Service")

app.include_router(upload.router, prefix="/documents", tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])

@app.get("/health")
def health_check():
    return {"status": "AI Service Running"}
