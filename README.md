# Phase 1 Conversational Path Dependence Pilot
[![DOI](https://zenodo.org/badge/1399596856.svg)](https://doi.org/10.5281/zenodo.23660727)

This project implements the approved Phase 1 protocol without changing its cases, facts, trajectories, prompts, scoring rubric, or analysis logic.

## Safety default

No API request is made by validation, manifest generation, testing, scoring, or analysis. Model execution requires both a configured exact model identifier and the explicit `--execute-paid-api` flag.

## Design

- 3 immutable synthetic relationship cases
- 5 conditions per case: neutral, negative-first, positive-first, commit-to-A, commit-to-B
- 5 initial replicates per cell, producing 75 conversations
- One initial evaluation and one secondary revision stress test per conversation
- Commitment conditions are compared only with their exact order-matched controls
- Duplicate-output diagnostics report initial and full behavioral uniqueness separately

## Local setup and validation

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
python -m path_dependence validate --output-dir validation
python -m path_dependence manifest --config config.example.json --output-dir validation
```

The `manifest` command creates a randomized 75-run manifest and complete message transcripts without contacting any API.

## Future execution

Copy `config.example.json` and set `OPENAI_API_KEY`. Execution remains blocked unless explicitly invoked:

```bash
python -m path_dependence run --config config.json --execute-paid-api
```

The runner uses the Responses API with a complete manually managed transcript for the initial evaluation, then resends that transcript plus the initial assistant output and adaptive revision prompt. Each run is isolated.

For the approved five-run Case 1 smoke test, retain the same configuration and use execution-only filters:

```bash
PYTHONPATH=src python -m path_dependence run --config config.example.json --case C1 --replicates 1 --execute-paid-api
```

Omitting `--case`, `--conditions`, and `--replicates` preserves the full 75-run default.

Model identifier, reasoning effort, temperature, top-p, output-token limit, and optional seed are configuration fields. The approved initial pilot configuration is `gpt-5.6-sol`, reasoning effort `none`, temperature 0, top-p 1, and five replicates; departures should be treated as a separate protocol run. Each manifest records whether its decoding values match the approved initial settings.

## Output separation

```text
outputs/
  raw/                 API request/response envelopes and raw text
  parsed/              validated initial and revision JSON
  coded/               machine-coded run records and manual-coding template
  tables/              analysis-ready run, diagnostic, summary, and contrast CSVs
  manifests/           randomized run manifest and exact transcripts
  validation/          protocol validation reports
```

Manual judgment remains required for the rubric fields `unsupported_evidence_score` and `revision_responsiveness_score`. The pipeline preserves these as explicit nullable annotations rather than pretending they can be inferred reliably from surface form.

## Analysis

After outputs exist:

```bash
python -m path_dependence score --output-root outputs
python -m path_dependence analyze --output-root outputs
```

If temperature-0 replicates are behaviorally identical, the diagnostic marks the cell as effectively deterministic. Repeated copies remain available for reproducibility but are not treated as independent inferential evidence.
