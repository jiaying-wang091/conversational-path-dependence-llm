# Phase 1C Self-Reinforcement Pilot

This project implements `PHASE1C_SELF_REINFORCEMENT_PROTOCOL.md` without altering its facts, prompts, conditions, scoring definitions, planned contrasts, analysis logic, or run count.

## Safety default

Validation, manifest generation, fixture tests, scoring, and analysis make no API requests. Model execution requires `OPENAI_API_KEY` and the explicit `--execute-paid-api` flag.

## Design

- One fixed ambiguous interpersonal case with six original facts
- Four longitudinal conditions: fresh evidence, no new evidence, re-anchored, and self-summary
- T0–T3 assessments with prior assistant turns retained in context
- Ten trajectories per condition: 40 trajectories and 160 model responses
- Claim-level manual-coding templates for unsupported interpretation, prior abstraction reuse, abstraction-as-evidence, and factual hallucination

## Local validation

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m path_dependence validate --output-dir validation_phase1c
PYTHONPATH=src python -m path_dependence manifest \
  --config config.example.json \
  --output-dir validation_phase1c
```

## Future execution

```bash
PYTHONPATH=src python -m path_dependence run \
  --config config.example.json \
  --execute-paid-api
```

Omitting `--execute-paid-api` blocks execution before provider creation. Optional `--conditions` and `--replicates` filters support later smoke tests while preserving the 40-trajectory default.

## Output separation

```text
outputs_phase1c/
  raw/          request/response envelopes and complete message provenance
  parsed/       validated JSON for each run and turn
  coded/        turn-level coded records and manual-coding templates
  tables/       longitudinal summaries, contrasts, interactions, and diagnostics
  manifests/    randomized trajectory manifest and exact planned prompts
  validation/   protocol validation reports
```

After outputs exist:

```bash
PYTHONPATH=src python -m path_dependence score --output-root outputs_phase1c
PYTHONPATH=src python -m path_dependence analyze --output-root outputs_phase1c
```

Fresh-evidence comparisons remain descriptive benchmarks. Unsupported interpretation, abstraction provenance, abstraction-as-evidence, and factual hallucination require blinded manual coding; automated outputs do not infer these labels.
