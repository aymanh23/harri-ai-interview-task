import re
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class KBChunk:
    content: str
    metadata: Dict[str, str]

class MarkdownChunker:
    """Primary: split by markdown headers; Fallback: recursive char splitter."""
    def __init__(self, max_len: int = 500, overlap: int = 80):
        self.max_len = max_len
        self.overlap = overlap

    def split_by_headers(self, text: str) -> List[Dict[str, str]]:
        # Split on headers and keep header text
        parts = re.split(r'(?m)^(#{1,6}\s.*)$', text)
        # parts like: ["preamble", "## Sec1", "content1", "## Sec2", "content2", ...]
        sections = []
        preamble = parts[0].strip()
        if preamble:
            sections.append({"section": "Preamble", "content": preamble})
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            body = parts[i+1].strip() if i+1 < len(parts) else ""
            # strip leading #'s for cleaner section name
            section_name = re.sub(r'^#{1,6}\s*', '', header).strip()
            sections.append({"section": section_name, "content": body})
        return sections

    def _fallback_chunks(self, text: str) -> List[str]:
        # Simple recursive-ish splitter by paragraphs then fixed-size
        paras = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
        chunks: List[str] = []
        buf = ""
        for p in paras:
            if len(buf) + len(p) + 2 <= self.max_len:
                buf = (buf + "\n\n" + p).strip() if buf else p
            else:
                # flush buf into sliding windows if needed
                for piece in self._slide(buf):
                    chunks.append(piece)
                buf = p
        if buf:
            for piece in self._slide(buf):
                chunks.append(piece)
        return chunks or [text[: self.max_len]]  # extreme fallback

    def _slide(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.max_len
            piece = text[start:end]
            chunks.append(piece.strip())
            if end >= len(text):
                break
            start = end - self.overlap
            if start < 0: start = 0
        return chunks

    def chunk_markdown(self, text: str, intent: str, source: str) -> List[KBChunk]:
        out: List[KBChunk] = []
        sections = self.split_by_headers(text)
        cid = 0
        for sec in sections:
            body = sec["content"]
            if len(body) <= self.max_len:
                out.append(KBChunk(
                    content=body,
                    metadata={"intent": intent, "source": source, "section": sec["section"], "chunk_id": str(cid)}
                ))
                cid += 1
            else:
                for sub in self._fallback_chunks(body):
                    out.append(KBChunk(
                        content=sub,
                        metadata={"intent": intent, "source": source, "section": sec["section"], "chunk_id": str(cid)}
                    ))
                    cid += 1
        return out
