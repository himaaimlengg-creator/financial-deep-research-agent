from app.models import Source
from app.report_generator import _deduplicate_sources


def test_source_deduplication():
    sources = [
        Source(
            title="Northstar Annual Report",
            source_type="pdf",
            page="1",
        ),
        Source(
            title="Northstar Annual Report",
            source_type="pdf",
            page="2",
        ),
        Source(
            title="Northstar Annual Report",
            source_type="pdf",
            page="3",
        ),
    ]

    result = _deduplicate_sources(sources)

    assert len(result) == 1
    assert result[0]["title"] == "Northstar Annual Report"
    assert result[0]["pages"] == {"1", "2", "3"}


