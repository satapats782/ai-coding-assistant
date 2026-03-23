# AI Coding Assistant

An AI-powered coding assistant that ingests GitHub repositories, performs semantic code search, and answers repository-aware questions using embeddings, vector search, and LLMs.

## Features
- GitHub repo ingestion
- Semantic code search
- Repository-aware Q&A
- Context-aware multi-turn conversation
- File and line-level citations

## Tech Stack
- FastAPI
- Streamlit
- Sentence Transformers
- FAISS
- OpenAI API

## Run locally

### Backend
```bash
uvicorn app.main:app --reload
