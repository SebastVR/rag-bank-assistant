from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.config.settings import settings
from app.rag.embeddings import SentenceTransformerEmbeddingClient
from app.rag.llm import LlamaCppClient, OllamaClient, OpenAIClient
from app.rag.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from app.rag.reranker import CrossEncoderReranker
from app.rag.vectorstore import QdrantVectorStore


@dataclass
class RetrievalHit:
    score: float
    text: str
    metadata: dict


class RagQueryService:
    def __init__(self):
        self.embedder = SentenceTransformerEmbeddingClient(settings.rag_embedding_model)
        self.vector_store = QdrantVectorStore(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            grpc_port=settings.qdrant_grpc_port,
            collection_name=settings.qdrant_collection_name,
            vector_size=self.embedder.embedding_dimension(),
        )
        self.reranker = CrossEncoderReranker(settings.rag_reranker_model)

    def retrieve(
        self, question: str, limit: int | None = None, use_rerank: bool = True
    ) -> List[RetrievalHit]:
        if limit is None:
            limit = settings.qdrant_max_chunks_retrieved

        query_vector = self.embedder.embed_texts([question])[0]
        points = self.vector_store.search(query_vector=query_vector, limit=limit)

        hits = [
            RetrievalHit(
                score=float(point.score or 0.0),
                text=str(
                    point.payload.get("content") or point.payload.get("text") or ""
                ),
                metadata=dict(point.payload),
            )
            for point in points
        ]

        if not use_rerank or not hits:
            return hits

        reranked = self.reranker.rerank(
            query=question,
            texts=[item.text for item in hits],
            top_k=min(settings.qdrant_max_chunks_reranked, len(hits)),
        )
        return [hits[idx] for idx, _score in reranked]

    def answer(self, question: str, use_rerank: bool = True) -> dict:
        hits = self.retrieve(question=question, use_rerank=use_rerank)
        context = "\n\n".join([item.text for item in hits])
        prompt = RAG_USER_PROMPT_TEMPLATE.format(question=question, context=context)
        llm = self._build_llm_client()
        answer = llm.generate(prompt=prompt, system_prompt=RAG_SYSTEM_PROMPT)

        return {
            "question": question,
            "answer": answer,
            "context_hits": [
                {
                    "score": item.score,
                    "metadata": item.metadata,
                }
                for item in hits
            ],
        }

    def _build_llm_client(self):
        provider = settings.llm_provider.lower()
        if provider == "ollama":
            return OllamaClient(
                base_url=settings.ollama_base_url,
                model=settings.llm_model_name,
            )
        if provider == "openai":
            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required when llm_provider=openai"
                )
            return OpenAIClient(
                api_key=settings.openai_api_key,
                model=settings.llm_model_name,
            )

        return LlamaCppClient(
            model_path=settings.llm_model_path,
        )
