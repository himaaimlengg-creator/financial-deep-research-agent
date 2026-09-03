# Financial Deep Research Agent

A prototype deep-research system for answering complex
financial questions using structured planning, evidence
collection, verification and synthesis.

The system accepts:

1. A financial research question
2. An optional PDF document

Every successful run generates a structured PDF research
report.

## Architecture

Question + Optional PDF
        |
        v
Input Processing
        |
        v
Research Planner
        |
        v
Evidence Research
        |
        v
Verifier
        |
        v
Synthesizer
        |
        v
PDF Report

## Setup

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create `.env`:

GEMINI_API_KEY=<your-key>

## Run

Question only:

python main.py --question "..."

Question + PDF:

python main.py --question "..." --pdf document.pdf

## Design Decisions

### Why separate planning and research?

Planning reduces premature conclusions and creates explicit
research objectives before evidence gathering.

### Why structured evidence?

Claims remain linked to their source throughout the pipeline,
making verification and final reporting easier.

### Why a verifier?

The verifier looks for unsupported claims, contradictions,
missing evidence and incomplete research before synthesis.

### Why no vector database?

The interview workload involves an optional document rather
than a large persistent document collection. Adding a vector
database would increase complexity without enough benefit.

## Known Limitations

- Scanned PDFs require OCR support.
- PDF context is currently bounded by a context-size limit.
- Financial numerical calculations are not independently
  executed or reconciled.
- Source quality assessment is basic.
- Research iteration is intentionally bounded.


