"""Prompt builder for the one-shot SkillExtractor baseline."""

from __future__ import annotations

import json
from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """
    Role: One-Shot Skill Distillation Agent

    You are a specialized agent that analyzes benchmark execution trajectories
    and distills them into one reusable skill package for future agents.

    Your mission:
    Analyze one task description, successful trajectories, and failed
    trajectories. Extract the transferable workflow, checks, algorithms,
    tool-use habits, and failure-avoidance lessons. Package them as exactly one
    standard skill resource.

    What makes a good extracted skill:
    - It is reusable for a family of similar tasks, not just the original task.
    - It teaches an agent what to inspect, what to compute, what to verify, and
      which mistakes to avoid.
    - It is concrete enough to guide action, but abstract enough to avoid
      leaking benchmark answers or overfitting to one run.
    - It may include small deterministic helper scripts only when they encode a
      reusable algorithm or validation utility.

    Non-leakage and abstraction rules:
    - Do not reveal trajectory-specific constants, final answers, hidden
      intermediate values, exact task outputs, timestamps, job IDs, or
      one-off file contents.
    - Do not copy long spans of trajectory text.
    - Do not write a recipe that only works for the original task instance.
    - Do not preserve brittle absolute paths unless they are generic skill
      installation conventions shown in the exemplar.
    - Prefer generalized workflows, invariants, verification checks, and
      reusable helper logic.

    Output rule:
    Return valid JSON only. Do not include markdown fences, explanations, or
    any text outside the JSON object.
    """
).strip()


OUTPUT_SCHEMA = {
    "skills": [
        {
            "skill_name": "short-kebab-case-name",
            "description": "One sentence describing when to use this skill.",
            "skill_md": (
                "Complete SKILL.md content, including YAML frontmatter with "
                "name and description."
            ),
            "scripts": [
                {
                    "path": "scripts/helper.py",
                    "content": "Optional helper script content.",
                }
            ],
        }
    ]
}


def build_user_prompt(
    *,
    task_name: str,
    task_description: str,
    success_trajectories: list[dict],
    failure_trajectories: list[dict],
    exemplar: dict[str, str],
    only_failure: bool = False,
) -> str:
    """Build the user prompt for a single-task, single-skill distillation run."""
    has_success = bool(success_trajectories)
    payload = {
        "task_name": task_name,
        "task_description": task_description,
        "success_trajectories": success_trajectories,
        "failure_trajectories": failure_trajectories,
    }
    if only_failure:
        step1 = (
            "STEP 1: Analyze the failure trajectories thoroughly.\n"
            "Identify the specific error types, incorrect assumptions, missing\n"
            "validations, brittle implementations, and misuse of tools. Classify the\n"
            "failure modes into concrete, generalizable pitfalls."
        )
        step2 = (
            "STEP 2: Infer what a correct approach would look like.\n"
            "Based on the failure patterns, reason backward: what workflow, tool\n"
            "combination, validation step, or algorithm would have avoided each\n"
            "failure mode? Do not invent new information — strictly derive from\n"
            "what went wrong."
        )
        step3 = (
            "STEP 3: Abstract a reusable avoidance skill.\n"
            "Extract exactly one skill that teaches a future agent to AVOID the\n"
            "observed failure patterns. The skill should help recognize warning\n"
            "signs, apply correct tools/algorithms, and validate results before\n"
            "finalizing. Focus on the workflow and decision points that led to\n"
            "failure so a future agent can sidestep them."
        )
        quality_note = (
            "- The skill captures failure patterns and avoidance strategies,\n"
            "  not a success recipe.\n"
            "- The skill name should reflect the failure domain."
        )
    else:
        step1 = (
            "STEP 1: Analyze the successful trajectories.\n"
            "Look for repeated strategies, critical decision points, useful helper\n"
            "scripts, verification habits, tool usage patterns, and domain-specific\n"
            "workflows. Ask what the agent did that made success more likely."
        )
        step2 = (
            "STEP 2: Compare against failed trajectories.\n"
            "Identify where failures diverged from successes. Look for missing\n"
            "validation, wrong assumptions, brittle parsing, skipped edge cases,\n"
            "misuse of tools, or premature finalization. Convert these observations\n"
            "into general pitfalls and recovery checks."
        )
        step3 = (
            "STEP 3: Abstract one reusable skill.\n"
            "Extract exactly one skill that would help a future agent solve similar\n"
            "tasks. The skill should be broader than this task instance but still\n"
            "operational. If several micro-patterns appear, merge them into one\n"
            "coherent skill with sections and, if useful, optional scripts."
        )
        quality_note = (
            "- The skill captures transferable workflow knowledge rather than a\n"
            "  transcript summary."
        )

    note = (
        "NOTE: This task has NO successful trajectories — you must analyze failure patterns "
        "to infer the correct approach. Focus on failure modes and their root causes.\n\n"
        if only_failure else ""
    )

    skill_content_note = (
        "and derived from failure pattern analysis"
        if not has_success else
        "and contrasted with failures"
    )

    return dedent(f"""\
        You will receive one preprocessed benchmark task record.

        Understanding your input:
        - Task name: the benchmark task identifier.
        - Task description: the user-facing goal and constraints.
        - Success trajectories: executions that solved the task or demonstrate
          useful partial workflows.
        - Failure trajectories: executions that failed after meaningful agent
          work and can reveal avoidable mistakes.
        - Ideal skill example: a complete skill package that demonstrates the
          desired abstraction level, file structure, and writing style.

        {note}
        Your execution process:

        {step1}

        {step2}

        {step3}

        STEP 4: Package the skill.
        Produce a standard skill package as JSON. The code workflow will write
        SKILL.md and scripts/ files from your JSON, so every file must be
        complete and ready to save.

        The ideal skill package style is shown below. Use it as a format and
        abstraction-level example. Do not copy its biological content unless
        the new task genuinely needs that same domain knowledge.

        <ideal_skill_example>
        {json.dumps(exemplar, ensure_ascii=False, indent=2)}
        </ideal_skill_example>

        Required output schema:
        {json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, indent=2)}

        SKILL.md requirements:
        - Begin with YAML frontmatter:
          ---
          name: <skill-name>
          description: "<when to use this skill>"
          ---
        - Include sections such as When to Use, Core Workflow, Verification,
          Common Pitfalls, and Optional Script Usage when relevant.
        - The content should teach a reusable workflow inferred from the
          trajectories {skill_content_note}.
        - Avoid task-specific values, exact answers, exact intermediate results,
          job IDs, timestamps, and path names that only apply to one run.
        - Include success criteria and verification guidance.
        - Include common pitfalls that are abstracted from failures.
        - Use clear procedural writing. Avoid vague advice such as "be careful"
          unless it is tied to a concrete check.

        Script requirements:
        - Include scripts only when a deterministic helper would genuinely
          improve reuse.
        - Scripts must be self-contained and generic.
        - Script paths must be relative, normally under scripts/.
        - Scripts must not contain task answers or trajectory-specific data.

        Quality checklist before returning:
        - Exactly one skill is present.
        - The skill name is short, descriptive, and kebab-case.
        - SKILL.md is complete, installable, and begins with YAML frontmatter.
        {quality_note}
        - No concrete answers, hidden values, job IDs, or one-run artifacts are
          leaked.
        - Optional scripts are genuinely reusable and placed under scripts/.

        Task data:
        {json.dumps(payload, ensure_ascii=False, indent=2)}

        Return valid JSON only.
        """)