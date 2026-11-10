"""Live demo for Subsystem 3.   Run:  python -m subsystem_3_recycling_ai.demo [--api-key KEY]

Without a key it shows the local-rule fallback; with a key it also asks the real LLM.
"""

import argparse
import os

from .ai_assistant import WasteAssistant
from .exceptions import MissingAPIKeyError, RecyclingAIErrorHandler
from .llm_client import OpenAICompatibleClient
from .recycling_rules import RecyclingRuleEngine
from .rule_store import InMemoryRuleStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY"))
    parser.add_argument("--llm-model", default=os.environ.get("LLM_MODEL", "mistralai-mistral-small-4"))
    parser.add_argument("--llm-base-url", default=os.environ.get("LLM_BASE_URL", "https://chat.kiconnect.nrw/api/v1"))
    args = parser.parse_args()

    engine = RecyclingRuleEngine(InMemoryRuleStore())
    client = OpenAICompatibleClient(args.api_key, args.llm_model, args.llm_base_url)
    assistant = WasteAssistant(engine, client)

    print("Client           :", client)                      # key is never printed
    print("Rule for Papier  :", engine.get("Papier").bin, "/", engine.get("Papier").bin_de)
    print("Unknown label    :", engine.get("Banana"))
    detections = [{"label": "Plastic", "confidence": 0.42}]
    review = assistant.review_detection(detections)
    print(f"\nReview (source={review.source}):\n{review.answer}")
    if review.notice:
        print("Notice           :", review.notice)
    print("\nError handler    :", RecyclingAIErrorHandler().handle(MissingAPIKeyError()).to_dict())


if __name__ == "__main__":
    main()
