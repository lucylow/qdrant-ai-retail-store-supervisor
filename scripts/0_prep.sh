#!/usr/bin/env bash
set -euo pipefail
echo "=== PREP: create venv and install ==="
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true

echo "=== RUN TESTS (may show failures) ==="
pytest -q || true

echo "=== Baseline: python version and env ==="
python - <<'PY'
import sys, os, json
print("python:", sys.version)
print("env keys:", sorted([k for k in os.environ.keys() if k.startswith('QDRANT') or k.startswith('GEN')][:50]))
PY

echo "=== Done prep ==="
