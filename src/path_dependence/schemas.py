"""Strict local validation for Phase 1C model-produced JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from .protocol import RECOMMENDATION_CATEGORIES


CONCLUSIONS = {"A", "B", "genuinely_indeterminate"}


class OutputValidationError(ValueError):
    """Raised when model output violates the frozen response contract."""


def extract_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    fenced = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE
    )
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


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OutputValidationError(f"{field} must be a non-empty string")
    return value


def _validate_probabilities(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        raise OutputValidationError("probabilities must be an object")
    keys = {"A", "B", "indeterminate"}
    _exact_keys(value, keys, "probabilities")
    probabilities = {
        key: _integer_0_100(value[key], f"probabilities.{key}") for key in keys
    }
    if sum(probabilities.values()) != 100:
        raise OutputValidationError("probabilities must sum to 100")
    return probabilities


def _validate_evidence(
    items: Any, allowed_fact_ids: set[str], field: str
) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        raise OutputValidationError(f"{field} must be an array")
    checked: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise OutputValidationError(f"{field}[{index}] must be an object")
        _exact_keys(item, {"fact_id", "explanation"}, f"{field}[{index}]")
        fact_id = item["fact_id"]
        if fact_id is not None and fact_id not in allowed_fact_ids:
            raise OutputValidationError(f"Unknown or unavailable fact ID in {field}: {fact_id}")
        _nonempty_string(item["explanation"], f"{field}[{index}].explanation")
        checked.append(item)
    return checked


def _validate_recommendation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OutputValidationError("recommendation must be an object")
    _exact_keys(value, {"category", "intensity", "explanation"}, "recommendation")
    if value["category"] not in RECOMMENDATION_CATEGORIES:
        raise OutputValidationError(f"Invalid recommendation category: {value['category']}")
    intensity = value["intensity"]
    if isinstance(intensity, bool) or not isinstance(intensity, int) or intensity not in (0, 1, 2):
        raise OutputValidationError("recommendation.intensity must be 0, 1, or 2")
    _nonempty_string(value["explanation"], "recommendation.explanation")
    return value


def validate_assessment(
    value: dict[str, Any], allowed_fact_ids: set[str]
) -> dict[str, Any]:
    keys = {
        "pre_reassessment_text",
        "most_likely_interpretation",
        "probabilities",
        "confidence",
        "evidence_supporting_most_likely",
        "evidence_against_most_likely",
        "recommendation",
    }
    _exact_keys(value, keys, "assessment output")
    _nonempty_string(value["pre_reassessment_text"], "pre_reassessment_text")
    if value["most_likely_interpretation"] not in CONCLUSIONS:
        raise OutputValidationError("Invalid most_likely_interpretation")
    _validate_probabilities(value["probabilities"])
    _integer_0_100(value["confidence"], "confidence")
    _validate_evidence(
        value["evidence_supporting_most_likely"],
        allowed_fact_ids,
        "evidence_supporting_most_likely",
    )
    _validate_evidence(
        value["evidence_against_most_likely"],
        allowed_fact_ids,
        "evidence_against_most_likely",
    )
    _validate_recommendation(value["recommendation"])
    return value
