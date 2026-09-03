import json

from app.gemini_client import GeminiClient
from app.models import ResearchTask, TaskResult


class Researcher:
    """
    Research worker responsible for gathering evidence
    for one research task at a time.
    """

    def __init__(self):
        self.llm = GeminiClient()

    def research(
        self,
        task: ResearchTask,
        pdf_context: str | None = None,
    ) -> TaskResult:

        document_section = ""

        if pdf_context:
            document_section = f"""
OPTIONAL USER-SUPPLIED DOCUMENT:

{pdf_context}

The PDF is additional context.

Use information from the PDF when it is relevant to
the research task.

When using PDF evidence, preserve the page number
from the PDF PAGE markers.
"""

        prompt = f"""
You are a careful financial research analyst.

RESEARCH TASK:
{task.question}

PURPOSE:
{task.purpose}

{document_section}

Research this task carefully.

Follow these rules:

1. Separate evidence from interpretation.
2. Do not invent financial numbers or facts.
3. If evidence is uncertain, clearly say so.
4. Preserve available source information.
5. Consider evidence that may disagree with the
   apparent conclusion.
6. If PDF evidence is used, include its page number.
7. Do not make unsupported claims.
8. For page information, return it as a string, for example
   "12", "12-15", or "12, 17". Use null when unavailable.


Return ONLY valid JSON using this exact structure:

{{
  "task_id": "{task.id}",
  "question": "{task.question}",
  "findings": [
    {{
      "claim": "A factual or analytical finding",
      "evidence": "Evidence supporting the finding",
      "source": {{
        "title": "Source title",
        "source_type": "web, pdf, sec_filing, transcript, presentation, or another descriptive source type",
        "url": null,
        "page": null
        }}

      "confidence": 0.8
    }}
  ]
}}
"""

        raw = self.llm.generate(prompt)

        # Gemini sometimes wraps JSON inside Markdown.
        raw = (
            raw.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(raw)

        return TaskResult.model_validate(data)


