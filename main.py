"""Entry point for the Waste Sorting and Recycling Assistant."""
from __future__ import annotations

import argparse
from pathlib import Path

from recycling_ai.ai_assistant import WasteAssistant
from recycling_ai.llm_client import OpenAICompatibleClient
from recycling_ai.recycling_rules import RecyclingRuleEngine
from web_dashboard.app import create_app
from image_recognition.detector import WasteDetector
from dataset_preprocessing.image_validator import ImageValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the waste sorting assistant.")
    parser.add_argument("--api-key", help="LLM API key; prefer LLM_API_KEY in production")
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--llm-base-url", default="https://api.openai.com/v1")
    parser.add_argument("--model", type=Path, default=Path("models/best_model.pt"))
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    return parser


def create_application(args: argparse.Namespace):
    detector = WasteDetector(args.model, threshold=args.confidence)
    validator = ImageValidator()
    rules = RecyclingRuleEngine.default_rules()
    llm = OpenAICompatibleClient(api_key=args.api_key, model=args.llm_model, base_url=args.llm_base_url)
    assistant = WasteAssistant(rules, llm)
    return create_app(detector, validator, assistant)


def main() -> None:
    args = build_parser().parse_args()
    if not 0 < args.confidence <= 1:
        raise SystemExit("--confidence must be greater than 0 and at most 1")
    app = create_application(args)
    print(f"Waste Sorting Assistant: http://{args.host}:{args.port}", flush=True)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
