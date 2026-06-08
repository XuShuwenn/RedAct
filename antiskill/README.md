# RedAct Core

`antiskill` contains the core RedAct implementation for identifying protected
task information, rewriting public traces, and supporting trace-protection
experiments.

## Components

- `src/core/key_info_extractor.py`: extracts protected procedural information
  from task instructions and skill documents.
- `src/core/trajectory_rewriter.py`: rewrites assistant turns while preserving
  task evidence and final-answer fields.
- `src/prompts/`: prompt templates for extraction and rewriting.
- `src/configs/default.yaml`: default runtime configuration.

## Inputs

RedAct expects:

```text
data/tasks/<task_name>/instruction.md
data/tasks/<task_name>/environment/skills/<skill_name>/SKILL.md
data/extra_data/<task_name>/key_info.txt
trajectory/conversations-clean/<domain>/<task_name>/*.json
```

The key-info file lists formulas, thresholds, constants, tool choices, and
validation routines that should be generalized during trace rewriting.

## Rewriting Behavior

The rewriter processes assistant messages in batches. User messages are copied
and optionally truncated. If a rewrite fails, the original assistant content is
kept and the output is marked with `status: "rewrite_failed"`.

Successful outputs preserve:

- task intent and execution order,
- tool-use evidence,
- verifier-relevant schema fields,
- final answers needed for audit.

Protected details are replaced with natural, task-agnostic descriptions instead
of visible redaction markers.

## Example

```bash
python scripts/rewrite_trajectory.py \
  --traj-root trajectory/conversations-clean \
  --output-root trajectory/conversations-rewritten \
  --key-info-root data/extra_data \
  --task dna-frame2-translation \
  --rewrite-mode key_info \
  --workers 1 \
  --model gpt-5
```

Generated files keep the original domain/task/file layout under the output
root.
