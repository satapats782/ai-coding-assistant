from fastapi import APIRouter
from app.models.schemas import RepoIngestRequest
from app.services.repo_service import RepoService

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/repo")
def ingest_repo(payload: RepoIngestRequest):
    service = RepoService()
    return service.ingest_repo(payload.repo_url)