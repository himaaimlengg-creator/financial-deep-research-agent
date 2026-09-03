from app.pdf_parser import parse_pdf, build_pdf_context
from app.planner import ResearchPlanner
from app.researcher import Researcher
from app.verifier import ResearchVerifier
from app.synthesizer import Synthesizer
from app.report_generator import generate_pdf
from app.models import ResearchTask


class DeepResearchPipeline:
    def __init__(self):
        self.planner = ResearchPlanner()
        self.researcher = Researcher()
        self.verifier = ResearchVerifier()
        self.synthesizer = Synthesizer()

    def run(
        self,
        question: str,
        pdf_path: str | None = None,
        output_path: str = "outputs/research_report.pdf",
    ):
        print("[1/5] Processing input...")

        # Optional PDF context
        pdf_context = None

        if pdf_path:
            chunks = parse_pdf(pdf_path)
            pdf_context = build_pdf_context(chunks)
            print(f"Loaded {len(chunks)} PDF pages.")

        # -------------------------------------------------
        # 1. PLAN
        # -------------------------------------------------
        print("[2/5] Planning research...")

        plan = self.planner.create_plan(
            question=question,
            pdf_context=pdf_context,
        )

        print(f"Created {len(plan.tasks)} research tasks.")

        # -------------------------------------------------
        # 2. INITIAL RESEARCH
        # -------------------------------------------------
        print("[3/5] Gathering evidence...")

        research_results = []

        for task in plan.tasks:
            print(f"Researching: {task.question}")

            result = self.researcher.research(
                task=task,
                pdf_context=pdf_context,
            )

            research_results.append(result)

        # -------------------------------------------------
        # 3. VERIFY
        # -------------------------------------------------
        print("[4/5] Verifying evidence...")

        verification = self.verifier.verify(
            question=question,
            results=research_results,
        )

        print(f"Verification passed: {verification.passed}")

        # -------------------------------------------------
        # 4. TARGETED FOLLOW-UP RESEARCH
        # -------------------------------------------------
        # If verification finds important evidence gaps,
        # perform one bounded follow-up research pass.
        #
        # We intentionally allow only one retry so the
        # workflow cannot enter an uncontrolled agent loop.
        # -------------------------------------------------

        if not verification.passed and verification.missing_research:
            total_gaps = len(verification.missing_research)

            # Keep the retry bounded to avoid uncontrolled
            # latency and API cost.
            follow_up_items = verification.missing_research[:3]

            print(
                f"Verifier identified {total_gaps} evidence gap(s); "
                f"executing {len(follow_up_items)} bounded "
                f"follow-up research task(s)."
            )

            for index, missing in enumerate(
                follow_up_items,
                start=1,
            ):
                follow_up_question = (
                    missing.research_question
                    or missing.area
                )

                print(
                    f"Follow-up research: "
                    f"{follow_up_question}"
                )

                follow_up_task = ResearchTask(
                    id=f"follow_up_{index}",
                    question=follow_up_question,
                    purpose=(
                        "Resolve an evidence gap identified "
                        "by the verification stage. "
                        f"Reason: {missing.reason}"
                    ),
                    priority=1,
                )

                follow_up_result = self.researcher.research(
                    task=follow_up_task,
                    pdf_context=pdf_context,
                )

                research_results.append(follow_up_result)

            # Re-run verification using both the original
            # and follow-up evidence.
            print("Re-verifying after follow-up research...")

            verification = self.verifier.verify(
                question=question,
                results=research_results,
            )

            print(
                "Verification after follow-up: "
                f"{verification.passed}"
            )

        # -------------------------------------------------
        # 5. SYNTHESIZE
        # -------------------------------------------------
        print("[5/5] Synthesizing report...")

        report = self.synthesizer.synthesize(
            question=question,
            research=research_results,
            verification=verification,
        )

        generate_pdf(
            report=report,
            output_path=output_path,
        )

        print("\nResearch completed.")
        print(f"Report: {output_path}")

        return report


