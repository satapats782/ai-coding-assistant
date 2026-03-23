from pydantic import BaseModel, Field
from typing import List

class RepoIngestRequest(BaseModel):
    repo_url: str

class RepoIngestResponse(BaseModel):
    repo_id: str
    message: str
    total_files: int
    total_chunks: int

class Citation(BaseModel):
    file_path: str
    start_line: int
    end_line: int

class ChatHistoryTurn(BaseModel):
    question: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    repo_id: str
    question: str
    top_k: int = 5
    history: List[ChatHistoryTurn] = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]