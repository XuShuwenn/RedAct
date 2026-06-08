# Runtime Search Guide

Use this when the required approximant and mass sweep may be expensive.

## Checklist

1. Run a tiny pilot subset first.
2. Measure elapsed time per job and estimate the full sweep cost.
3. Reuse shared preprocessing work such as conditioned strain data and PSD.
4. If needed, execute in batches or per approximant while checkpointing intermediate best results.
5. Merge verified final best rows into `/root/detection_results.csv`.

## Do / Do not

- Do validate any rewritten or optimized script by actually running it.
- Do preserve the required final search unless the task explicitly permits approximation.
- Do inspect the final CSV before concluding.
- Do not spend the full budget on an unprofiled brute-force first attempt.
- Do not treat pilot runs, logs, or temp files as the final deliverable.
