"""LogosDB semantic retriever for Cohere Toolkit.

Uses Cohere embed API to index and query a local LogosDB HNSW vector store.
No external infrastructure required — the index lives in a directory on disk.

Configuration (environment variables or configuration.yaml):

    LOGOSDB_PATH         Root directory for the index (default: /tmp/logosdb)
    COHERE_API_KEY       Cohere API key (already required by the toolkit)
    LOGOSDB_EMBED_MODEL  Cohere embedding model (default: embed-english-v3.0)
    LOGOSDB_NAMESPACE    Default collection/namespace (default: default)

Install the extra dependency::

    poetry add logosdb --group community
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import cohere

from backend.config.settings import Settings
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool

logger = logging.getLogger(__name__)

try:
    import numpy as np
    from logosdb import DB, DIST_COSINE

    _LOGOSDB_AVAILABLE = True
except ImportError:
    _LOGOSDB_AVAILABLE = False


_settings = Settings().get("tools.logosdb")


class LogosDBRetriever(BaseTool):
    """Semantic retriever backed by a local LogosDB HNSW vector index.

    Documents are embedded with the Cohere Embed API and stored on disk.
    At query time the question is embedded and the nearest neighbours are
    returned as tool results.

    Because the index is local and mmap-backed, searches are sub-millisecond
    even for millions of vectors — with zero external services.
    """

    ID = "logosdb"

    # Settings resolved once at class load time.
    _logosdb_path: Optional[str] = _settings.path if _settings else None
    _embed_model: str = (
        _settings.embed_model if _settings else "embed-english-v3.0"
    )
    _namespace: str = _settings.namespace if _settings else "default"
    _cohere_api_key: Optional[str] = Settings().get("cohere_platform.api_key")

    # Embedding dimension for embed-english-v3.0 / embed-multilingual-v3.0.
    _DIM = 1024

    def __init__(self) -> None:
        if not _LOGOSDB_AVAILABLE:
            return

        self._co = cohere.Client(api_key=self._cohere_api_key)
        root = self._logosdb_path or "/tmp/logosdb"
        col_path = os.path.join(root, self._namespace)
        os.makedirs(col_path, exist_ok=True)
        self._db = DB(
            path=col_path,
            dim=self._DIM,
            max_elements=1_000_000,
            ef_construction=200,
            M=16,
            ef_search=50,
            distance=DIST_COSINE,
        )

    # ── Availability ──────────────────────────────────────────────────────

    @classmethod
    def is_available(cls) -> bool:
        return (
            _LOGOSDB_AVAILABLE
            and cls._cohere_api_key is not None
            and cls._logosdb_path is not None
        )

    # ── Tool definition ───────────────────────────────────────────────────

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="LogosDB Semantic Search",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": (
                        "Natural-language query to search the local semantic index."
                    ),
                    "type": "str",
                    "required": True,
                },
                "top_k": {
                    "description": "Maximum number of results to return (default 5).",
                    "type": "int",
                    "required": False,
                },
            },
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description=(
                "Semantic search over a local HNSW vector index powered by LogosDB. "
                "Documents are embedded with Cohere's Embed API and retrieved by "
                "cosine similarity — no external database required."
            ),
        )

    # ── Query ─────────────────────────────────────────────────────────────

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        if not _LOGOSDB_AVAILABLE:
            return self.get_tool_error(
                details="logosdb is not installed. Run: poetry add logosdb --group community"
            )

        query = parameters.get("query", "").strip()
        top_k = int(parameters.get("top_k", 5))

        if not query:
            return self.get_no_results_error()

        try:
            resp = self._co.embed(
                texts=[query],
                model=self._embed_model,
                input_type="search_query",
                embedding_types=["float"],
            )
            qvec = np.asarray(resp.embeddings.float[0], dtype=np.float32)
        except Exception as exc:
            return self.get_tool_error(details=f"Cohere embed error: {exc}")

        try:
            hits = self._db.search(qvec, top_k=top_k)
        except Exception as exc:
            return self.get_tool_error(details=f"LogosDB search error: {exc}")

        if not hits:
            return self.get_no_results_error()

        return [
            {
                "text": h.text or f"[vector id={h.id}]",
                "score": float(h.score),
                "url": h.timestamp or "",
            }
            for h in hits
        ]

    # ── Index helper (callable from outside, e.g. a setup script) ────────

    def index(
        self,
        texts: List[str],
        urls: Optional[List[str]] = None,
    ) -> int:
        """Embed and store *texts* in the local index.

        Args:
            texts: Documents to embed and store.
            urls:  Optional source URLs stored as the timestamp field.

        Returns:
            Number of vectors inserted.
        """
        if not _LOGOSDB_AVAILABLE:
            raise RuntimeError("logosdb is not installed.")

        urls = urls or [""] * len(texts)
        resp = self._co.embed(
            texts=texts,
            model=self._embed_model,
            input_type="search_document",
            embedding_types=["float"],
        )
        for text, url, embedding in zip(texts, urls, resp.embeddings.float):
            vec = np.asarray(embedding, dtype=np.float32)
            self._db.put(vec, text=text, timestamp=url)

        return len(texts)
