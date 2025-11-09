# app/api/routes/chat_route.py
from fastapi import APIRouter
from pydantic import BaseModel
from api.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["Chat"])
controller = ChatController()

class ChatRequest(BaseModel):
    session_id: str | None = None
    query: str
    domain: str | None = None

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint to handle user queries.
    """
    return await controller.handle_chat(request.session_id, request.query, request.domain)
