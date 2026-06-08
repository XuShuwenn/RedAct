"""
generate_instruction.py
=======================
Given pre-computed top-k retrieval results and task metadata, generate
instruction.md for each task using retrieved AWM-style workflow memories.

instruction.md format:
```
# Task: {task_name}

## Task Instruction
{instruction_text_from_task}

## Retrieved Workflow Memory
{retrieved_workflow_text}
```

Output: attackers/RAG/outputs/{task}/instruction.md
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_task_instruction(task_name):
    """Load task instruction from the CapTraceBench source."""
    project_root = Path(__file__).parent.parent.parent.parent
    fpath = project_root / "data" / "tasks" / task_name / "instruction.md"
    if fpath.exists():
        with open(fpath) as f:
            return f.read().strip()

    return f"[Task instruction for {task_name} not found. Please provide manually.]"


def load_workflow_texts(membank_path=None):
    """Load workflow memory text by workflow_id."""
    if membank_path is None:
        membank_path = Path(__file__).parent.parent / "membank" / "workflows.jsonl"
    membank_path = Path(membank_path)
    if not membank_path.exists():
        return {}

    workflow_texts = {}
    with open(membank_path) as f:
        for line in f:
            record = json.loads(line)
            workflow_id = record.get("workflow_id")
            if workflow_id:
                workflow_texts[workflow_id] = record.get("text") or record.get("text_for_embedding", "")
    return workflow_texts


def load_record_texts(membank_path=None):
    return load_workflow_texts(membank_path=membank_path)


def format_retrieved_context(results, record_texts, max_chars_per_record=2000):
    """
    Format retrieved records into a readable context section.
    Truncate each record to keep instruction.md manageable.
    """
    lines = []
    lines.append("## Workflow Examples\n")

    for i, r in enumerate(results):
        record_id = r.get("workflow_id") or r.get("record_id", "")

        text = record_texts.get(record_id, "[Text not found]")
        # Truncate
        if len(text) > max_chars_per_record:
            text = text[:max_chars_per_record] + "\n... [truncated]"

        lines.append(f"### Workflow Memory {i+1}")
        lines.append(text)
        lines.append("\n" + "---" + "\n")

    return "\n".join(lines)


def generate_instruction_md(task_name, task_instruction, results, record_texts, output_dir=None):
    """Generate the complete instruction.md content."""
    retrieved_context = format_retrieved_context(results, record_texts)

    md = f"""# Task: {task_name}

## Task Instruction
{task_instruction}

{retrieved_context}
"""
    return md


def generate_all_instructions(tasks_results, task_instructions, record_texts, output_base=None):
    """
    Generate instruction.md for all tasks.
    tasks_results: dict mapping task_name -> list of top-k retrieval results
    task_instructions: dict mapping task_name -> instruction text
    """
    if output_base is None:
        output_base = Path(__file__).parent.parent / "outputs"

    os.makedirs(str(output_base), exist_ok=True)

    outputs = {}
    for task_name, results in sorted(tasks_results.items()):
        instruction = task_instructions.get(task_name, f"[Instruction for {task_name}]")
        md_content = generate_instruction_md(
            task_name,
            instruction,
            results,
            record_texts,
        )

        task_output_dir = output_base / task_name
        os.makedirs(str(task_output_dir), exist_ok=True)
        output_path = task_output_dir / "instruction.md"

        with open(output_path, "w") as f:
            f.write(md_content)

        outputs[task_name] = str(output_path)

    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", type=str, default="attackers/RAG/outputs",
                        help="Directory containing per-task retrieval results")
    parser.add_argument("--tasks_file", type=str, default=None,
                        help="JSON file with task instructions (optional)")
    parser.add_argument("--output_base", type=str, default="attackers/RAG/outputs",
                        help="Base output directory for instruction.md files")
    parser.add_argument("--membank_path", type=str, default="attackers/RAG/membank/workflows.jsonl")
    args = parser.parse_args()

    base = Path(__file__).parent.parent.parent.parent
    results_dir = base / args.results_dir

    # Load all task results
    all_results = {}
    task_instructions = {}

    for task_dir in sorted(os.listdir(str(results_dir))):
        task_path = results_dir / task_dir
        if not task_path.is_dir():
            continue

        # Try to load retrieval results
        results_file = task_path / "retrieval_results.json"
        if results_file.exists():
            with open(results_file) as f:
                all_results[task_dir] = json.load(f)
        else:
            print(f"Warning: No retrieval results for task {task_dir}")
            all_results[task_dir] = []

        # Load task instruction
        task_instructions[task_dir] = load_task_instruction(task_dir)

    # Load retrieved record texts
    record_texts = load_record_texts(
        membank_path=base / args.membank_path,
    )

    # Generate all instruction.md files
    outputs = generate_all_instructions(all_results, task_instructions, record_texts,
                                         output_base=base / args.output_base)

    print(f"\nGenerated {len(outputs)} instruction.md files:")
    for task, path in sorted(outputs.items()):
        print(f"  {task}: {path}")
