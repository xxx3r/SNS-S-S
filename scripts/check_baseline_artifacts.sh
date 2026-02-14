#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-outputs/latest}"

rm -rf "${OUT_DIR}"
python -m experiments.baseline \
  --config configs/asteroid_baseline.json \
  --steps 50 \
  --out "${OUT_DIR}"

for artifact in metrics.json timeseries.csv plot_energy.png; do
  if [[ ! -f "${OUT_DIR}/${artifact}" ]]; then
    echo "Missing artifact: ${OUT_DIR}/${artifact}" >&2
    exit 1
  fi
done

echo "Baseline artifact check passed for ${OUT_DIR}"
