from pathlib import Path
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.config.settings import settings
from app.core.kb.kb_processing import MarkdownChunker

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def build_kb():
    kb_dir = settings.kb_dir
    chroma_dir = settings.chroma_dir
    chroma_dir.mkdir(parents=True, exist_ok=True)

    embedding_model = SentenceTransformerEmbeddings(model_name=settings.kb_model_name)
    chunker = MarkdownChunker(settings.kb_chunk_size, settings.kb_chunk_overlap)

    all_docs: List[Document] = []
    for md in sorted(kb_dir.glob("*.md")):
        intent = md.stem  # filename without .md
        text = _read(md)
        chunks = chunker.chunk_markdown(text, intent=intent, source=md.name)
        for ch in chunks:
            all_docs.append(Document(page_content=ch.content, metadata=ch.metadata))

    # persist new DB fresh (simple approach); for incremental, clear selectively
    db = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding_model,
        persist_directory=str(chroma_dir),
    )
    db.persist()
    print(f" Built KB with {len(all_docs)} chunks → {chroma_dir}")


