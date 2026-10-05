"""Manifest creation and explicitly gated Phase 1C trajectory execution."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .protocol import (
    CONDITIONS,
    ORIGINAL_FACTS,
    TURNS,
    SYSTEM_PROMPT,
    available_fact_ids,
    available_new_fact_ids,
    planned_user_turns,
    user_prompt,
)
from .provider import ModelProvider, OpenAIResponsesProvider
from .schemas import extract_json, validate_assessment
from .storage import ensure_output_tree, read_json, write_csv, write_json, write_jsonl
from .validation import assert_protocol_valid


@dataclass(frozen=True)
class ExperimentConfig:
    provider: str
    model: str
    reasoning_effort: str
    temperature: float | None
    top_p: float | None
    max_output_tokens: int
    replicates: int
    seed: int | None
    randomization_seed: int
    output_root: str
    base_url: str

    @classmethod
    def from_path(cls, path: Path) -> "ExperimentConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        required = {field.name for field in cls.__dataclass_fields__.values()}
        missing = required - value.keys()
        extra = value.keys() - required
        if missing or extra:
            raise ValueError(
                f"Config keys differ; missing={sorted(missing)}, extra={sorted(extra)}"
            )
        config = cls(**value)
        if config.replicates != 10:
            raise ValueError("Approved Phase 1C design requires exactly ten trajectories per condition")
        if config.model != "gpt-5.6-sol":
            raise ValueError("Phase 1C preserves the gpt-5.6-sol model configuration")
        if config.reasoning_effort != "none":
            raise ValueError('Approved configuration requires reasoning_effort="none"')
        if config.temperature != 0:
            raise ValueError("Approved configuration requires temperature=0")
        if config.top_p != 1:
            raise ValueError("Approved configuration requires top_p=1")
        if config.provider != "openai_responses":
            raise ValueError("Only the explicitly implemented openai_responses provider is supported")
        if config.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        return config


def _execution_scope(
    config: ExperimentConfig,
    *,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> tuple[list[str], int]:
    selected_conditions = list(CONDITIONS) if condition_ids is None else list(condition_ids)
    selected_replicates = config.replicates if replicates is None else replicates
    unknown = set(selected_conditions) - set(CONDITIONS)
    if unknown:
        raise ValueError(f"Unknown condition IDs: {sorted(unknown)}")
    if len(selected_conditions) != len(set(selected_conditions)):
        raise ValueError("Condition IDs must not be repeated")
    if not 1 <= selected_replicates <= config.replicates:
        raise ValueError(f"replicates must be between 1 and {config.replicates}")
    return selected_conditions, selected_replicates


def build_manifest(
    config: ExperimentConfig,
    *,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> list[dict[str, Any]]:
    assert_protocol_valid()
    selected_conditions, selected_replicates = _execution_scope(
        config, condition_ids=condition_ids, replicates=replicates
    )
    rows: list[dict[str, Any]] = []
    for condition_id in selected_conditions:
        condition = CONDITIONS[condition_id]
        for replicate in range(1, selected_replicates + 1):
            rows.append(
                {
                    "run_id": f"C_{condition_id}_r{replicate:02d}",
                    "case_id": "C",
                    "condition": condition_id,
                    "condition_label": condition.label,
                    "basis_instruction": condition.basis_instruction,
                    "receives_new_external_facts": condition.receives_new_external_facts,
                    "replicate": replicate,
                    "planned_turns": len(TURNS),
                    "planned_model_responses": len(TURNS),
                    "model": config.model,
                    "reasoning_effort": config.reasoning_effort,
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "max_output_tokens": config.max_output_tokens,
                    "seed": config.seed,
                    "approved_decoding": (
                        config.reasoning_effort == "none"
                        and config.temperature == 0
                        and config.top_p == 1
                    ),
                }
            )
    random.Random(config.randomization_seed).shuffle(rows)
    for execution_order, row in enumerate(rows, start=1):
        row["execution_order"] = execution_order
    return rows


def write_manifest(
    config: ExperimentConfig,
    output_dir: Path,
    *,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> tuple[Path, Path]:
    manifest = build_manifest(
        config, condition_ids=condition_ids, replicates=replicates
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "run_manifest.jsonl"
    csv_path = output_dir / "run_manifest.csv"
    write_jsonl(jsonl_path, manifest)
    write_csv(csv_path, manifest)
    planned = [
        {
            "run_id": row["run_id"],
            "condition": row["condition"],
            "system_prompt": SYSTEM_PROMPT,
            "user_turns": planned_user_turns(row["condition"]),
            "assistant_turn_placeholders": [f"T{turn}" for turn in TURNS],
        }
        for row in manifest
    ]
    write_jsonl(output_dir / "planned_conversations.jsonl", planned)
    return jsonl_path, csv_path


def provider_from_config(config: ExperimentConfig) -> ModelProvider:
    return OpenAIResponsesProvider(
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
        base_url=config.base_url,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _message_sha256(messages: list[dict[str, str]]) -> str:
    encoded = json.dumps(messages, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def execute(
    config: ExperimentConfig,
    *,
    paid_api_confirmed: bool,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> None:
    if not paid_api_confirmed:
        raise RuntimeError("Execution blocked: pass --execute-paid-api explicitly")
    assert_protocol_valid()
    paths = ensure_output_tree(Path(config.output_root))
    manifest = build_manifest(
        config, condition_ids=condition_ids, replicates=replicates
    )
    write_manifest(
        config,
        paths["manifests"],
        condition_ids=condition_ids,
        replicates=replicates,
    )
    provider = provider_from_config(config)

    for run in manifest:
        run_id = run["run_id"]
        condition = run["condition"]
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(condition, 0)},
        ]
        prior_assistant_turns: list[str] = []

        for turn in TURNS:
            turn_id = f"T{turn}"
            raw_path = paths["raw"] / f"{run_id}_{turn_id}.json"
            parsed_path = paths["parsed"] / f"{run_id}_{turn_id}.json"

            if raw_path.exists() and parsed_path.exists():
                raw = read_json(raw_path)
                output_text = raw["output_text"]
            else:
                started = _utc_now()
                result = provider.generate(messages)
                finished = _utc_now()
                output_text = result.output_text
                raw = {
                    "run": run,
                    "turn": turn,
                    "turn_id": turn_id,
                    "started_at": started,
                    "finished_at": finished,
                    "request_messages": messages,
                    "request_message_sha256": _message_sha256(messages),
                    "prior_assistant_turns": list(prior_assistant_turns),
                    "available_original_fact_ids": sorted(ORIGINAL_FACTS),
                    "available_new_fact_ids": sorted(
                        available_new_fact_ids(condition, turn)
                    ),
                    "response_id": result.response_id,
                    "output_text": output_text,
                    "response_body": result.response_body,
                }
                write_json(raw_path, raw)
                parsed = validate_assessment(
                    extract_json(output_text), available_fact_ids(condition, turn)
                )
                parsed.update(
                    {
                        "_turn": turn,
                        "_turn_id": turn_id,
                        "_prior_assistant_turns": list(prior_assistant_turns),
                        "_available_original_fact_ids": sorted(ORIGINAL_FACTS),
                        "_available_new_fact_ids": sorted(
                            available_new_fact_ids(condition, turn)
                        ),
                        "_request_message_sha256": _message_sha256(messages),
                    }
                )
                write_json(parsed_path, parsed)

            messages.append({"role": "assistant", "content": output_text})
            prior_assistant_turns.append(turn_id)
            if turn < TURNS[-1]:
                messages.append(
                    {"role": "user", "content": user_prompt(condition, turn + 1)}
                )
