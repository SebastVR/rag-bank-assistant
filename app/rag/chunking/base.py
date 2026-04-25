from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ChunkedText:
    content: str
    index: int
    metadata: Dict[str, object]


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, object]) -> List[ChunkedText]:
        """Split a long text into chunks with metadata."""
