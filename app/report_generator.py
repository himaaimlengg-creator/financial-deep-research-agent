from pathlib import Path
from collections import OrderedDict
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)

from app.models import FinalReport


def _clean_text(text: str) -> str:
    """
    Escape special characters before sending text
    to ReportLab's Paragraph parser.
    """
    return escape(str(text).strip())


def _add_bullet_list(
    story,
    items: list[str],
    body_style,
):
    """
    Add a consistently formatted bullet list.
    """
    for item in items:
        if not item:
            continue

        story.append(
            Paragraph(
                f"• {_clean_text(item)}",
                body_style,
            )
        )

        story.append(Spacer(1, 5))


def _add_analysis_paragraphs(
    story,
    analysis: str,
    body_style,
):
    """
    Break long analysis text into readable paragraphs.

    If the model already returns multiple paragraphs,
    preserve those boundaries. If it returns one very
    large paragraph, split it into smaller sentence
    groups for readability.
    """
    if not analysis:
        return

    paragraphs = [
        paragraph.strip()
        for paragraph in analysis.split("\n")
        if paragraph.strip()
    ]

    # Gemini sometimes returns the entire analysis
    # as one large paragraph.
    if len(paragraphs) == 1:
        text = paragraphs[0]

        sentences = (
            text.replace("? ", "?\n")
            .replace("! ", "!\n")
            .replace(". ", ".\n")
            .split("\n")
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        # Group approximately 4 sentences per paragraph.
        paragraphs = []

        for index in range(0, len(sentences), 4):
            group = " ".join(
                sentences[index:index + 4]
            )
            paragraphs.append(group)

    for paragraph in paragraphs:
        story.append(
            Paragraph(
                _clean_text(paragraph),
                body_style,
            )
        )

        story.append(Spacer(1, 8))


def _deduplicate_sources(sources):
    """
    Merge repeated references to the same source.

    Example:
        Northstar Report — page 1
        Northstar Report — page 2
        Northstar Report — page 1, 3

    becomes:
        Northstar Report — pages 1, 2, 3
    """
    grouped = OrderedDict()

    for source in sources:
        key = (
            source.title.strip(),
            (source.url or "").strip(),
        )

        if key not in grouped:
            grouped[key] = {
                "title": source.title.strip(),
                "url": (
                    source.url.strip()
                    if source.url
                    else None
                ),
                "pages": set(),
            }

        if source.page:
            page_text = str(source.page)

            # Accept page values such as:
            # "1"
            # "1, 2"
            # "2-3"
            for page in page_text.split(","):
                page = page.strip()

                if page:
                    grouped[key]["pages"].add(page)

    return list(grouped.values())


def generate_pdf(
    report: FinalReport,
    output_path: str,
):
    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=report.title,
        author="Financial Deep Research Agent",
    )

    styles = getSampleStyleSheet()

    # -------------------------------------------------
    # Custom styles
    # -------------------------------------------------

    title_style = ParagraphStyle(
        "ResearchTitle",
        parent=styles["Title"],
        fontSize=19,
        leading=23,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=17,
        spaceBefore=8,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ResearchBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=4,
    )

    question_style = ParagraphStyle(
        "QuestionBody",
        parent=body_style,
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )

    source_style = ParagraphStyle(
        "SourceBody",
        parent=body_style,
        fontSize=9,
        leading=12,
        leftIndent=8,
    )

    story = []

    # -------------------------------------------------
    # TITLE
    # -------------------------------------------------

    story.append(
        Paragraph(
            _clean_text(report.title),
            title_style,
        )
    )

    # -------------------------------------------------
    # RESEARCH QUESTION
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Research Question",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            _clean_text(report.question),
            question_style,
        )
    )

    story.append(Spacer(1, 8))

    # -------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Executive Summary",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            _clean_text(report.executive_summary),
            body_style,
        )
    )

    story.append(Spacer(1, 10))

    # -------------------------------------------------
    # KEY FINDINGS
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Key Findings",
            heading_style,
        )
    )

    _add_bullet_list(
        story,
        report.key_findings,
        body_style,
    )

    story.append(Spacer(1, 8))

    # -------------------------------------------------
    # DETAILED ANALYSIS
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Detailed Analysis",
            heading_style,
        )
    )

    _add_analysis_paragraphs(
        story,
        report.detailed_analysis,
        body_style,
    )

    # -------------------------------------------------
    # CONFLICTING EVIDENCE
    # -------------------------------------------------

    if report.conflicting_evidence:
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Conflicting Evidence",
                heading_style,
            )
        )

        _add_bullet_list(
            story,
            report.conflicting_evidence,
            body_style,
        )

    # -------------------------------------------------
    # LIMITATIONS
    # -------------------------------------------------

    if report.limitations:
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Limitations",
                heading_style,
            )
        )

        _add_bullet_list(
            story,
            report.limitations,
            body_style,
        )

    # -------------------------------------------------
    # FINAL SYNTHESIS
    # -------------------------------------------------

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "Final Synthesis",
            heading_style,
        )
    )

    _add_analysis_paragraphs(
        story,
        report.final_synthesis,
        body_style,
    )

    # -------------------------------------------------
    # SOURCES
    # -------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Sources",
            heading_style,
        )
    )

    unique_sources = _deduplicate_sources(
        report.sources
    )

    if not unique_sources:
        story.append(
            Paragraph(
                "No source metadata was available.",
                body_style,
            )
        )

    for index, source in enumerate(
        unique_sources,
        start=1,
    ):
        parts = [
            f"{index}. {_clean_text(source['title'])}"
        ]

        pages = sorted(source["pages"])

        if pages:
            page_label = (
                "page"
                if len(pages) == 1
                else "pages"
            )

            parts.append(
                f"{page_label} "
                f"{', '.join(_clean_text(p) for p in pages)}"
            )

        if source["url"]:
            parts.append(
                _clean_text(source["url"])
            )

        source_text = " — ".join(parts)

        story.append(
            KeepTogether(
                [
                    Paragraph(
                        source_text,
                        source_style,
                    ),
                    Spacer(1, 7),
                ]
            )
        )

    doc.build(story)


