#!/usr/bin/env bash
# Benchmark every preset in src.config.PRESETS, one at a time, with the LLM judge.
# Logs to MLflow and tees console output to bench_overnight.log.
#
# Usage: ./scripts/benchmark_all.sh
set -uo pipefail

cd "$(dirname "$0")/.."
source venv/bin/activate

# Load .env into the shell so OPENAI_API_KEY is visible here (Python loads it separately).
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

mkdir -p var
LOG="var/bench_overnight.log"

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set; the 'gpt' preset and --judge will fail." | tee -a "$LOG"
fi

# caffeinate keeps macOS awake for the whole run; falls back to plain bash elsewhere.
RUNNER=""
command -v caffeinate >/dev/null 2>&1 && RUNNER="caffeinate -i"

$RUNNER bash -c '
  for cfg in $(python -c "from src.config import PRESETS; print(\" \".join(PRESETS))"); do
    echo "=== $cfg @ $(date) ==="
    python scripts/benchmark.py --config "$cfg" --fresh --judge || echo "FAILED: $cfg"
  done
  echo "ALL DONE @ $(date)"
' 2>&1 | tee -a "$LOG"
