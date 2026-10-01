"""Command-line entry point."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .analysis import case_instability, condition_summaries, planned_contrasts
from .diagnostics import duplicate_diagnostics
from .protocol import CASES, CONDITIONS
from .runner import ExperimentConfig, execute, write_manifest
from .scoring import code_run, manual_annotation_template
from .storage import ensure_output_tree, read_json, read_jsonl, write_csv, write_jsonl
from .validation import write_validation_report


def _annotations(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    output: dict[str, dict] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            for field in ("unsupported_evidence_score", "revision_responsiveness_score"):
                row[field] = int(row[field]) if row.get(field, "").strip() else None
            output[row["run_id"]] = row
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
        case_ids=args.case_ids,
        condition_ids=args.conditions,
        replicates=args.replicates,
    )
    return 0


def command_score(args: argparse.Namespace) -> int:
    root = Path(args.output_root)
    paths = ensure_output_tree(root)
    manifest = read_jsonl(paths["manifests"] / "run_manifest.jsonl")
    annotations_path = paths["coded"] / "manual_annotations.csv"
    annotations = _annotations(annotations_path)
    coded: list[dict] = []
    parsed_by_run: dict[str, tuple[dict, dict]] = {}
    missing: list[str] = []
    for run in manifest:
        run_id = run["run_id"]
        initial_path = paths["parsed"] / f"{run_id}_initial.json"
        revision_path = paths["parsed"] / f"{run_id}_revision.json"
        if not initial_path.exists() or not revision_path.exists():
            missing.append(run_id)
            continue
        initial = read_json(initial_path)
        revision = read_json(revision_path)
        parsed_by_run[run_id] = (initial, revision)
        coded.append(code_run(run, initial, revision, annotations.get(run_id)))
    if missing and not args.allow_partial:
        raise RuntimeError(f"Missing parsed outputs for {len(missing)} runs; use --allow-partial to inspect")

    write_jsonl(paths["coded"] / "coded_results.jsonl", coded)
    write_csv(paths["tables"] / "run_level_coded.csv", coded)
    if not annotations_path.exists():
        write_csv(
            annotations_path,
            manual_annotation_template(manifest),
            [
                "run_id",
                "unsupported_evidence_score",
                "revision_responsiveness_score",
                "manual_notes",
            ],
        )
    diagnostics = duplicate_diagnostics(coded, parsed_by_run)
    write_jsonl(paths["coded"] / "duplicate_diagnostics.jsonl", diagnostics)
    write_csv(paths["tables"] / "duplicate_diagnostics.csv", diagnostics)
    print(json.dumps({"coded_runs": len(coded), "missing_runs": len(missing)}, indent=2))
    return 0


def command_analyze(args: argparse.Namespace) -> int:
    root = Path(args.output_root)
    paths = ensure_output_tree(root)
    coded = read_jsonl(paths["coded"] / "coded_results.jsonl")
    diagnostics = read_jsonl(paths["coded"] / "duplicate_diagnostics.jsonl")
    if not coded or not diagnostics:
        raise RuntimeError("Run the score command before analyze")
    summaries = condition_summaries(coded, diagnostics)
    contrasts = planned_contrasts(summaries)
    instability = case_instability(coded)
    write_csv(paths["tables"] / "case_condition_summary.csv", summaries)
    write_csv(paths["tables"] / "planned_contrasts.csv", contrasts)
    write_csv(paths["tables"] / "case_instability.csv", instability)
    print(
        json.dumps(
            {
                "case_condition_rows": len(summaries),
                "planned_contrasts": len(contrasts),
                "case_instability_rows": len(instability),
                "revision_interpretation": "secondary stress test only",
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate immutable protocol")
    validate.add_argument("--output-dir", default="validation")
    validate.set_defaults(func=command_validate)

    manifest = subparsers.add_parser("manifest", help="write dry-run manifest and transcripts")
    manifest.add_argument("--config", required=True)
    manifest.add_argument("--output-dir", required=True)
    manifest.set_defaults(func=command_manifest)

    run = subparsers.add_parser("run", help="execute model calls; explicitly gated")
    run.add_argument("--config", required=True)
    run.add_argument(
        "--case",
        dest="case_ids",
        action="append",
        choices=tuple(CASES),
        help="case ID to execute; repeat for multiple cases (default: all)",
    )
    run.add_argument(
        "--conditions",
        nargs="+",
        choices=tuple(CONDITIONS),
        help="conditions to execute (default: all five)",
    )
    run.add_argument(
        "--replicates",
        type=int,
        help="replicates per selected cell (default: value from config)",
    )
    run.add_argument("--execute-paid-api", action="store_true")
    run.set_defaults(func=command_run)

    score = subparsers.add_parser("score", help="score parsed outputs")
    score.add_argument("--output-root", required=True)
    score.add_argument("--allow-partial", action="store_true")
    score.set_defaults(func=command_score)

    analyze = subparsers.add_parser("analyze", help="write analysis-ready summaries")
    analyze.add_argument("--output-root", required=True)
    analyze.set_defaults(func=command_analyze)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
