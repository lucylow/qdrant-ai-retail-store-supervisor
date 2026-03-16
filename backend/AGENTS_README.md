# Multi-Agent Improvements — README

This set of changes upgrades the AI Agents for `multi_agent_store_supervisor_v5_hybrid_rag`.

## How to run (local quick demo)

1. Create venv and install (optional helper):

```bash
./scripts/0_prep.sh
```

2. Seed demo goals:

```bash
python scripts/seed_goals.py
```

3. Run a single supervisor pass:

```bash
python scripts/run_supervisor_once.py
```

## What improved

* Strong Agent base + safe execution decorators
* Deterministic planner + LLM-assisted refinements (LLM used only for notes/explanation)
* Executor module with idempotent persistence
* Supervisor with parallelization and safe context merging
* Message bus (durable SQLite) for audit trail
* Safety validators and audit agent
* Observability metrics and tests

## Acceptance criteria

* `pytest tests/*.py` passes for unit tests
* `python scripts/seed_goals.py` seeds goals without exceptions
* `python scripts/run_supervisor_once.py` prints agent results and publishes events

