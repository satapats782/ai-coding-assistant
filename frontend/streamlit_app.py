import os
from pathlib import Path
from urllib.parse import urlparse

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API_BASE = os.environ.get("AI_ASSISTANT_API", "http://127.0.0.1:8000").rstrip("/")
_parsed_api = urlparse(API_BASE)
_API_HOST = _parsed_api.hostname or "127.0.0.1"
_API_PORT = _parsed_api.port or 8000
_UVICORN_HELP = (
    f"`uvicorn app.main:app --reload --host {_API_HOST} --port {_API_PORT}` "
    f"— must match **{API_BASE}** (`AI_ASSISTANT_API` in `.env`). "
    "If that port is busy, pick another port and update `AI_ASSISTANT_API` to the same URL."
)
REQUEST_TIMEOUT = (15, 600)  # (connect, read) — fail fast if API is not running

st.set_page_config(page_title="AI Coding Assistant", page_icon="💻", layout="centered")

st.title("AI Coding Assistant")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if st.button("Clear Chat", key="clear_chat_btn"):
    st.session_state["chat_history"] = []


def _chat_history_for_api():
    """Prior turns only (current question not yet appended)."""
    payload = []
    for e in st.session_state.get("chat_history") or []:
        cites = []
        for c in e.get("citations") or []:
            cites.append(
                {
                    "file_path": c["file_path"],
                    "start_line": c["start_line"],
                    "end_line": c["end_line"],
                }
            )
        payload.append(
            {
                "question": e["question"],
                "answer": e["answer"],
                "citations": cites,
                "files": list(e.get("files") or []),
            }
        )
    return payload


def _render_chat_history():
    history = st.session_state.get("chat_history") or []
    if not history:
        return
    st.subheader("Conversation")
    for i, entry in enumerate(history, start=1):
        st.markdown(f"**Q{i}:** {entry['question']}")
        st.markdown(entry["answer"])
        citations = entry.get("citations") or []
        if citations:
            st.caption("Citations")
            for c in citations:
                st.write(f"{c['file_path']} ({c['start_line']}-{c['end_line']})")
        files = entry.get("files") or []
        if files:
            st.caption("Relevant files")
            for path in files:
                st.write(path)
        st.divider()


@st.cache_data(ttl=5, show_spinner=False)
def _backend_reachable() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


if not _backend_reachable():
    st.warning(
        f"API is not reachable at **{API_BASE}**. Ingest and chat need the FastAPI server. "
        f"From the project root with the venv active, run: {_UVICORN_HELP}"
    )

repo_url = st.text_input("Enter GitHub Repo URL", key="repo_url_input")

if st.button("Ingest Repo", key="ingest_btn"):
    if not repo_url.strip():
        st.error("Please enter a GitHub repo URL.")
    else:
        st.info("Sending request to the API…")
        try:
            with st.spinner("Indexing repo... this can take 1-3 minutes on first run"):
                response = requests.post(
                    f"{API_BASE}/ingest/repo",
                    json={"repo_url": repo_url},
                    timeout=REQUEST_TIMEOUT,
                )

            if response.status_code == 200:
                data = response.json()
                st.session_state["repo_id"] = data["repo_id"]
                st.session_state["chat_history"] = []
                st.success(f"Repo indexed! Repo ID: {data['repo_id']}")
                st.write(data)
            else:
                st.error(f"Ingestion failed: {response.text}")

        except requests.exceptions.Timeout:
            st.error("Ingestion timed out. Try a smaller repo or check backend logs.")
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the API at {API_BASE}. {_UVICORN_HELP} "
                "(activate the project venv first)."
            )
            _backend_reachable.clear()
        except Exception as e:
            st.error(f"Unexpected error during ingestion: {e}")

question = st.text_input("Ask a question about the repo", key="question_input")

if st.button("Ask Question", key="ask_btn"):
    repo_id = st.session_state.get("repo_id")

    if not repo_id:
        st.error("Please ingest a repo first.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_BASE}/chat",
                    json={
                        "repo_id": repo_id,
                        "question": question.strip(),
                        "top_k": 5,
                        "history": _chat_history_for_api(),
                    },
                    timeout=(15, 180),
                )

            if response.status_code == 200:
                data = response.json()
                st.session_state["chat_history"].append(
                    {
                        "question": question.strip(),
                        "answer": data["answer"],
                        "citations": data.get("citations") or [],
                        "files": data.get("files") or [],
                    }
                )
            else:
                st.error(f"Chat failed: {response.text}")

        except requests.exceptions.Timeout:
            st.error("Chat request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the API at {API_BASE}. {_UVICORN_HELP} "
                "(activate the project venv first)."
            )
            _backend_reachable.clear()
        except Exception as e:
            st.error(f"Unexpected error during chat: {e}")

st.divider()
file_to_explain = st.text_input("Enter file path to explain", key="explain_file_input")

if st.button("Explain File", key="explain_file_btn"):
    repo_id = st.session_state.get("repo_id")

    if not repo_id:
        st.error("Please ingest a repo first.")
    elif not file_to_explain.strip():
        st.error("Please enter a file path.")
    else:
        question = f"Explain the file {file_to_explain.strip()}"
        try:
            with st.spinner("Explaining file..."):
                response = requests.post(
                    f"{API_BASE}/chat",
                    json={
                        "repo_id": repo_id,
                        "question": question,
                        "top_k": 5,
                        "history": _chat_history_for_api(),
                    },
                    timeout=(15, 180),
                )

            if response.status_code == 200:
                data = response.json()
                st.session_state["chat_history"].append(
                    {
                        "question": question,
                        "answer": data["answer"],
                        "citations": data.get("citations") or [],
                        "files": data.get("files") or [],
                    }
                )
            else:
                st.error(f"Explain failed: {response.text}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the API at {API_BASE}. {_UVICORN_HELP} "
                "(activate the project venv first)."
            )
            _backend_reachable.clear()
        except Exception as e:
            st.error(f"Unexpected error: {e}")

_render_chat_history()