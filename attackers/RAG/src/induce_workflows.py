"""
induce_workflows.py
===================
Build an AWM-style MemBank from successful trajectories.

Each reward=1 trajectory is compressed into one reusable workflow memory. The
memory should preserve the transferable procedure while redacting trajectory-
specific answers, intermediate numbers, paths, and identifiers.
"""

import argparse
import hashlib
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"
MEMBANK_DIR = Path(__file__).parent.parent / "membank"


SYSTEM_PROMPT = """You are inducing reusable workflow memories from successful assistant trajectories.
Write a reusable planning-style workflow summary that would help solve similar benchmark tasks.

Hard constraints:
- Do not reveal final answers from the trajectory.
- Do not reveal intermediate numeric values, IDs, coordinates, file-specific constants, material names, account names, or other instance-specific facts.
- Replace instance-specific details with variables such as {input_file}, {target_id}, {computed_value}, {threshold}, {output_file}.
- Preserve the continuous workflow: what to inspect, what tools/scripts to use, what checks to run, and how to verify completion.
- The workflow must be reusable guidance, not a transcript and not an answer.
- Use a concise planning style. Prefer 1 short title line plus 4-8 ordered steps.
- Include verification and common pitfalls when useful.

Return only the workflow summary as plain Markdown. Do not wrap it in JSON or code fences.
"""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def stable_id(*parts):
    raw = "::".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def redact_instance_values(text):
    """Conservatively redact trajectory-specific values before induction."""
    if not text:
        return ""

    redacted = text
    redacted = re.sub(r"\b3D\b", "__THREE_D__", redacted, flags=re.IGNORECASE)

    # Paths and filenames often directly encode task instances or expected outputs.
    redacted = re.sub(r"`?/(?:[\w.-]+/)*[\w.-]+`?", "{path}", redacted)
    redacted = re.sub(
        r"\b[\w.-]+\.(?:json|csv|tsv|txt|md|stl|obj|ply|py|npz|npy|pkl|parquet|yaml|yml)\b",
        "{file}",
        redacted,
        flags=re.IGNORECASE,
    )

    # Long hashes, UUID-like strings, trajectory ids, and opaque codes.
    redacted = re.sub(r"\b[a-f0-9]{6,}\b", "{id}", redacted, flags=re.IGNORECASE)
    redacted = re.sub(
        r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[-_])[A-Za-z0-9][A-Za-z0-9._-]{5,}\b",
        "{identifier}",
        redacted,
    )

    # Numeric values, including units. This intentionally redacts most numbers
    # from trajectories; task instructions are kept separately at evaluation time.
    redacted = re.sub(
        r"(?<![A-Za-z])[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:e[-+]?\d+)?\s*(?:%|[A-Za-z]{1,8}(?:/[A-Za-z]{1,8})?)?",
        "{value}",
        redacted,
        flags=re.IGNORECASE,
    )

    # Quoted paths and long answer-like literals are often names or labels. Keep
    # JSON keys and short tool arguments readable because they preserve workflow.
    redacted = re.sub(r'"[^"\n]*(?:/|\\\\|\.)[^"\n]*"', '"{literal}"', redacted)
    redacted = re.sub(r"'[^'\n]*(?:/|\\\\|\.)[^'\n]*'", "'{literal}'", redacted)
    redacted = re.sub(r'"[^"\n]{81,}"', '"{literal}"', redacted)
    redacted = re.sub(r"'[^'\n]{81,}'", "'{literal}'", redacted)

    # Collapse repeated placeholders and excessive whitespace.
    redacted = re.sub(r"(?:\{value\}\s*){2,}", "{value} ", redacted)
    redacted = re.sub(r"\n{3,}", "\n\n", redacted)
    redacted = redacted.replace("__THREE_D__", "3D")
    return redacted.strip()


def remove_final_answer_section(text):
    patterns = [
        r"\n\s*\*\*Results:\*\*",
        r"\n\s*##\s*Summary\b",
        r"\n\s*#+\s*Results\b",
        r"\n\s*Perfect!.*summary:",
        r"\n\s*Excellent!.*summary:",
        r"\n\s*The calculation is complete\b",
    ]
    cut_points = []
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            cut_points.append(match.start())
    if not cut_points:
        return text
    return text[:min(cut_points)].rstrip() + "\n[final answer summary omitted]"


def trajectory_to_redacted_text(traj, max_chars=12000):
    lines = []
    for turn in traj.get("turns", []):
        if turn.get("role") != "assistant":
            continue
        role = turn.get("role", "unknown").upper()
        content = turn.get("content", "")
        content = remove_final_answer_section(content)
        content = redact_instance_values(content)
        if not content:
            continue
        lines.append(f"[{role}]\n{content}")
    text = "\n\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [truncated]"
    return text


def get_openai_client(api_base=None, api_key=None):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError("pip install openai") from exc

    return OpenAI(
        api_key=api_key or os.environ.get("OPENAI_API_KEY"),
        base_url=api_base or os.environ.get("OPENAI_BASE_URL"),
    )


def generate_with_openai(client, model_name, prompt, max_tokens=1200,
                         max_retries=3, retry_sleep=3.0):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                )
            except Exception as exc:
                msg = str(exc).lower()
                if "max_completion_tokens" not in msg and "unsupported" not in msg and "unrecognized" not in msg:
                    raise
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            last_error = exc
            if attempt == max_retries:
                break
            time.sleep(retry_sleep * attempt)

    raise RuntimeError(f"OpenAI workflow induction failed after {max_retries} attempts: {last_error}")


def clean_workflow_summary(text):
    text = text.strip()
    text = re.sub(r"^```(?:markdown|md|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def induce_workflow_for_trajectory(traj_path, client=None, args=None):
    traj = load_json(traj_path)
    if traj.get("meta_info", {}).get("reward") != 1:
        return None

    meta_info = traj.get("meta_info", {})
    task_name = traj.get("task_name", Path(traj_path).parent.name)
    traj_id = traj.get("trajectory_id", Path(traj_path).stem.replace("trajectory_", ""))
    redacted_text = trajectory_to_redacted_text(traj, max_chars=args.max_trace_chars)

    prompt = f"""Task family: {task_name}
Source trajectory id: {traj_id}

Redacted successful assistant trajectory:
{redacted_text}

Induce one reusable planning-style workflow summary from this assistant trajectory."""
    raw = generate_with_openai(
        client,
        args.generator_model,
        prompt,
        max_tokens=args.max_new_tokens,
        max_retries=args.max_retries,
        retry_sleep=args.retry_sleep,
    )
    workflow_summary = clean_workflow_summary(raw)
    raw_model_output = raw
    compression_mode = "openai_api"

    return {
        "workflow_id": f"{task_name}__{traj_id}__{stable_id(task_name, traj_id)}",
        "task": task_name,
        "source_trajectory_id": traj_id,
        "source_file": str(traj_path),
        "agent_name": traj.get("agent_name") or meta_info.get("agent") or meta_info.get("agent_name"),
        "model_name": traj.get("model_name") or meta_info.get("model") or meta_info.get("model_name"),
        "reward": traj.get("meta_info", {}).get("reward"),
        "compression_mode": compression_mode,
        "generator_model": args.generator_model,
        "workflow_summary": workflow_summary,
        "text": workflow_summary,
        "text_for_embedding": workflow_summary,
        "raw_model_output": raw_model_output,
    }


def collect_trajectory_paths(data_dir, max_per_task=8):
    tasks = [
        d for d in sorted(os.listdir(data_dir))
        if (data_dir / d).is_dir() and not d.startswith("_") and d != "__pycache__"
    ]
    paths = []
    for task in tasks:
        task_dir = data_dir / task
        task_paths = []
        for fname in sorted(os.listdir(task_dir)):
            if fname.endswith(".json"):
                fpath = task_dir / fname
                try:
                    traj = load_json(fpath)
                except Exception:
                    continue
                if traj.get("meta_info", {}).get("reward") == 1:
                    task_paths.append(fpath)
        paths.extend(task_paths[:max_per_task])
    return paths


def save_membank(workflows, output_path):
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, "w") as f:
        for workflow in workflows:
            f.write(json.dumps(workflow, ensure_ascii=False) + "\n")
    return output_path


def induce_one_indexed(index, total, traj_path, args):
    client = get_openai_client(api_base=args.api_base, api_key=args.api_key)
    workflow = induce_workflow_for_trajectory(traj_path, client, args)
    return index, workflow


def induce_all_workflows(args):
    data_dir = Path(args.data_dir)
    output_path = Path(args.output)
    traj_paths = collect_trajectory_paths(data_dir, max_per_task=args.max_per_task)

    workflows = []
    failed = []
    total = len(traj_paths)
    indexed_workflows = {}

    if args.workers <= 1:
        for i, traj_path in enumerate(traj_paths, start=1):
            try:
                _, workflow = induce_one_indexed(i, total, traj_path, args)
                if workflow:
                    indexed_workflows[i] = workflow
                print(f"  Induced {i}/{total}: {traj_path}")
            except Exception as exc:
                failed.append({"path": str(traj_path), "error": str(exc)})
                print(f"  Warning: failed to induce workflow for {traj_path}: {exc}")
    else:
        print(f"Running workflow induction with {args.workers} worker threads")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(induce_one_indexed, i, total, traj_path, args): (i, traj_path)
                for i, traj_path in enumerate(traj_paths, start=1)
            }
            for future in as_completed(futures):
                i, traj_path = futures[future]
                try:
                    _, workflow = future.result()
                    if workflow:
                        indexed_workflows[i] = workflow
                    print(f"  Induced {i}/{total}: {traj_path}")
                except Exception as exc:
                    failed.append({"path": str(traj_path), "error": str(exc)})
                    print(f"  Warning: failed to induce workflow for {traj_path}: {exc}")

    workflows = [indexed_workflows[i] for i in sorted(indexed_workflows)]

    save_membank(workflows, output_path)

    failed_path = output_path.with_suffix(".failed.json")
    if failed:
        with open(failed_path, "w") as f:
            json.dump(failed, f, indent=2, ensure_ascii=False)

    print(f"\nMemBank saved to: {output_path}")
    print(f"Total workflows: {len(workflows)}")
    if failed:
        print(f"Failed trajectories: {len(failed)} ({failed_path})")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Induce workflow memories from successful trajectories")
    parser.add_argument("--data_dir", type=str, default=str(DATA_DIR))
    parser.add_argument("--output", type=str, default=str(MEMBANK_DIR / "workflows.jsonl"))
    parser.add_argument("--max_per_task", type=int, default=8)
    parser.add_argument("--generator_model", type=str, default="gpt-5.4",
                        help="OpenAI-compatible chat model used for workflow induction")
    parser.add_argument("--api_base", type=str, default=None)
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--max_trace_chars", type=int, default=12000)
    parser.add_argument("--max_new_tokens", type=int, default=1200)
    parser.add_argument("--max_retries", type=int, default=3)
    parser.add_argument("--retry_sleep", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=8,
                        help="Number of parallel workflow-induction API calls")
    args = parser.parse_args()

    induce_all_workflows(args)
