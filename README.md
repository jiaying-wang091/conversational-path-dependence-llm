# Phase 1B Ambiguity × Conversational Trajectory Pilot

This project implements `PHASE1B_AMBIGUITY_PROTOCOL_REVISED.md` without altering its facts, diagnosticity scores, conditions, planned contrasts, or analysis logic.

## Safety default

Validation, manifest generation, tests, scoring, and analysis make no API requests. Model execution requires `OPENAI_API_KEY` and the explicit `--execute-paid-api` flag.

## Design

- Six variants: Low-A, Low-B, Medium-A, Medium-B, High-A, High-B
- Five conditions per variant: neutral, negative-first, positive-first, commit-to-A, commit-to-B
- Five replicates per cell: 150 experimental runs
- One initial evaluation and one secondary revision stress-test response per run
- Frozen ex ante diagnosticity scores with symmetric A/B net scores and total absolute evidence strength within each ambiguity level
- Revision results remain secondary and are excluded from the primary ambiguity × trajectory analysis

## Local validation

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
python -m path_dependence validate --output-dir validation_phase1b
python -m path_dependence manifest --config config.example.json --output-dir validation_phase1b
```

Manifest generation writes all 150 planned transcripts without contacting the API.

## Future execution

The approved configuration is `gpt-5.6-sol`, reasoning effort `none`, temperature `0`, top-p `1`, five replicates, and no seed.

```bash
PYTHONPATH=src python -m path_dependence run \
  --config config.json \
  --execute-paid-api
```

Execution filters remain available through `--variant`, `--conditions`, and `--replicates`; omitting them preserves the full 150-run default.

## Output separation

```text
outputs_phase1b/
  raw/          API request/response envelopes and raw model text
  parsed/       validated initial and revision JSON
  coded/        coded run records, manual annotations, duplicate diagnostics
  tables/       analysis-ready summaries, contrasts, interactions, and checks
  manifests/    randomized manifest and exact initial transcripts
  validation/   protocol validation reports
```

After model outputs exist:

```bash
PYTHONPATH=src python -m path_dependence score --output-root outputs_phase1b
PYTHONPATH=src python -m path_dependence analyze --output-root outputs_phase1b
```

Analysis tables include within-variant contrasts, polarity-pooled sensitivity measures, neutral-condition manipulation checks, monotonicity classifications, descriptive three-way interaction contrasts, variant and ambiguity-level disagreement summaries, and separate initial/full duplicate diagnostics.

Manual judgment remains required for `unsupported_evidence_score` and `revision_responsiveness_score`. Effectively identical temperature-0 replicates are retained as reproducibility diagnostics and are not treated as independent evidence.
