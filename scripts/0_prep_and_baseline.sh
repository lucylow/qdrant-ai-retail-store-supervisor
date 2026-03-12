#!/usr/bin/env bash
set -euo pipefail
echo "=== PREP: venv, install, lint, tests ==="
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true

echo "=== LINT / TYPECHECK ==="
mypy --ignore-missing-imports || true
flake8 || true

echo "=== RUN UNIT TESTS (some may rely on Qdrant) ==="
pytest -q || true

echo "=== ENV INFO ==="
python - <<'PY'
import sys, os
print("python:", sys.version)
print("important env keys:", {k: os.environ.get(k) for k in ['QDRANT_URL','QDRANT_API_KEY','HF_API_KEY','OPENAI_API_KEY'] if os.environ.get(k)})
PY

echo "=== PREP DONE ==="

#!/usr/bin/env bash
set -euo pipefail
echo "=== prepare virtualenv and install ==="
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== run linters and tests (warnings allowed) ==="
mypy --ignore-missing-imports || true
flake8 || true
pytest -q || true

echo "=== collect baseline info ==="
python - <<'PY'
import sys, json, platform, os
print("python", sys.version)
print("platform", platform.platform())
env = {k: os.environ.get(k) for k in ("QDRANT_URL","QDRANT_API_KEY","GENERATOR_MODEL")}
print("env keys:", {k:v for k,v in env.items() if v})
PY

echo "=== done ==="
