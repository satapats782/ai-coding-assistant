from fastapi import APIRouter, Body

from app.services.chat_service import ChatService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("")
def search(payload: dict = Body(...)):
    service = ChatService(payload["repo_id"])
    results = service.retriever.retrieve(payload["query"], top_k=5)
    return results
