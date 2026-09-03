from pathlib import Path

from pypdf import PdfReader

from app.models import DocumentChunk


def parse_pdf(path: str) -> list[DocumentChunk]:
    """
    Read a PDF file and extract text page by page.

    We intentionally preserve the page number because
    financial research questions may reference a specific
    page in the supplied document.
    """

    pdf_path = Path(path)

    # Make sure the supplied PDF actually exists.
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    # Open and read the PDF.
    reader = PdfReader(str(pdf_path))

    chunks: list[DocumentChunk] = []

    # Extract text separately from every page.
    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""

        text = text.strip()

        # Ignore pages that contain no extractable text.
        if not text:
            continue

        chunks.append(
            DocumentChunk(
                page=page_number,
                text=text,
            )
        )

    # If nothing could be extracted, fail clearly instead
    # of silently passing an empty document downstream.
    if not chunks:
        raise ValueError(
            "The PDF contained no extractable text."
        )

    return chunks


def build_pdf_context(
    chunks: list[DocumentChunk],
    max_chars: int = 50000,
) -> str:
    """
    Convert extracted PDF pages into bounded text context
    that can be supplied to the research agent.

    Page markers are preserved so the model can reference
    evidence back to its original PDF page.
    """

    sections: list[str] = []
    current_size = 0

    for chunk in chunks:

        # Preserve page information in the context.
        section = (
            f"\n--- PDF PAGE {chunk.page} ---\n"
            f"{chunk.text}\n"
        )

        # Prevent an unexpectedly large PDF from consuming
        # unlimited model context.
        if current_size + len(section) > max_chars:
            break

        sections.append(section)

        current_size += len(section)

    return "".join(sections)
