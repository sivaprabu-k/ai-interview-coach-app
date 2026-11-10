class ChunkingService:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:
            remaining = text_length - start

            if chunks and remaining <= self.chunk_overlap:
                break

            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks
