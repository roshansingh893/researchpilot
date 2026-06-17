"""Grounded RAG prompt construction."""

from app.schemas.retrieve import RetrieveResult

INSUFFICIENT_CONTEXT_MESSAGE = (
    "I could not find sufficient information in the provided documents."
)


def build_rag_prompt(question: str, chunks: list[RetrieveResult]) -> str:
    """
    Build a grounded prompt that constrains the LLM to retrieved context only.

    Each chunk is labeled with its source filename and page number so the model
    can reason over traceable evidence. The prompt explicitly instructs the model
    to refuse when the context does not contain the answer.
    """
    context_blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        page_label = (
            f", page {chunk.page_number}" if chunk.page_number is not None else ""
        )
        context_blocks.append(
            f"[{index}] ({chunk.source_filename}{page_label}):\n{chunk.chunk_text}"
        )

    context = "\n\n".join(context_blocks)

    return (
        "You are a research assistant.\n\n"
        "Answer ONLY using the provided context.\n\n"
        "If the answer is not contained in the context, say:\n\n"
        f'"{INSUFFICIENT_CONTEXT_MESSAGE}"\n\n'
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
