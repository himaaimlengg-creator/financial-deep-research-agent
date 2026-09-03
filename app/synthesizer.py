from app.gemini_client import GeminiClient
from app.models import (
    FinalReport,
    TaskResult,
    VerificationResult,
)


class Synthesizer:

    def __init__(self):
        self.llm = GeminiClient()

    def synthesize(
        self,
        question: str,
        research: list[TaskResult],
        verification: VerificationResult,
    ) -> FinalReport:

        research_json = "\n\n".join(
            item.model_dump_json(indent=2)
            for item in research
        )

        verification_json = (
            verification.model_dump_json(indent=2)
        )

        prompt = f"""
You are the final synthesis component of a
financial deep-research system.

ORIGINAL QUESTION:

{question}


COLLECTED RESEARCH:

{research_json}


VERIFICATION RESULTS:

{verification_json}


Create a balanced, evidence-driven financial
research report.

Follow these rules carefully:

1. Answer the original research question directly.

2. Use only facts supported by the supplied research.

3. Do not invent financial numbers, dates, sources,
   quotations, or URLs.

4. Clearly distinguish factual evidence from
   interpretation.

5. Include material conflicting evidence.

6. Be transparent about uncertainty and missing
   information.

7. If verification identified missing research,
   mention that under limitations.

8. Do not present uncertain conclusions as facts.

9. The executive summary should be concise but useful.

10. Detailed analysis should explain the reasoning
    behind the findings.

11. Final synthesis should answer what the available
    evidence reasonably supports, rather than forcing
    a bullish or bearish conclusion.

12. Preserve source titles, URLs and page references
    from the supplied research whenever available.
"""

        return self.llm.generate_structured(
            prompt=prompt,
            schema=FinalReport,
        )


