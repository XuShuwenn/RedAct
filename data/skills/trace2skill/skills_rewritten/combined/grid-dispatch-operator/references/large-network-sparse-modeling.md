# Large-network sparse modeling patterns

Use this when `network.json` is large or the dispatch model must scale to many buses/branches.

## Fast input inspection

Inspect structure before modeling:
- print top-level keys
- count buses, generators, branches, and gencost rows
- print 1 to 3 representative records from each table
- confirm available fields for generator status, branch ratings, and any reserve data
- determine whether `gencost` is piecewise linear, linear polynomial, or higher-order polynomial

Avoid pasting or manually scanning the full JSON when targeted queries answer the modeling questions.

- Search targeted constraint keys first before broader inspection; for example, look for reserve-defining fields such as `reserve_requirement`, `reserve_capacity`, and other task-specific obligation/capability fields.
- Add a lightweight preflight summary before solver construction:
  - compute bus/generator/branch/`gencost` counts
  - compute total load MW and total online `Pmax`/`Pmin`
  - count online generators and in-service branches
  - record `baseMVA` and whether explicit reserve requirement or reserve-capability fields exist
  - use these values to sanity-check model dimensions and catch obvious infeasibility or missing required fields before coding
- If the file contains embedded schema, `column_info`, or documentation blocks, read those before inferring column positions from raw numeric tables.
- Prefer one short programmatic summary command/script that prints keys, counts, and 1 to 3 sample rows, so the same inspection can be rerun after parsing changes.
- If the file is very large or a full read fails/clips, switch immediately to targeted reads or a short scripted schema probe rather than retrying the full dump.
- For very large structured files, first search for section names or metadata keys, then inspect only short slices around those hits; this is often more reliable than broad reads when tools truncate output.

## Sparse DC-OPF build pattern

Prefer sparse matrices when available:
- generator-to-bus incidence matrix
- branch-to-bus incidence matrix
- branch susceptance / flow matrix
- reduced bus-balance system after fixing one reference angle, if convenient

Keep the formulation equivalent to the required model:
- nodal DC balance
- branch flow equations and limits
- generator bounds
- reserve coupling and reserve requirement

## Post-solve checks

After solving:
- compute reported branch loadings from the same optimized dispatch
- verify slack/reference treatment did not change physical feasibility
- verify totals and per-generator outputs map back to original MATPOWER row ordering

- Validate large output artifacts with both detail and summary checks: confirm expected row counts or representative `generator_dispatch` entries, then confirm totals, `most_loaded_lines`, and `operating_margin_MW` from the parsed saved JSON.
- Prefer targeted parsed checks over full-file display, but do not skip aggregate cross-checks such as summed generator outputs/reserves versus reported totals.
