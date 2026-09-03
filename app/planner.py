import json

from app.gemini_client import GeminiClient
from app.models import ResearchPlan


class ResearchPlanner:

    def __init__(self):
        self.llm = GeminiClient()

    def create_plan(
        self,
        question: str,
        pdf_context: str | None = None,
    ) -> ResearchPlan:

        document_instruction = ""

        if pdf_context:
            document_instruction = """
The user has also supplied a PDF.
Create research tasks that use the document when
relevant, but do not assume the document alone is
sufficient evidence.
"""

        prompt = f"""
You are the planning component of a financial
deep-research system.

USER QUESTION:
{question}

{document_instruction}

Break this question into 3 to 6 focused research
tasks required to produce a balanced and defensible
answer.

Cover multiple perspectives where appropriate.
Do not answer the question yet.

Return ONLY valid JSON using exactly this shape:

{{
  "original_question": "...",
  "tasks": [
    {{
      "id": "task_1",
      "question": "...",
      "purpose": "...",
      "priority": 1
    }}
  ]
}}
"""

        raw = self.llm.generate(prompt)

        raw = (
            raw.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(raw)

        return ResearchPlan.model_validate(data)


