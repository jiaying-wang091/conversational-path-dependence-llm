"""Command-line entry point for the Phase 1C self-reinforcement pilot."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .analysis import (
    condition_slope_summaries,
    condition_turn_interactions,
    fresh_update_effects,
    lagged_abstraction_rows,
    monotonicity_summaries,
    planned_contrasts,
    trajectory_slope_rows,
    transition_rows,
    turn_condition_summaries,
    within_condition_changes,
)
from .diagnostics import duplicate_diagnostics
from .protocol import CONDITIONS
from .runner import ExperimentConfig, execute, write_manifest
from .scoring import (
    MANUAL_COUNT_FIELDS,
    code_trajectory,
    manual_claim_annotation_template,
    manual_turn_annotation_template,
)
from .storage import ensure_output_tree, read_json, read_jsonl, write_csv, write_jsonl
from .validation import write_validation_report


def _annotations(path: Path) -> dict[tuple[str, int], dict]:
    if not path.exists():
        return {}
    output: dict[tuple[str, int], dict] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            for field in MANUAL_COUNT_FIELDS:
                row[field] = int(row[field]) if row.get(field, "").strip() else None
            output[(row["run_id"], int(row["turn"]))] = row
    return output


def command_validate(args: argparse.Namespace) -> int:
    path = write_validation_report(Path(args.output_dir))
    print(path)
    return 0


def command_manifest(args: argparse.Namespace) -> int:
    config = ExperimentConfig.from_path(Path(args.config))
    output_dir = Path(args.output_dir)
    write_validation_report(output_dir)
    paths = write_manifest(config, output_dir)
    print("\n".join(str(path) for path in paths))
    return 0


def command_run(args: argparse.Namespace) -> int:
    config = ExperimentConfig.from_path(Path(args.config))
    execute(
        config,
        paid_api_confirmed=args.execute_paid_api,
        condition_ids=args.conditions,
        replicates=args.replicates,
    )
    return 0


def command_score(args: argparse.Namespace) -> int:
    root = Path(args.output_root)
    paths = ensure_output_tree(root)
    manifest = read_jsonl(paths["manifests"] / "run_manifest.jsonl")
    annotation_path = paths["coded"] / "manual_turn_annotations.csv"
    claim_path = paths["coded"] / "manual_claim_annotations.csv"
    annotations = _annotations(annotation_path)
    coded: list[dict] = []
    parsed_by_run: dict[str, dict[int, dict]] = {}
    missing: list[str] = []

    for run in manifest:
        run_id = run["run_id"]
        assessments: dict[int, dict] = {}
        for turn in range(4):
            path = paths["parsed"] / f"{run_id}_T{turn}.json"
            if path.exists():
                assessments[turn] = read_json(path)
        if len(assessments) != 4:
            missing.append(run_id)
            continue
        parsed_by_run[run_id] = assessments
        run_annotations = {
            turn: annotations[(run_id, turn)]
            for turn in range(4)
            if (run_id, turn) in annotations
        }
        coded.extend(code_trajectory(run, assessments, run_annotations))

    if missing and not args.allow_partial:
        raise RuntimeError(
            f"Missing complete T0-T3 parsed outputs for {len(missing)} trajectories; "
            "use --allow-partial to inspect"
        )

    write_jsonl(paths["coded"] / "turn_coded_results.jsonl", coded)
    write_csv(paths["tables"] / "turn_level_coded.csv", coded)
    if not annotation_path.exists():
        write_csv(annotation_path, manual_turn_annotation_template(manifest))
    if not claim_path.exists():
        write_csv(claim_path, manual_claim_annotation_template(manifest))
    condition_diagnostics, turn_diagnostics = duplicate_diagnostics(
        coded, parsed_by_run
    )
    write_jsonl(
        paths["coded"] / "duplicate_diagnostics.jsonl", condition_diagnostics
    )
    write_csv(paths["tables"] / "duplicate_diagnostics.csv", condition_diagnostics)
    write_csv(paths["tables"] / "turn_duplicate_diagnostics.csv", turn_diagnostics)
    print(
        json.dumps(
            {
                "coded_trajectories": len(parsed_by_run),
                "coded_turns": len(coded),
                "missing_trajectories": len(missing),
            },
            indent=2,
        )
    )
    return 0


def command_analyze(args: argparse.Namespace) -> int:
    root = Path(args.output_root)
    paths = ensure_output_tree(root)
    coded = read_jsonl(paths["coded"] / "turn_coded_results.jsonl")
    if not coded:
        raise RuntimeError("Run the score command before analyze")
    turn_summary = turn_condition_summaries(coded)
    trajectory_slopes = trajectory_slope_rows(coded)
    slope_summary = condition_slope_summaries(trajectory_slopes)
    changes = within_condition_changes(coded)
    contrasts = planned_contrasts(slope_summary, changes)
    interactions = condition_turn_interactions(turn_summary)
    monotonicity = monotonicity_summaries(coded)
    conclusion_transitions = transition_rows(coded, "conclusion_category")
    recommendation_transitions = transition_rows(coded, "recommendation_category")
    fresh_effects = fresh_update_effects(coded)
    lagged = lagged_abstraction_rows(coded)

    write_csv(paths["tables"] / "condition_turn_summary.csv", turn_summary)
    write_csv(paths["tables"] / "trajectory_longitudinal_slopes.csv", trajectory_slopes)
    write_csv(paths["tables"] / "condition_longitudinal_slopes.csv", slope_summary)
    write_csv(paths["tables"] / "within_condition_T3_minus_T0.csv", changes)
    write_csv(paths["tables"] / "planned_contrasts.csv", contrasts)
    write_csv(paths["tables"] / "condition_by_turn_interactions.csv", interactions)
    write_csv(paths["tables"] / "monotonicity_summary.csv", monotonicity)
    write_csv(paths["tables"] / "conclusion_transitions.csv", conclusion_transitions)
    write_csv(
        paths["tables"] / "recommendation_transitions.csv",
        recommendation_transitions,
    )
    write_csv(paths["tables"] / "fresh_update_effects.csv", fresh_effects)
    write_csv(paths["tables"] / "lagged_abstraction_descriptive.csv", lagged)
    print(
        json.dumps(
            {
                "condition_turn_rows": len(turn_summary),
                "trajectory_slope_rows": len(trajectory_slopes),
                "planned_contrast_rows": len(contrasts),
                "condition_turn_interaction_rows": len(interactions),
                "fresh_evidence_is_descriptive_benchmark": True,
                "lagged_abstraction_analysis_is_causal": False,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate immutable protocol")
    validate.add_argument("--output-dir", default="validation_phase1c")
    validate.set_defaults(func=command_validate)

    manifest = subparsers.add_parser(
        "manifest", help="write dry-run manifest and planned conversations"
    )
    manifest.add_argument("--config", required=True)
    manifest.add_argument("--output-dir", required=True)
    manifest.set_defaults(func=command_manifest)

    run = subparsers.add_parser("run", help="execute model calls; explicitly gated")
    run.add_argument("--config", required=True)
    run.add_argument(
        "--conditions",
        nargs="+",
        choices=tuple(CONDITIONS),
        help="conditions to execute (default: all four)",
    )
    run.add_argument(
        "--replicates",
        type=int,
        help="trajectories per selected condition (default: config value)",
    )
    run.add_argument("--execute-paid-api", action="store_true")
    run.set_defaults(func=command_run)

    score = subparsers.add_parser("score", help="score parsed turn outputs")
    score.add_argument("--output-root", required=True)
    score.add_argument("--allow-partial", action="store_true")
    score.set_defaults(func=command_score)

    analyze = subparsers.add_parser("analyze", help="write longitudinal analysis tables")
    analyze.add_argument("--output-root", required=True)
    analyze.set_defaults(func=command_analyze)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
