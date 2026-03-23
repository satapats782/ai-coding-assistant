import os
from app.core.config import settings
from app.ingestion.github_loader import clone_repo
from app.ingestion.repo_scanner import scan_repo
from app.ingestion.file_loader import read_file
from app.ingestion.parser import extract_python_symbols
from app.chunking.code_chunker import chunk_code
from app.embeddings.embedder import Embedder
from app.embeddings.vector_store import FaissStore

class RepoService:
    def __init__(self):
        print("Loading embedding model...")
        self.embedder = Embedder()
        print("Embedding model loaded.")

    def ingest_repo(self, repo_url: str):
        print(f"Cloning repo: {repo_url}")
        repo_id, repo_path = clone_repo(repo_url, settings.REPO_DIR)
        print(f"Repo cloned to: {repo_path}")

        files = scan_repo(repo_path)
        print(f"Total files found: {len(files)}")

        all_chunks = []
        texts_to_embed = []
        metadata = []

        for i, file_path in enumerate(files, start=1):
            print(f"Processing file {i}/{len(files)}: {file_path}")

            content = read_file(file_path)
            if not content.strip():
                continue

            relative_path = os.path.relpath(file_path, repo_path)
            symbols = []
            if relative_path.endswith(".py"):
                symbols = extract_python_symbols(content)

            chunks = chunk_code(content, relative_path)

            for chunk in chunks:
                symbol_names = ", ".join([s["name"] for s in symbols]) if symbols else "None"

                enriched_text = (
                    f"FILE: {chunk['file_path']}\n"
                    f"LINES: {chunk['start_line']}-{chunk['end_line']}\n"
                    f"SYMBOLS: {symbol_names}\n"
                    f"CONTENT:\n{chunk['content']}"
                )
                texts_to_embed.append(enriched_text)
                metadata.append(chunk)
                all_chunks.append(chunk)

        print(f"Total chunks created: {len(all_chunks)}")
        print("Generating embeddings...")

        embeddings = self.embedder.embed_texts(texts_to_embed)
        dim = embeddings.shape[1]

        print("Embeddings generated. Saving FAISS index...")

        index_path = os.path.join(settings.FAISS_DIR, f"{repo_id}.index")
        metadata_path = os.path.join(settings.FAISS_DIR, f"{repo_id}_meta.pkl")

        vector_store = FaissStore(dim, index_path, metadata_path)
        vector_store.add(embeddings, metadata)
        vector_store.save()

        print("Index saved successfully.")

        return {
            "repo_id": repo_id,
            "message": "Repository indexed successfully",
            "total_files": len(files),
            "total_chunks": len(all_chunks)
        }