"""Strict local validation for model-produced JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from .protocol import RECOMMENDATION_CATEGORIES


CONCLUSIONS = {"A", "B", "Genuinely indeterminate"}


class OutputValidationError(ValueError):
    """Raised when model output violates the approved output contract."""


def extract_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OutputValidationError(f"Invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise OutputValidationError("Top-level output must be a JSON object")
    return value


def _exact_keys(value: dict[str, Any], required: set[str], context: str) -> None:
    missing = required - value.keys()
    extra = value.keys() - required
    if missing or extra:
        raise OutputValidationError(
            f"{context} keys differ; missing={sorted(missing)}, extra={sorted(extra)}"
        )


def _integer_0_100(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise OutputValidationError(f"{field} must be an integer from 0 to 100")
    return value


def _validate_probabilities(value: Any, field: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise OutputValidationError(f"{field} must be an object")
    keys = {"A", "B", "Genuinely_indeterminate"}
    _exact_keys(value, keys, field)
    probabilities = {key: _integer_0_100(value[key], f"{field}.{key}") for key in keys}
    if sum(probabilities.values()) != 100:
        raise OutputValidationError(f"{field} must sum to 100")
    return probabilities


def _validate_evidence(items: Any, allowed_fact_ids: set[str], field: str, text_key: str) -> list[dict]:
    if not isinstance(items, list):
        raise OutputValidationError(f"{field} must be an array")
    checked: list[dict] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise OutputValidationError(f"{field}[{index}] must be an object")
        _exact_keys(item, {"fact_id", text_key}, f"{field}[{index}]")
        if item["fact_id"] not in allowed_fact_ids:
            raise OutputValidationError(f"Unknown fact ID in {field}: {item['fact_id']}")
        if not isinstance(item[text_key], str) or not item[text_key].strip():
            raise OutputValidationError(f"{field}[{index}].{text_key} must be non-empty")
        checked.append(item)
    return checked


def _validate_recommendation(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise OutputValidationError(f"{field} must be an object")
    _exact_keys(value, {"category", "explanation"}, field)
    if value["category"] not in RECOMMENDATION_CATEGORIES:
        raise OutputValidationError(f"Invalid recommendation category: {value['category']}")
    if not isinstance(value["explanation"], str) or not value["explanation"].strip():
        raise OutputValidationError(f"{field}.explanation must be non-empty")
    return value


def validate_initial(value: dict[str, Any], allowed_fact_ids: set[str]) -> dict[str, Any]:
    keys = {
        "most_likely_interpretation",
        "confidence",
        "probabilities",
        "evidence_supporting",
        "evidence_against",
        "recommended_action",
        "uncertainty_explanation",
    }
    _exact_keys(value, keys, "initial output")
    if value["most_likely_interpretation"] not in CONCLUSIONS:
        raise OutputValidationError("Invalid initial conclusion")
    _integer_0_100(value["confidence"], "confidence")
    _validate_probabilities(value["probabilities"], "probabilities")
    _validate_evidence(value["evidence_supporting"], allowed_fact_ids, "evidence_supporting", "relevance")
    _validate_evidence(value["evidence_against"], allowed_fact_ids, "evidence_against", "relevance")
    _validate_recommendation(value["recommended_action"], "recommended_action")
    if not isinstance(value["uncertainty_explanation"], str) or not value["uncertainty_explanation"].strip():
        raise OutputValidationError("uncertainty_explanation must be non-empty")
    return value


def validate_revision(
    value: dict[str, Any], allowed_fact_ids: set[str], challenge_ids: set[str]
) -> dict[str, Any]:
    keys = {
        "revised_most_likely_interpretation",
        "revised_confidence",
        "revised_probabilities",
        "challenge_facts_addressed",
        "reason_for_retaining_or_changing",
        "revised_recommended_action",
    }
    _exact_keys(value, keys, "revision output")
    if value["revised_most_likely_interpretation"] not in CONCLUSIONS:
        raise OutputValidationError("Invalid revised conclusion")
    _integer_0_100(value["revised_confidence"], "revised_confidence")
    _validate_probabilities(value["revised_probabilities"], "revised_probabilities")
    addressed = _validate_evidence(
        value["challenge_facts_addressed"],
        allowed_fact_ids,
        "challenge_facts_addressed",
        "effect_on_judgment",
    )
    non_challenge = {item["fact_id"] for item in addressed} - challenge_ids
    if non_challenge:
        raise OutputValidationError(
            f"challenge_facts_addressed contains non-challenge IDs: {sorted(non_challenge)}"
        )
    if not isinstance(value["reason_for_retaining_or_changing"], str) or not value[
        "reason_for_retaining_or_changing"
    ].strip():
        raise OutputValidationError("reason_for_retaining_or_changing must be non-empty")
    _validate_recommendation(value["revised_recommended_action"], "revised_recommended_action")
    return value

