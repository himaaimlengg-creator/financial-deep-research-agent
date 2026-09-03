import pytest
from pydantic import ValidationError

from app.models import Source, Evidence


def test_evidence_model():
    source = Source(
        title="Northstar Annual Report",
        source_type="financial_report",
        page="12",
    )

    evidence = Evidence(
        claim="Revenue increased.",
        evidence="Revenue increased 28% year over year.",
        source=source,
        confidence=0.9,
    )

    assert evidence.claim == "Revenue increased."
    assert evidence.source.page == "12"
    assert evidence.confidence == 0.9


def test_confidence_cannot_exceed_one():
    source = Source(
        title="Test Source",
        source_type="pdf",
    )

    with pytest.raises(ValidationError):
        Evidence(
            claim="Test claim",
            evidence="Test evidence",
            source=source,
            confidence=1.5,
        )


