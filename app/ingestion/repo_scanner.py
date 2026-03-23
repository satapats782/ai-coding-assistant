import os
from app.core.config import settings

def scan_repo(repo_path: str):
    collected_files = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in settings.IGNORED_DIRS]

        for file_name in files:
            ext = os.path.splitext(file_name)[1]
            if ext not in settings.ALLOWED_EXTENSIONS:
                continue

            full_path = os.path.join(root, file_name)
            collected_files.append(full_path)

    return collected_files