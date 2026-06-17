from sqlalchemy.orm import Session, sessionmaker

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chroma_service import index_chunks


def seed_document_with_chunks(
    session_factory: sessionmaker,
    filename: str,
    chunk_texts: list[str],
) -> Document:
    db: Session = session_factory()
    try:
        document = Document(filename=filename)
        db.add(document)
        db.flush()

        chunk_rows: list[Chunk] = []
        for order, text in enumerate(chunk_texts):
            chunk = Chunk(
                document_id=document.id,
                chunk_text=text,
                page_number=order + 1,
                chunk_order=order,
            )
            db.add(chunk)
            chunk_rows.append(chunk)

        db.flush()
        index_chunks(chunk_rows, source_filename=filename)
        db.commit()
        db.refresh(document)
        return document
    finally:
        db.close()
