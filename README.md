# AI Coding Assistant

FastAPI backend with RAG over ingested GitHub repos, Streamlit UI, optional session memory and symbol-aware embeddings.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # add OPENAI_API_KEY
mkdir -p data/repos data/faiss
```

Terminal 1 — API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — UI:

```bash
streamlit run frontend/streamlit_app.py
```

Optional: set `AI_ASSISTANT_API` in `.env` if the API is not on `http://127.0.0.1:8000`.

## Publish to GitHub (satapats782)

The repo remote is configured as `origin` → `https://github.com/satapats782/ai-coding-assistant.git`.

**One command** (creates the repo if needed, then pushes):

```bash
export GITHUB_TOKEN=ghp_your_personal_access_token
chmod +x scripts/create_github_repo_and_push.sh
./scripts/create_github_repo_and_push.sh
```

Create a token under [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens) with **repo** scope (classic) or fine-grained access to **Contents: Read and write** for that repository.

After a successful push, remove the token from your shell: `unset GITHUB_TOKEN`.
