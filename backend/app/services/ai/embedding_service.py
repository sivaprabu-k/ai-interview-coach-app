from google import genai
from google.genai import types

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        if not text.strip():
            raise ValueError("Text cannot be empty")

        response = self.client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=settings.gemini_embedding_dimensions,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned an empty embedding")

        embedding = response.embeddings[0].values

        if embedding is None:
            raise RuntimeError("Gemini returned an empty embedding vector")

        if len(embedding) != settings.gemini_embedding_dimensions:
            raise RuntimeError("Unexpected embedding dimensions")

        return embedding
