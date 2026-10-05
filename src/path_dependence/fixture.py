"""Generate deterministic offline Phase 1C fixtures; never contacts a provider."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .protocol import (
    ORIGINAL_FACTS,
    SYSTEM_PROMPT,
    available_fact_ids,
    available_new_fact_ids,
    user_prompt,
)
from .runner import ExperimentConfig, build_manifest, write_manifest
from .schemas import validate_assessment
from .scoring import manual_turn_annotation_template
from .storage import ensure_output_tree, write_csv, write_json
from .validation import write_validation_report


STEPS = {
    "fresh_evidence": 1,
    "no_new_evidence": 2,
    "re_anchored": 0,
    "self_summary": 3,
}


def _assessment(condition: str, turn: int, replicate: int) -> dict:
    variation = (replicate - 1) % 3
    signed = STEPS[condition] * turn + (variation if turn else 0)
    p_a = 40 + signed
    p_b = 40 - signed
    original_ids = list(ORIGINAL_FACTS)
    if condition == "re_anchored" and turn:
        cited_original = original_ids
    elif condition == "self_summary" and turn:
        cited_original = original_ids[: max(1, 3 - turn)]
    elif condition == "no_new_evidence" and turn:
        cited_original = original_ids[: max(2, 4 - turn)]
    else:
        cited_original = ["C-F1", "C-F4", "C-F5"]
    support_ids = cited_original[: max(1, len(cited_original) // 2)]
    against_ids = cited_original[len(support_ids) :]
    available_updates = sorted(available_new_fact_ids(condition, turn))
    if available_updates:
        against_ids.append(available_updates[-1])
    value = {
        "pre_reassessment_text": f"Offline fixture basis for {condition} at T{turn}.",
        "most_likely_interpretation": "genuinely_indeterminate",
        "probabilities": {"A": p_a, "B": p_b, "indeterminate": 20},
        "confidence": 60 + STEPS[condition] * turn + variation,
        "evidence_supporting_most_likely": [
            {"fact_id": fact_id, "explanation": "Offline fixture support."}
            for fact_id in support_ids
        ],
        "evidence_against_most_likely": [
            {"fact_id": fact_id, "explanation": "Offline fixture counterevidence."}
            for fact_id in against_ids
        ],
        "recommendation": {
            "category": "observe_and_wait",
            "intensity": 0,
            "explanation": "Offline fixture recommendation.",
        },
    }
    validate_assessment(value, available_fact_ids(condition, turn))
    return value


def generate_fixture(config_path: Path, output_root: Path) -> None:
    config = ExperimentConfig.from_path(config_path)
    paths = ensure_output_tree(output_root)
    write_validation_report(paths["validation"])
    write_manifest(config, paths["manifests"])
    manifest = build_manifest(config)
    manual_rows = manual_turn_annotation_template(manifest)
    manual_index = {(row["run_id"], row["turn"]): row for row in manual_rows}

    for run in manifest:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(run["condition"], 0)},
        ]
        prior_turns: list[str] = []
        for turn in range(4):
            value = _assessment(run["condition"], turn, run["replicate"])
            output_text = json.dumps(value, ensure_ascii=False, sort_keys=True)
            raw = {
                "offline_fixture": True,
                "run": run,
                "turn": turn,
                "turn_id": f"T{turn}",
                "request_messages": list(messages),
                "prior_assistant_turns": list(prior_turns),
                "available_original_fact_ids": sorted(ORIGINAL_FACTS),
                "available_new_fact_ids": sorted(
                    available_new_fact_ids(run["condition"], turn)
                ),
                "response_id": None,
                "output_text": output_text,
                "response_body": {"offline_fixture": True},
            }
            write_json(paths["raw"] / f"{run['run_id']}_T{turn}.json", raw)
            parsed = dict(value)
            parsed.update(
                {
                    "_turn": turn,
                    "_turn_id": f"T{turn}",
                    "_prior_assistant_turns": list(prior_turns),
                    "_available_original_fact_ids": sorted(ORIGINAL_FACTS),
                    "_available_new_fact_ids": sorted(
                        available_new_fact_ids(run["condition"], turn)
                    ),
                    "_offline_fixture": True,
                }
            )
            write_json(paths["parsed"] / f"{run['run_id']}_T{turn}.json", parsed)
            annotation = manual_index[(run["run_id"], turn)]
            annotation.update(
                {
                    "interpretive_proposition_count": 4,
                    "unsupported_interpretation_count": (
                        turn if run["condition"] == "self_summary" else 0
                    ),
                    "factual_proposition_count": 4,
                    "fabricated_factual_claim_count": 0,
                    "prior_abstraction_reference_count": (
                        turn if run["condition"] == "self_summary" else 0
                    ),
                    "stated_evidentiary_premise_count": 4,
                    "abstraction_as_evidence_count": (
                        turn if run["condition"] == "self_summary" else 0
                    ),
                    "manual_notes": "Synthetic offline validation fixture; not empirical coding.",
                }
            )
            messages.append({"role": "assistant", "content": output_text})
            prior_turns.append(f"T{turn}")
            if turn < 3:
                messages.append(
                    {
                        "role": "user",
                        "content": user_prompt(run["condition"], turn + 1),
                    }
                )
    write_csv(paths["coded"] / "manual_turn_annotations.csv", manual_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    generate_fixture(Path(args.config), Path(args.output_root))
    print(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
