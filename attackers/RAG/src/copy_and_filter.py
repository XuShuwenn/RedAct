"""Collect successful trajectories for workflow-memory induction."""

import argparse
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_SRC_BASE = PROJECT_ROOT / "attackers" / "RAG" / "data" / "conversations-clean"
DEFAULT_DST_BASE = PROJECT_ROOT / "attackers" / "RAG" / "membank" / "source_trajectories"
MAX_TRAJS_PER_TASK = 8


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_reward(traj):
    return traj.get("meta_info", {}).get("reward")


def get_agent_model(traj):
    meta = traj.get("meta_info", {})
    agent = traj.get("agent_name") or meta.get("agent") or meta.get("agent_name") or "unknown"
    model = traj.get("model_name") or meta.get("model") or meta.get("model_name") or "unknown"
    return str(agent), str(model).replace("/", "-")


def collect_reward1_trajs(src_base):
    """Collect reward=1 trajectories under a nested or flat source tree."""
    groups = defaultdict(lambda: defaultdict(list))  # task -> (harness,model) -> [traj_paths]

    for fpath in sorted(Path(src_base).rglob("*.json")):
        try:
            traj = load_json(fpath)
        except Exception as e:
            print(f"Error reading {fpath}: {e}")
            continue

        if get_reward(traj) != 1:
            continue

        task = traj.get("task_name") or fpath.parent.name
        agent, model = get_agent_model(traj)
        groups[task][(agent, model)].append({
            "path": str(fpath),
            "harness": agent,
            "model": model,
            "fname": fpath.name,
            "turn_count": traj.get("turn_count", len(traj.get("turns", []))),
            "chars": sum(len(t.get("content", "") or "") for t in traj.get("turns", [])),
        })

    return groups


def select_diverse_trajs(trajs_by_hm, max_total=MAX_TRAJS_PER_TASK):
    """
    Select up to max_total trajectories, ensuring diverse (harness, model) coverage.
    Strategy: round-robin across (harness, model) groups, then fill remaining slots.
    """
    hm_groups = list(trajs_by_hm.items())  # list of ((harness, model), trajs)
    selected = []

    # Round-robin: take up to ceil(max_total / num_groups) from each group
    num_groups = len(hm_groups)
    if num_groups == 0:
        return []

    per_group_target = (max_total + num_groups - 1) // num_groups

    for (hm, trajs) in hm_groups:
        # Sort by char count (prefer medium-length trajectories)
        trajs_sorted = sorted(trajs, key=lambda x: x["chars"])
        taken = trajs_sorted[:per_group_target]
        selected.extend(taken)

    # If still under limit, keep adding in order
    if len(selected) < max_total:
        remaining = []
        for (hm, trajs) in hm_groups:
            already_selected = set(x["path"] for x in selected)
            remaining.extend([t for t in trajs if t["path"] not in already_selected])
        remaining.sort(key=lambda x: x["chars"])
        selected.extend(remaining[:max_total - len(selected)])

    return selected[:max_total]


def unique_destination(task_dst, fname):
    stem = Path(fname).stem
    suffix = Path(fname).suffix
    dst = task_dst / fname
    i = 1
    while dst.exists():
        dst = task_dst / f"{stem}__dup{i}{suffix}"
        i += 1
    return dst


def run(src_base=DEFAULT_SRC_BASE, dst_base=DEFAULT_DST_BASE, max_per_task=MAX_TRAJS_PER_TASK):
    src_base = Path(src_base)
    dst_base = Path(dst_base)
    if not src_base.exists():
        raise FileNotFoundError(f"Source trajectory directory not found: {src_base}")

    if dst_base.exists():
        shutil.rmtree(dst_base)
    os.makedirs(dst_base, exist_ok=True)

    groups = collect_reward1_trajs(src_base)

    task_stats = {}
    total_copied = 0

    for task in sorted(groups.keys()):
        trajs_by_hm = groups[task]

        # Select diverse trajectories
        selected = select_diverse_trajs(trajs_by_hm, max_total=max_per_task)

        # Copy to destination
        task_dst = dst_base / task
        os.makedirs(task_dst, exist_ok=True)

        for traj_info in selected:
            src = traj_info["path"]
            dst = unique_destination(task_dst, traj_info["fname"])
            shutil.copy2(src, dst)

        task_stats[task] = {
            "num_copied": len(selected),
            "num_hm_groups": len(trajs_by_hm),
            "hm_groups": [(hm, len(t)) for hm, t in trajs_by_hm.items()]
        }
        total_copied += len(selected)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Copy & Filter Complete")
    print(f"{'='*60}")
    print(f"Total tasks processed: {len(task_stats)}")
    print(f"Total trajectories copied: {total_copied}")
    print(f"\nPer-task summary (first 20):")
    for task, stat in sorted(task_stats.items(), key=lambda x: -x[1]["num_copied"])[:20]:
        print(f"  {task}: {stat['num_copied']} trajs, {stat['num_hm_groups']} hm-groups")

    # Save metadata
    meta_path = dst_base / "_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(task_stats, f, indent=2)
    print(f"\nMetadata saved to: {meta_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect reward=1 trajectories for MemBank induction")
    parser.add_argument("--src_base", type=str, default=str(DEFAULT_SRC_BASE))
    parser.add_argument("--dst_base", type=str, default=str(DEFAULT_DST_BASE))
    parser.add_argument("--max_per_task", type=int, default=MAX_TRAJS_PER_TASK)
    args = parser.parse_args()
    run(src_base=args.src_base, dst_base=args.dst_base, max_per_task=args.max_per_task)
