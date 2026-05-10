"""
═══════════════════════════════════════════════════════════════════════════════
KNOWLEDGE BASE - Indexing & Retrieval System
═══════════════════════════════════════════════════════════════════════════════

Dokumente: libra, artikuj, kode, API docs.
Indekse: vector stores, keyword, hybrid.
Tagging: domain, level, prerequisites, code_available, lang.

Author: Ledjan Ahmati / Kloud
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
from pathlib import Path
import json
import uuid
import logging
import hashlib

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class DocumentType(Enum):
    """Llojet e dokumenteve"""

    ARTICLE = "article"
    BOOK_CHAPTER = "book_chapter"
    CODE = "code"
    API_DOC = "api_doc"
    TUTORIAL = "tutorial"
    FAQ = "faq"
    PAPER = "paper"
    NOTEBOOK = "notebook"


class ContentLevel(Enum):
    """Niveli i vështirësisë"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Language(Enum):
    """Gjuhët e mbështetura"""

    EN = "en"
    SQ = "sq"  # Shqip
    DE = "de"
    FR = "fr"
    ES = "es"


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT MODEL
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DocumentMetadata:
    """Metadata e dokumentit"""

    domain: str = ""  # p.sh. "ai-ml", "deep-learning"
    level: ContentLevel = ContentLevel.INTERMEDIATE
    language: Language = Language.EN
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    code_available: bool = False
    source_url: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "level": self.level.value,
            "language": self.language.value,
            "tags": self.tags,
            "prerequisites": self.prerequisites,
            "code_available": self.code_available,
            "source_url": self.source_url,
            "author": self.author,
            "published_date": self.published_date,
        }


@dataclass
class Document:
    """Dokument në knowledge base"""

    id: str = field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    title: str = ""
    content: str = ""
    doc_type: DocumentType = DocumentType.ARTICLE
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    # Chunks për retrieval
    chunks: List[str] = field(default_factory=list)
    chunk_embeddings: List[List[float]] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def compute_hash(self) -> str:
        return hashlib.md5(self.content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content[:500] + "..."
            if len(self.content) > 500
            else self.content,
            "doc_type": self.doc_type.value,
            "metadata": self.metadata.to_dict(),
            "num_chunks": len(self.chunks),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SearchResult:
    """Rezultat i kërkimit"""

    document_id: str
    chunk_index: int
    chunk_text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE INDEX
# ═══════════════════════════════════════════════════════════════════════════════


class KnowledgeBaseIndex:
    """
    KNOWLEDGE BASE INDEX - Sistemi i indeksimit dhe kërkimit

    Mbështet:
    - Vector search (semantic)
    - Keyword search
    - Hybrid search
    - Filtering by metadata
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._documents: Dict[str, Document] = {}
        self._embeddings: Dict[
            str, List[Tuple[int, List[float]]]
        ] = {}  # doc_id -> [(chunk_idx, embedding)]
        self._inverted_index: Dict[
            str, List[Tuple[str, int]]
        ] = {}  # word -> [(doc_id, chunk_idx)]

        logger.info(f"📚 Knowledge Base '{name}' initialized")

    # ─────────────────────────────────────────────────────────────────────────
    # INDEXING
    # ─────────────────────────────────────────────────────────────────────────

    async def index_document(
        self,
        document: Document,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        generate_embeddings: bool = True,
    ) -> str:
        """Indekson një dokument"""

        # Chunk the content
        if not document.chunks:
            document.chunks = self._chunk_text(
                document.content, chunk_size, chunk_overlap
            )

        # Generate embeddings
        if generate_embeddings:
            document.chunk_embeddings = await self._generate_embeddings(document.chunks)

            # Store embeddings
            self._embeddings[document.id] = [
                (i, emb) for i, emb in enumerate(document.chunk_embeddings)
            ]

        # Build inverted index
        for chunk_idx, chunk in enumerate(document.chunks):
            words = self._tokenize(chunk)
            for word in words:
                if word not in self._inverted_index:
                    self._inverted_index[word] = []
                self._inverted_index[word].append((document.id, chunk_idx))

        # Store document
        self._documents[document.id] = document

        logger.info(
            f"📄 Indexed document: {document.id} ({len(document.chunks)} chunks)"
        )
        return document.id

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Ndan tekstin në chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence/paragraph boundary
            if end < len(text):
                for sep in ["\n\n", "\n", ". ", "! ", "? "]:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start + chunk_size // 2:
                        end = last_sep + len(sep)
                        break

            chunks.append(text[start:end].strip())
            start = end - overlap

        return [c for c in chunks if c]

    def _tokenize(self, text: str) -> List[str]:
        """Ndan tekstin në fjalë"""
        import re

        words = re.findall(r"\b\w+\b", text.lower())
        # Remove stopwords
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "and",
            "or",
            "but",
            "if",
            "then",
            "else",
            "when",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
        }
        return [w for w in words if w not in stopwords and len(w) > 2]

    async def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Gjeneron embeddings për chunks"""
        try:
            from core.engines import EngineRequest, EngineMode, get_registry

            embeddings = []
            for chunk in chunks:
                request = EngineRequest(
                    engine_id="clx:nomic-embed-text",
                    mode=EngineMode.EMBEDDING,
                    input_text=chunk,
                )
                response = await get_registry().generate(request)
                if response.success and response.embedding:
                    embeddings.append(response.embedding)
                else:
                    embeddings.append([0.0] * 768)  # Placeholder

            return embeddings

        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return [[0.0] * 768 for _ in chunks]

    # ─────────────────────────────────────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        top_k: int = 5,
        method: str = "hybrid",  # "vector", "keyword", "hybrid"
        filters: Dict[str, Any] = None,
    ) -> List[SearchResult]:
        """Kërkon në knowledge base"""

        if method == "vector":
            results = await self._vector_search(query, top_k * 2)
        elif method == "keyword":
            results = self._keyword_search(query, top_k * 2)
        else:  # hybrid
            vector_results = await self._vector_search(query, top_k)
            keyword_results = self._keyword_search(query, top_k)
            results = self._merge_results(vector_results, keyword_results)

        # Apply filters
        if filters:
            results = self._apply_filters(results, filters)

        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def _vector_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Semantic search me vectors"""
        try:
            from core.engines import EngineRequest, EngineMode, get_registry

            # Get query embedding
            request = EngineRequest(
                engine_id="clx:nomic-embed-text",
                mode=EngineMode.EMBEDDING,
                input_text=query,
            )
            response = await get_registry().generate(request)

            if not response.success or not response.embedding:
                return []

            query_embedding = response.embedding

            # Compute similarities
            results = []
            for doc_id, chunk_embeddings in self._embeddings.items():
                doc = self._documents.get(doc_id)
                if not doc:
                    continue

                for chunk_idx, embedding in chunk_embeddings:
                    score = self._cosine_similarity(query_embedding, embedding)
                    results.append(
                        SearchResult(
                            document_id=doc_id,
                            chunk_index=chunk_idx,
                            chunk_text=doc.chunks[chunk_idx]
                            if chunk_idx < len(doc.chunks)
                            else "",
                            score=score,
                            metadata=doc.metadata.to_dict(),
                        )
                    )

            return results

        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Keyword search me inverted index"""
        query_words = self._tokenize(query)

        # Count matches per (doc_id, chunk_idx)
        match_counts: Dict[Tuple[str, int], int] = {}
        for word in query_words:
            if word in self._inverted_index:
                for doc_id, chunk_idx in self._inverted_index[word]:
                    key = (doc_id, chunk_idx)
                    match_counts[key] = match_counts.get(key, 0) + 1

        # Convert to results
        results = []
        for (doc_id, chunk_idx), count in match_counts.items():
            doc = self._documents.get(doc_id)
            if not doc:
                continue

            score = count / len(query_words) if query_words else 0
            results.append(
                SearchResult(
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    chunk_text=doc.chunks[chunk_idx]
                    if chunk_idx < len(doc.chunks)
                    else "",
                    score=score,
                    metadata=doc.metadata.to_dict(),
                )
            )

        return results

    def _merge_results(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Bashkon rezultatet e vector dhe keyword search"""
        merged: Dict[Tuple[str, int], SearchResult] = {}

        # Weight: vector=0.7, keyword=0.3
        for r in vector_results:
            key = (r.document_id, r.chunk_index)
            if key not in merged:
                merged[key] = r
                merged[key].score = r.score * 0.7
            else:
                merged[key].score += r.score * 0.7

        for r in keyword_results:
            key = (r.document_id, r.chunk_index)
            if key not in merged:
                merged[key] = r
                merged[key].score = r.score * 0.3
            else:
                merged[key].score += r.score * 0.3

        return list(merged.values())

    def _apply_filters(
        self,
        results: List[SearchResult],
        filters: Dict[str, Any],
    ) -> List[SearchResult]:
        """Aplikon filtra në rezultate"""
        filtered = []

        for r in results:
            doc = self._documents.get(r.document_id)
            if not doc:
                continue

            match = True

            if "domain" in filters:
                if doc.metadata.domain != filters["domain"]:
                    match = False

            if "level" in filters:
                if doc.metadata.level.value != filters["level"]:
                    match = False

            if "language" in filters:
                if doc.metadata.language.value != filters["language"]:
                    match = False

            if "tags" in filters:
                if not any(t in doc.metadata.tags for t in filters["tags"]):
                    match = False

            if match:
                filtered.append(r)

        return filtered

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Llogarit cosine similarity"""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    # ─────────────────────────────────────────────────────────────────────────
    # MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        return [doc.to_dict() for doc in self._documents.values()]

    def stats(self) -> Dict[str, Any]:
        """Statistikat e knowledge base"""
        return {
            "name": self.name,
            "num_documents": len(self._documents),
            "num_chunks": sum(len(d.chunks) for d in self._documents.values()),
            "num_words_indexed": len(self._inverted_index),
            "domains": list(set(d.metadata.domain for d in self._documents.values())),
        }

    def save(self, path: Path) -> None:
        """Ruan knowledge base në disk"""
        data = {
            "name": self.name,
            "documents": {
                doc_id: {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "doc_type": doc.doc_type.value,
                    "metadata": doc.metadata.to_dict(),
                    "chunks": doc.chunks,
                }
                for doc_id, doc in self._documents.items()
            },
        }

        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(f"💾 Knowledge Base saved to {path}")

    def load(self, path: Path) -> int:
        """Ngarkon knowledge base nga disk"""
        if not path.exists():
            return 0

        data = json.loads(path.read_text(encoding="utf-8"))

        for doc_data in data.get("documents", {}).values():
            metadata = DocumentMetadata(
                domain=doc_data["metadata"].get("domain", ""),
                level=ContentLevel(doc_data["metadata"].get("level", "intermediate")),
                language=Language(doc_data["metadata"].get("language", "en")),
                tags=doc_data["metadata"].get("tags", []),
            )

            doc = Document(
                id=doc_data["id"],
                title=doc_data["title"],
                content=doc_data["content"],
                doc_type=DocumentType(doc_data.get("doc_type", "article")),
                metadata=metadata,
                chunks=doc_data.get("chunks", []),
            )

            self._documents[doc.id] = doc

        logger.info(f"📂 Loaded {len(self._documents)} documents from {path}")
        return len(self._documents)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

_indices: Dict[str, KnowledgeBaseIndex] = {}


def get_knowledge_base(name: str = "default") -> KnowledgeBaseIndex:
    """Merr ose krijon knowledge base"""
    global _indices
    if name not in _indices:
        _indices[name] = KnowledgeBaseIndex(name)
    return _indices[name]


async def index_document(
    content: str,
    title: str = "",
    metadata: Dict[str, Any] = None,
    kb_name: str = "default",
) -> str:
    """Indekson dokument"""
    kb = get_knowledge_base(kb_name)

    meta = DocumentMetadata()
    if metadata:
        meta.domain = metadata.get("domain", "")
        meta.level = ContentLevel(metadata.get("level", "intermediate"))
        meta.language = Language(metadata.get("language", "en"))
        meta.tags = metadata.get("tags", [])

    doc = Document(title=title, content=content, metadata=meta)
    return await kb.index_document(doc)


async def query_knowledge(
    query: str,
    kb_name: str = "default",
    top_k: int = 5,
    filters: Dict[str, Any] = None,
) -> List[SearchResult]:
    """Kërkon në knowledge base"""
    kb = get_knowledge_base(kb_name)
    return await kb.search(query, top_k=top_k, filters=filters)


__all__ = [
    "DocumentType",
    "ContentLevel",
    "Language",
    "DocumentMetadata",
    "Document",
    "SearchResult",
    "KnowledgeBaseIndex",
    "get_knowledge_base",
    "index_document",
    "query_knowledge",
]
