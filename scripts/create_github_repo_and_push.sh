#!/usr/bin/env bash
# Creates https://github.com/satapats782/ai-coding-assistant (if missing) and pushes main.
# Requires: export GITHUB_TOKEN=ghp_...  (classic PAT with "repo" scope, or fine-grained with Contents: Read/Write)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OWNER="${GITHUB_OWNER:-satapats782}"
REPO="${GITHUB_REPO_NAME:-ai-coding-assistant}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Missing GITHUB_TOKEN."
  echo "Create a token: https://github.com/settings/tokens"
  echo "Then run:"
  echo "  export GITHUB_TOKEN=ghp_your_token_here"
  echo "  ./scripts/create_github_repo_and_push.sh"
  exit 1
fi

TMP="$(mktemp)"
HTTP_CODE="$(
  curl -sS -o "$TMP" -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/user/repos" \
    -d "{\"name\":\"${REPO}\",\"private\":false,\"description\":\"AI coding assistant (FastAPI, Streamlit, RAG)\"}"
)"

if [[ "$HTTP_CODE" == "201" ]]; then
  echo "Created GitHub repository ${OWNER}/${REPO}"
elif [[ "$HTTP_CODE" == "422" ]]; then
  if grep -q "already exists" "$TMP" 2>/dev/null; then
    echo "Repository ${OWNER}/${REPO} already exists; continuing to push."
  else
    echo "GitHub API error (HTTP $HTTP_CODE):"
    cat "$TMP"
    exit 1
  fi
else
  echo "GitHub API error (HTTP $HTTP_CODE):"
  cat "$TMP"
  exit 1
fi
rm -f "$TMP"

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${OWNER}/${REPO}.git"

echo "Pushing to origin main..."
git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${OWNER}/${REPO}.git" HEAD:main
git branch --set-upstream-to=origin/main main 2>/dev/null || true

echo "Done: https://github.com/${OWNER}/${REPO}"
