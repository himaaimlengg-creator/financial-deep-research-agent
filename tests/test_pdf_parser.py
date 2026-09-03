import pytest

from app.pdf_parser import parse_pdf


def test_missing_pdf():
    with pytest.raises(FileNotFoundError):
        parse_pdf("does_not_exist.pdf")


def test_sample_pdf_extracts_pages():
    chunks = parse_pdf("samples/sample_input.pdf")

    assert len(chunks) > 0
    assert chunks[0].page == 1
    assert len(chunks[0].text) > 0

    combined_text = " ".join(
        chunk.text for chunk in chunks
    )

    assert "Northstar Compute Systems" in combined_text


