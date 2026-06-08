# Report Verification for Large or Truncated JSON Outputs

Use this when the final report is too large for a single read or the environment truncates file previews.

## Goal
Inspect the exact saved fields that matter for the claim you are about to make, especially after a code edit and rerun.

## Required pattern
1. Confirm the producing command finished and the report was regenerated.
2. Parse the saved JSON from disk, not just console logs.
3. Query the exact fields you changed or depend on.
4. Only then summarize or complete the task.

## Minimum targeted checks
- `summary.solver_status`
- `summary.total_cost_per_hour`
- `summary.total_load_MW`
- `summary.total_generation_MW`
- full `feasibility_check`
- at least one entry from `generators` or `buses`
- at least one entry from `most_loaded_branches`

- confirm no obvious red-flag numerics remain: generation is not implausibly zero relative to load, implied losses are not negative beyond tolerance, and branch loading is not wildly nonphysical

## Example Python pattern
```python
import json
p = "/root/report.json"  # replace with required path
with open(p) as f:
    data = json.load(f)
print(json.dumps({
    "summary": data["summary"],
    "feasibility_check": data["feasibility_check"],
    "generator_sample": data["generators"][:1],
    "bus_sample": data["buses"][:1],
    "branch_sample": data["most_loaded_branches"][:1],
}, indent=2))
```

## Do not
- Do not rely only on the first or last screenful of a large JSON file.
- Do not assume a field changed just because code was edited.
- Do not summarize values that were not directly re-read from the final saved artifact.
