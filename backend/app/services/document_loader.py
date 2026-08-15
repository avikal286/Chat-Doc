import os
from typing import List, Dict, Any
from pathlib import Path
import pypdf
import docx


class DocumentLoader:
    """Loads and extracts text & metadata from various document formats (PDF, DOCX, TXT, MD)."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    @staticmethod
    def load_document(file_path: str, original_filename: str = "") -> List[Dict[str, Any]]:
        """
        Parses a file and returns a list of page/section dictionaries:
        [{"text": "...", "page_number": 1, "source": "doc.pdf"}, ...]
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        display_name = original_filename or path.name

        if not path.exists():
            raise FileNotFoundError(f"Document file not found at: {file_path}")

        if ext == ".pdf":
            return DocumentLoader._load_pdf(file_path, display_name)
        elif ext == ".docx":
            return DocumentLoader._load_docx(file_path, display_name)
        elif ext in {".txt", ".md"}:
            return DocumentLoader._load_text(file_path, display_name)
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported formats: {', '.join(DocumentLoader.SUPPORTED_EXTENSIONS)}"
            )

    @staticmethod
    def _load_pdf(file_path: str, filename: str) -> List[Dict[str, Any]]:
        pages = []
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            total_pages = len(reader.pages)
            for page_idx in range(total_pages):
                page = reader.pages[page_idx]
                text = page.extract_text() or ""
                clean_text = text.strip()
                if clean_text:
                    pages.append({
                        "text": clean_text,
                        "page_number": page_idx + 1,
                        "source": filename
                    })
        if not pages:
            pages.append({
                "text": "[Empty PDF Document]",
                "page_number": 1,
                "source": filename
            })
        return pages

    @staticmethod
    def _load_docx(file_path: str, filename: str) -> List[Dict[str, Any]]:
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        if not full_text:
            full_text = "[Empty DOCX Document]"
        return [{
            "text": full_text,
            "page_number": 1,
            "source": filename
        }]

    @staticmethod
    def _load_text(file_path: str, filename: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().strip()
        if not text:
            text = "[Empty Document]"
        return [{
            "text": text,
            "page_number": 1,
            "source": filename
        }]
