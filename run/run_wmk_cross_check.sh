#!/bin/bash
set -euo pipefail

# Inject cross_check watermark.
#
# Environment overrides:
#   INPUT_ROOT          Rewritten trajectory root.
#   OUTPUT_ROOT         Watermarked trajectory output root.
#   FREQUENCY           Proportion of trajectories that receive triggers/watermarks.
#   SEED                Random seed for trigger sampling.
#   CROSS_CHECK_COUNT   Maximum number of cross_check injections per trajectory.
#   MODEL               LLM model for constrained cross-check generation.
#   BASE_URL            LLM base URL. Defaults to OPENAI_BASE_URL from .envrc.
#
# Extra runner args can be appended, e.g.
#   ./run_wmk_cross_check.sh --domain 'Bioinformatics & Life Sciences' --task dna-frame2-translation
#   ./run_wmk_cross_check.sh --no-trigger

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ -f .envrc ]]; then
    source .envrc
fi


python scripts/run_watermark.py cross_check \
    --input-root trajectory/conversations-rewritten \
    --output-root trajectory/conversations-watermarked/ratio0.5 \
    --model gpt-5.5 \
    --frequency 0.5 \
    --seed 42 \
    --cross-check-count 2
