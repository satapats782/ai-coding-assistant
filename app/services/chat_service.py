import os
from typing import List, Optional

from openai import OpenAI

from app.core.config import settings
from app.models.schemas import ChatHistoryTurn
from app.embeddings.embedder import Embedder
from app.embeddings.vector_store import FaissStore
from app.retrieval.retriever import Retriever

class ChatService:
    def __init__(self, repo_id: str):
        self.repo_id = repo_id
        self.embedder = Embedder()

        index_path = os.path.join(settings.FAISS_DIR, f"{repo_id}.index")
        metadata_path = os.path.join(settings.FAISS_DIR, f"{repo_id}_meta.pkl")

        sample_embedding = self.embedder.embed_query("test")
        dim = len(sample_embedding)

        self.vector_store = FaissStore(dim, index_path, metadata_path)
        self.vector_store.load()

        self.retriever = Retriever(self.embedder, self.vector_store)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    _MAX_HISTORY_TURNS = 12

    def _format_session_history(self, history: Optional[List[ChatHistoryTurn]]) -> str:
        if not history:
            return ""
        recent = history[-self._MAX_HISTORY_TURNS :]
        parts = [
            "Prior conversation in this session (use it to resolve follow-ups like "
            '"that file" or "the main logic"):',
        ]
        for turn in recent:
            parts.append(f"User: {turn.question}")
            parts.append(f"Assistant: {turn.answer}")
            if turn.files:
                parts.append(f"Mentioned files: {', '.join(turn.files)}")
            if turn.citations:
                cites = [
                    f"{c.file_path}:{c.start_line}-{c.end_line}" for c in turn.citations[:15]
                ]
                parts.append(f"Citations from that turn: {'; '.join(cites)}")
            parts.append("")
        return "\n".join(parts).strip()

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        history: Optional[List[ChatHistoryTurn]] = None,
    ):
        results = self.retriever.retrieve(question, top_k=top_k)

        context_blocks = []
        citations = []

        for item in results:
            meta = item["metadata"]
            context_blocks.append(
                f"FILE: {meta['file_path']}\n"
                f"LINES: {meta['start_line']}-{meta['end_line']}\n"
                f"CONTENT:\n{meta['content']}"
            )

            citations.append({
                "file_path": meta["file_path"],
                "start_line": meta["start_line"],
                "end_line": meta["end_line"]
            })

        context_text = "\n\n".join(context_blocks)

        history_block = self._format_session_history(history)
        if history_block:
            history_block = history_block + "\n\n"

        prompt = f"""
You are an expert software engineer.

{history_block}Answer the question using ONLY the repository context provided (and the prior session context above for disambiguation).

Instructions:
- Do NOT hallucinate
- If unsure, say "Not found in repository"
- Always mention file paths and line ranges
- Be concise but clear
- Use prior Q&A when the user refers to something mentioned earlier (e.g. "that file")
- Structure answer like:
  1. Summary
  2. Key files involved
  3. Explanation

Question:
{question}

Repository Context:
{context_text}
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        files = list(set([c["file_path"] for c in citations]))
        return {
            "answer": response.choices[0].message.content,
            "citations": citations,
            "files": files,
        }