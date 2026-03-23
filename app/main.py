from fastapi import FastAPI
from app.api.routes_ingest import router as ingest_router
from app.api.routes_chat import router as chat_router
from app.api.routes_search import router as search_router

app = FastAPI(title="AI Coding Assistant")

app.include_router(ingest_router)
app.include_router(chat_router)
app.include_router(search_router)

@app.get("/health")
def health():
    return {"status": "ok"}