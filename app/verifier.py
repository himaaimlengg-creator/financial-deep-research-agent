import json

from app.gemini_client import GeminiClient
from app.models import (
    TaskResult,
    VerificationResult,
)


class ResearchVerifier:

    def __init__(self):
        self.llm = GeminiClient()

    def verify(
        self,
        question: str,
        results: list[TaskResult],
    ) -> VerificationResult:

        evidence = "\n\n".join(
            result.model_dump_json(indent=2)
            for result in results
        )

        prompt = f"""
You are the verification component of a financial
deep-research system.

ORIGINAL QUESTION:
{question}

COLLECTED RESEARCH:
{evidence}

Your job is NOT to answer the original question.

Evaluate whether the collected research is sufficient,
balanced, supported, and internally consistent.

Check:

1. Are important conclusions supported by evidence?
2. Are there conflicting claims or evidence?
3. Are any important claims unsupported?
4. Is an important perspective missing?
5. Is additional research required?
6. Is uncertainty being hidden?

IMPORTANT OUTPUT RULES:

- unsupported_claims must contain strings only.
- conflicts must contain strings only.
- notes must contain strings only.
- missing_research must contain objects with:
  area, reason, and research_question.
- Return empty arrays when nothing is found.
- Return ONLY valid JSON.
- Do not include markdown fences.

Use exactly this JSON structure:

{{
  "passed": true,
  "unsupported_claims": [
    "Description of unsupported claim"
  ],
  "conflicts": [
    "Description of conflicting evidence"
  ],
  "missing_research": [
    {{
      "area": "Area requiring more evidence",
      "reason": "Why current evidence is insufficient",
      "research_question": "Specific follow-up question"
    }}
  ],
  "notes": [
    "Additional verification observation"
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

        return VerificationResult.model_validate(data)


