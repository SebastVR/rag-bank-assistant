from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingClient(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""

    @abstractmethod
    def embedding_dimension(self) -> int:
        """Return embedding vector size."""
