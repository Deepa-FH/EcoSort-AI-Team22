"""Subsystem 3 - Recycling Rules & Ask AI (owner: Mayuresh Kumbhar)."""
from .ai_assistant import WasteAssistant
from .default_rules import DEFAULT_RULES
from .exceptions import (InvalidRuleError, LLMServiceError, MissingAPIKeyError, RecyclingAIError,
                         RecyclingAIErrorHandler, UnknownMaterialError)
from .fallback_responses import FallbackResponder
from .guidance_response import SOURCE_LLM, SOURCE_LOCAL, GuidanceResponse
from .llm_client import OpenAICompatibleClient
from .prompt_builder import PromptBuilder
from .recycling_rule import RecyclingRule
from .recycling_rules import RecyclingRuleEngine
from .rule_store import InMemoryRuleStore, RuleStore

__all__ = [
    "WasteAssistant", "DEFAULT_RULES", "RecyclingRule", "RecyclingRuleEngine", "RuleStore",
    "InMemoryRuleStore", "PromptBuilder", "OpenAICompatibleClient", "FallbackResponder",
    "GuidanceResponse", "SOURCE_LLM", "SOURCE_LOCAL", "RecyclingAIError", "LLMServiceError",
    "MissingAPIKeyError", "UnknownMaterialError", "InvalidRuleError", "RecyclingAIErrorHandler",
]
