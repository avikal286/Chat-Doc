from typing import List, Dict, Any


class RecursiveCharacterTextSplitter:
    """
    Recursively splits text into chunks using a hierarchy of natural separators
    (paragraphs -> lines -> sentences -> words -> characters).
    Maintains chunk overlap to prevent semantic loss at boundaries.
    """

    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 120,
        separators: List[str] = None
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Splits raw text into a list of chunk strings."""
        return self._split(text, self.separators)

    def _split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        separator = separators[-1]
        for sep in separators:
            if sep == "" or sep in text:
                separator = sep
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        chunks = []
        current_chunk = ""

        for split in splits:
            item = split if separator == "" else (split + separator)
            if len(current_chunk) + len(item) <= self.chunk_size:
                current_chunk += item
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # Start new chunk with overlap from the tail of current_chunk
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + item

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Post-process: if any single chunk still exceeds chunk_size and we have deeper separators, recurse
        final_chunks = []
        next_separators = separators[separators.index(separator) + 1:] if separator in separators and separators.index(separator) + 1 < len(separators) else []

        for chunk in chunks:
            if len(chunk) > self.chunk_size and next_separators:
                final_chunks.extend(self._split(chunk, next_separators))
            else:
                final_chunks.append(chunk)

        return final_chunks

    def split_documents(
        self,
        docs: List[Dict[str, Any]],
        document_id: str,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Takes raw document pages/sections and creates chunk objects with rich metadata.
        Returns:
        [
            {
                "chunk_id": "doc123_chunk_0",
                "text": "...",
                "metadata": {
                    "document_id": "doc123",
                    "filename": "annual_report.pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                    "char_count": 482
                }
            },
            ...
        ]
        """
        all_chunks = []
        global_chunk_idx = 0

        for doc_part in docs:
            page_text = doc_part.get("text", "")
            page_number = doc_part.get("page_number", 1)
            raw_chunks = self.split_text(page_text)

            for chunk_text in raw_chunks:
                chunk_id = f"{document_id}_chunk_{global_chunk_idx}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page_number,
                        "chunk_index": global_chunk_idx,
                        "char_count": len(chunk_text),
                    }
                })
                global_chunk_idx += 1

        return all_chunks
