def chunk_code(content: str, file_path: str, chunk_size: int = 200, overlap: int = 30):
    lines = content.splitlines()
    chunks = []

    start = 0
    chunk_index = 0

    while start < len(lines):
        end = min(start + chunk_size, len(lines))
        chunk_text = "\n".join(lines[start:end])

        chunks.append({
            "chunk_id": f"{file_path}::chunk_{chunk_index}",
            "file_path": file_path,
            "start_line": start + 1,
            "end_line": end,
            "content": chunk_text
        })

        chunk_index += 1
        start += chunk_size - overlap

    return chunks