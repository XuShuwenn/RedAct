# SkillExtractor Attacker

SkillExtractor is a one-shot skill distillation baseline. Given a task
description and preprocessed successful or failed trajectories, it asks an LLM
to synthesize a reusable skill package for future agents.

## Input

Each input JSON contains:

- `task_name`: task identifier,
- `task_description`: user goal and constraints,
- `success_trajectories`: summarized successful runs,
- `failure_trajectories`: summarized failed runs, optional.

## Output

The attacker writes one skill package per task:

```text
attackers/SkillExtractor/skills/<task_name>/<skill_name>/
├── SKILL.md
└── scripts/        # optional helper scripts
```

## Quick Start

Prepare trajectory inputs:

```bash
python attackers/SkillExtractor/data_converter.py \
  --input-root trajectory/conversations-clean \
  --output-root attackers/SkillExtractor/inputs
```

Run one task:

```bash
python -m attackers.SkillExtractor.skill_extractor.run \
  --input-json attackers/SkillExtractor/inputs/dna-frame2-translation.json \
  --output-root attackers/SkillExtractor/skills \
  --model gpt-5 \
  --wire-api responses \
  --overwrite
```

Run all prepared inputs:

```bash
find attackers/SkillExtractor/inputs -name '*.json' -print0 | \
  xargs -0 -n 1 -I {} python -m attackers.SkillExtractor.skill_extractor.run \
    --input-json {} \
    --output-root attackers/SkillExtractor/skills \
    --model gpt-5 \
    --wire-api responses
```

## Configuration

The attacker reads OpenAI-compatible credentials from the environment:

```bash
export OPENAI_API_KEY=your_key
export OPENAI_BASE_URL=https://api.openai.com/v1
```

By default, the prompt includes an exemplar skill from:

```text
captracebench/tasks/dna-frame2-translation/environment/skills/sequence-analysis
```

Use `--exemplar-skill-dir` to provide a different exemplar.

## Notes

- The system prompt asks the model to avoid copying task-specific constants,
  final answers, hidden intermediate values, job IDs, timestamps, or one-off
  artifacts.
- Generated scripts are syntax-checked before the skill package is written.
- Use the RedAct experiment scripts to evaluate extracted skills against
  CapTraceBench tasks.
