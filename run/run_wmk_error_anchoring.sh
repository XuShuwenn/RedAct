#!/bin/bash
# Inject error_anchoring watermark
#
# Options:
#   --frequency   Proportion of trajectories that receive triggers (0.0-1.0, default: 0.5)
#   --domain      Filter by domain (can be repeated)
#   --task        Filter by task name (can be repeated)
#   --no-trigger  Skip trigger injection (test inject logic only)

python scripts/run_watermark.py error_anchoring \
    --input-root trajectory/conversations-rewritten \
    --output-root trajectory/conversations-watermarked/ratio0.5 \
    --model gpt-5.5 \
    --frequency 0.5 \
    --seed 42