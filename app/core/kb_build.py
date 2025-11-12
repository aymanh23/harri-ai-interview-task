from pathlib import Path
from typing import List
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings



from app.config.settings import settings
from app.core.kb_processing import MarkdownChunker

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def build_kb():
    kb_dir = settings.kb_dir
    chroma_dir = settings.chroma_dir
    chroma_dir.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(settings.kb_model_name)
    chunker = MarkdownChunker(settings.kb_chunk_size, settings.kb_chunk_overlap)

    all_docs: List[Document] = []
    for md in sorted(kb_dir.glob("*.md")):
        intent = md.stem  # filename without .md
        text = _read(md)
        chunks = chunker.chunk_markdown(text, intent=intent, source=md.name)
        for ch in chunks:
            all_docs.append(Document(page_content=ch.content, metadata=ch.metadata))

    # def embed_fn(texts: List[str]):
    #     return model.encode(texts, normalize_embeddings=True).tolist()

    embed_fn = SentenceTransformerEmbeddings(model_name=settings.kb_model_name)

    # persist new DB fresh (simple approach); for incremental, clear selectively
    db = Chroma.from_documents(
        documents=all_docs,
        embedding=embed_fn,
        persist_directory=str(chroma_dir),
    )
    db.persist()
    print(f"✅ Built KB with {len(all_docs)} chunks → {chroma_dir}")

if __name__ == "__main__":
    build_kb()
