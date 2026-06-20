import io
import uuid
import logging
from typing import List, Dict, Any
from pypdf import PdfReader
from config import settings

logger = logging.getLogger("RAG.Ingestion.PDFProcessor")

class SimplePDFProcessor:
    """Manages file streams parsing, serialization extraction, and context block chunking."""
    
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_pdf(self, pdf_stream: io.BytesIO) -> str:
        """Extracts text character elements reliably out of in-memory byte strings."""
        try:
            reader = PdfReader(pdf_stream)
            extracted_pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)
            return "\n".join(extracted_pages)
        except Exception as e:
            logger.error(f"Binary portable format deserialization error: {str(e)}")
            raise RuntimeError(f"Failed to read and parse structural layout configurations out of PDF file: {e}")

    def create_chunks(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        """Splits character sequences into overlapping segment blocks using sentence boundary fallbacks."""
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk_slice = text[start:end]

            # Try to break cleanly at sentence ends to maintain structural semantic continuity
            if end < text_length:
                last_period = chunk_slice.rfind(".")
                if last_period != -1 and last_period > (self.chunk_size // 2):
                    end = start + last_period + 1
                    chunk_slice = text[start:end]

            # Eliminate noisy spacing footprints
            normalized_text = " ".join(chunk_slice.split())
            if normalized_text:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": normalized_text,
                    "metadata": {"source": source_filename}
                })

            start = end - self.chunk_overlap
            if start >= text_length or (end >= text_length):
                break

        return chunks