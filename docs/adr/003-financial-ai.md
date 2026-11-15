# ADR 003: Financial AI approach

## Decision

Authoritative totals are computed with Decimal application code. Forecasts use chronological time-trend regression. Narratives use deterministic EN/AR templates. Optional LLM may only restate structured facts and is never used for arithmetic.

## Why

Prevents financial hallucination and keeps forecasts auditable and testable without external AI keys.
