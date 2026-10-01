"""Manifest creation and explicitly gated experiment execution."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .protocol import CASES, CONDITIONS, initial_transcript, revision_prompt
from .provider import ModelProvider, OpenAIResponsesProvider
from .schemas import extract_json, validate_initial, validate_revision
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
            raise ValueError(f"Config keys differ; missing={sorted(missing)}, extra={sorted(extra)}")
        config = cls(**value)
        if config.replicates != 5:
            raise ValueError("Approved initial design requires exactly five replicates")
        if config.model != "gpt-5.6-sol":
            raise ValueError("Approved Phase 1 primary model is gpt-5.6-sol")
        if config.reasoning_effort != "none":
            raise ValueError('Approved gpt-5.6-sol configuration requires reasoning_effort="none"')
        if config.temperature is not None and not 0 <= config.temperature <= 2:
            raise ValueError("temperature must be null or between 0 and 2")
        if config.top_p is not None and not 0 < config.top_p <= 1:
            raise ValueError("top_p must be null or in (0, 1]")
        if config.provider != "openai_responses":
            raise ValueError("Only the explicitly implemented openai_responses provider is supported")
        if config.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        return config


def _execution_scope(
    config: ExperimentConfig,
    *,
    case_ids: Sequence[str] | None = None,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> tuple[list[str], list[str], int]:
    selected_cases = list(CASES) if case_ids is None else list(case_ids)
    selected_conditions = list(CONDITIONS) if condition_ids is None else list(condition_ids)
    selected_replicates = config.replicates if replicates is None else replicates
    unknown_cases = set(selected_cases) - set(CASES)
    unknown_conditions = set(selected_conditions) - set(CONDITIONS)
    if unknown_cases:
        raise ValueError(f"Unknown case IDs: {sorted(unknown_cases)}")
    if unknown_conditions:
        raise ValueError(f"Unknown condition IDs: {sorted(unknown_conditions)}")
    if len(selected_cases) != len(set(selected_cases)):
        raise ValueError("Case IDs must not be repeated")
    if len(selected_conditions) != len(set(selected_conditions)):
        raise ValueError("Condition IDs must not be repeated")
    if not 1 <= selected_replicates <= config.replicates:
        raise ValueError(f"replicates must be between 1 and {config.replicates}")
    return selected_cases, selected_conditions, selected_replicates


def build_manifest(
    config: ExperimentConfig,
    *,
    case_ids: Sequence[str] | None = None,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> list[dict[str, Any]]:
    assert_protocol_valid()
    selected_cases, selected_conditions, selected_replicates = _execution_scope(
        config,
        case_ids=case_ids,
        condition_ids=condition_ids,
        replicates=replicates,
    )
    rows: list[dict[str, Any]] = []
    for case_id in selected_cases:
        for condition_id in selected_conditions:
            for replicate in range(1, selected_replicates + 1):
                rows.append(
                    {
                        "run_id": f"{case_id}_{condition_id}_r{replicate:02d}",
                        "case_id": case_id,
                        "condition": condition_id,
                        "order_id": CONDITIONS[condition_id].order_id,
                        "commitment": CONDITIONS[condition_id].commitment,
                        "replicate": replicate,
                        "model": config.model,
                        "reasoning_effort": config.reasoning_effort,
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "max_output_tokens": config.max_output_tokens,
                        "seed": config.seed,
                        "approved_initial_decoding": (
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
    case_ids: Sequence[str] | None = None,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> tuple[Path, Path]:
    manifest = build_manifest(
        config,
        case_ids=case_ids,
        condition_ids=condition_ids,
        replicates=replicates,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "run_manifest.jsonl"
    csv_path = output_dir / "run_manifest.csv"
    write_jsonl(jsonl_path, manifest)
    write_csv(csv_path, manifest)
    transcripts = [
        {
            "run_id": row["run_id"],
            "case_id": row["case_id"],
            "condition": row["condition"],
            "messages": initial_transcript(row["case_id"], row["condition"]),
        }
        for row in manifest
    ]
    write_jsonl(output_dir / "initial_transcripts.jsonl", transcripts)
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


def execute(
    config: ExperimentConfig,
    *,
    paid_api_confirmed: bool,
    case_ids: Sequence[str] | None = None,
    condition_ids: Sequence[str] | None = None,
    replicates: int | None = None,
) -> None:
    if not paid_api_confirmed:
        raise RuntimeError("Execution blocked: pass --execute-paid-api explicitly")
    assert_protocol_valid()
    paths = ensure_output_tree(Path(config.output_root))
    manifest = build_manifest(
        config,
        case_ids=case_ids,
        condition_ids=condition_ids,
        replicates=replicates,
    )
    write_manifest(
        config,
        paths["manifests"],
        case_ids=case_ids,
        condition_ids=condition_ids,
        replicates=replicates,
    )
    provider = provider_from_config(config)

    for run in manifest:
        run_id = run["run_id"]
        case_id = run["case_id"]
        condition = run["condition"]
        initial_parsed_path = paths["parsed"] / f"{run_id}_initial.json"
        revision_parsed_path = paths["parsed"] / f"{run_id}_revision.json"
        if initial_parsed_path.exists() and revision_parsed_path.exists():
            continue

        messages = initial_transcript(case_id, condition)
        initial_started = _utc_now()
        initial_result = provider.generate(messages)
        initial_finished = _utc_now()
        initial_raw = {
            "run": run,
            "stage": "initial",
            "started_at": initial_started,
            "finished_at": initial_finished,
            "request_messages": messages,
            "response_id": initial_result.response_id,
            "output_text": initial_result.output_text,
            "response_body": initial_result.response_body,
        }
        write_json(paths["raw"] / f"{run_id}_initial.json", initial_raw)
        initial_value = validate_initial(
            extract_json(initial_result.output_text), set(CASES[case_id].facts)
        )
        write_json(initial_parsed_path, initial_value)

        revision_text, challenge_ids = revision_prompt(case_id, initial_value)
        revision_messages = messages + [
            {"role": "assistant", "content": initial_result.output_text},
            {"role": "user", "content": revision_text},
        ]
        revision_started = _utc_now()
        revision_result = provider.generate(revision_messages)
        revision_finished = _utc_now()
        revision_raw = {
            "run": run,
            "stage": "secondary_revision_stress_test",
            "started_at": revision_started,
            "finished_at": revision_finished,
            "challenge_fact_ids": challenge_ids,
            "request_messages": revision_messages,
            "response_id": revision_result.response_id,
            "output_text": revision_result.output_text,
            "response_body": revision_result.response_body,
        }
        write_json(paths["raw"] / f"{run_id}_revision.json", revision_raw)
        revision_value = validate_revision(
            extract_json(revision_result.output_text),
            set(CASES[case_id].facts),
            set(challenge_ids),
        )
        revision_value["_challenge_fact_ids"] = challenge_ids
        write_json(revision_parsed_path, revision_value)
