# Validation

This package holds reusable validation helpers for Parameter Golf experiments.

## Available Helpers

- `validation.log_audit`: parse train logs, summarize final and step metrics, and emit reusable metric rows for telemetry
- `validation.artifact_size`: compute byte counts for candidate artifacts against the decimal `16_000_000` byte cap
- `validation.EXPERIMENT_GATES.md`: define the repo's smoke, proxy, and confirmatory gates

## Usage

```bash
.venv/bin/python -m validation.log_audit logs/<run_id>.txt
.venv/bin/python -m validation.artifact_size train_gpt.py
```

## Still Missing

- tokenizer-accounting checks for custom vocab/tokenizer lanes
- evaluation-protocol sanity checks beyond log parsing
- deeper confirmatory audits once the first baseline path is frozen
