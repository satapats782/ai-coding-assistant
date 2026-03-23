import faiss
import numpy as np
import pickle
import os

class FaissStore:
    def __init__(self, dim: int, index_path: str, metadata_path: str):
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, embeddings, metadata):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_embedding, top_k=5):
        query_vector = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                results.append({
                    "score": float(score),
                    "metadata": self.metadata[idx]
                })

        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)