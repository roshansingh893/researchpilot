"""
Retrieval-Augmented Generation orchestration.

Coordinates retrieval, prompt construction, LLM generation, and citation
assembly without duplicating retrieval logic.
"""

from sqlalchemy.orm import Session

from app.schemas.chat import ChatResponse, SourceReference
from app.schemas.retrieve import RetrieveResult
from app.services.llm_service import generate_answer
from app.services.prompt_builder import build_rag_prompt
from app.services.retrieval_service import retrieve_chunks

NO_CONTEXT_ANSWER = (
    "I could not find sufficient information in the uploaded documents."
)


def _has_meaningful_context(chunks: list[RetrieveResult]) -> bool:
    return bool(chunks) and any(chunk.chunk_text.strip() for chunk in chunks)


def build_citations(chunks: list[RetrieveResult]) -> list[SourceReference]:
    """
    Deduplicate citations by (filename, page_number) while preserving order
    of first appearance in the retrieved ranking.
    """
    seen: set[tuple[str, int | None]] = set()
    sources: list[SourceReference] = []

    for chunk in chunks:
        key = (chunk.source_filename, chunk.page_number)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceReference(
                filename=chunk.source_filename,
                page_number=chunk.page_number,
            )
        )

    return sources


def generate_chat_response(db: Session, question: str) -> ChatResponse:
    """
    Full RAG pipeline: retrieve → prompt → generate → cite.

    When retrieval returns no meaningful context, the LLM is not invoked and a
    safe fallback answer is returned to reduce hallucination risk.
    """
    chunks = retrieve_chunks(db, question)

    if not _has_meaningful_context(chunks):
        return ChatResponse(answer=NO_CONTEXT_ANSWER, sources=[])

    prompt = build_rag_prompt(question, chunks)
    answer = generate_answer(prompt)
    sources = build_citations(chunks)

    return ChatResponse(answer=answer, sources=sources)
