import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "AI Coding Assistant"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    DATA_DIR = "data"
    REPO_DIR = "data/repos"
    FAISS_DIR = "data/faiss"

    ALLOWED_EXTENSIONS = {
        ".py", ".md"
    }

    IGNORED_DIRS = {
        ".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".next"
    }

settings = Settings()