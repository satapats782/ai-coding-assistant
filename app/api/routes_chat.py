from fastapi import APIRouter
from app.models.schemas import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
def chat(payload: ChatRequest):
    service = ChatService(payload.repo_id)
    return service.answer_question(
        payload.question,
        top_k=payload.top_k,
        history=payload.history or None,
    )