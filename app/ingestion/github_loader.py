import os
import uuid
from git import Repo

def clone_repo(repo_url: str, base_dir: str):
    os.makedirs(base_dir, exist_ok=True)

    repo_id = str(uuid.uuid4())
    repo_path = os.path.join(base_dir, repo_id)

    Repo.clone_from(repo_url, repo_path)

    return repo_id, repo_path