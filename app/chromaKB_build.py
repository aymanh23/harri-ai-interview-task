from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from app.settings import settings


def _read(path):
    """Read raw text from a markdown file."""
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_markdown_file(file_text: str, intent: str, source: str) -> List[Document]:
    """
    Split markdown using:
       1) MarkdownHeaderTextSplitter → to detect sections
       2) RecursiveCharacterTextSplitter → to chunk long sections
    """

    # Split by headers
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "header_1"),
            ("##", "header_2"),
            ("###", "header_3"),
        ]
    )
    header_docs = header_splitter.split_text(file_text)

    # Chunk each header block using recursive splitter
    chunker = RecursiveCharacterTextSplitter(
        chunk_size=settings.kb_chunk_size,
        chunk_overlap=settings.kb_chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    final_docs: List[Document] = []
    cid = 0

    for d in header_docs:

        # Extract section name (if present)
        section = None
        if "header_3" in d.metadata:
            section = d.metadata["header_3"]
        elif "header_2" in d.metadata:
            section = d.metadata["header_2"]
        elif "header_1" in d.metadata:
            section = d.metadata["header_1"]
        else:
            section = "Preamble"

        # perform recursive splitting, a header block will be split if contents > settings.kb_chunk_size
        # otherwise the header block will be considered a chunk as it is
        chunks = chunker.split_text(d.page_content)

        for chunk in chunks:
            final_docs.append(
                Document(
                    page_content=chunk.strip(),
                    metadata={
                        "intent": intent,
                        "source": source,
                        "section": section,
                        "chunk_id": cid
                    }
                )
            )
            cid += 1

    return final_docs



def build_kb():
    """Builds the ChromaDB knowledge base from markdown files that are stored in app/data/kb."""

    kb_dir = settings.kb_dir
    chroma_dir = settings.chroma_dir
    chroma_dir.mkdir(parents=True, exist_ok=True)

    embedding_model = SentenceTransformerEmbeddings(model_name=settings.kb_model_name)

    all_docs: List[Document] = []

    # Process all markdown files
    for md in sorted(kb_dir.glob("*.md")):
        intent = md.stem
        file_text = _read(md)

        docs = chunk_markdown_file(file_text, intent=intent, source=md.name)
        all_docs.extend(docs)

    # Create vectorstore
    db = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding_model,
        persist_directory=str(chroma_dir),
    )
    db.persist()

    print(f" Built KB with {len(all_docs)} chunks → {chroma_dir}")
