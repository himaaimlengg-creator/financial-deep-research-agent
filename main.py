import argparse
import sys

from app.pipeline import DeepResearchPipeline


def main():

    parser = argparse.ArgumentParser(
        description="Financial Deep Research Agent"
    )

    parser.add_argument(
        "--question",
        required=True,
        help="Financial research question",
    )

    parser.add_argument(
        "--pdf",
        required=False,
        help="Optional PDF document",
    )

    parser.add_argument(
        "--output",
        default="outputs/research_report.pdf",
        help="Output PDF path",
    )

    args = parser.parse_args()

    try:

        pipeline = DeepResearchPipeline()

        pipeline.run(
            question=args.question,
            pdf_path=args.pdf,
            output_path=args.output,
        )

    except Exception as exc:

        print(
            f"\nResearch failed: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()


