#!/usr/bin/env python3
"""Per-task retrieval + instruction.md generation for RAG pipeline."""
import sys, json, os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAG_ROOT = PROJECT_ROOT / "attackers" / "RAG"

os.environ.setdefault("HF_CACHE_DIR", str(Path.home() / ".cache" / "huggingface"))
os.environ.setdefault("HOME", str(Path.home()))

sys.path.insert(0, str(PROJECT_ROOT))

from attackers.RAG.src.retrieve import retrieve_for_task
from attackers.RAG.src.generate_instruction import (
    load_task_instruction, load_record_texts, generate_all_instructions
)

task = sys.argv[1]
top_k = int(sys.argv[2])
model_name = sys.argv[3]
retrieval_scope = sys.argv[4]
query_instruction = sys.argv[5]
# Optional override: index_dir, output_base, membank_path
index_dir_arg = sys.argv[6] if len(sys.argv) > 6 else None
output_base_arg = sys.argv[7] if len(sys.argv) > 7 else None
membank_arg = sys.argv[8] if len(sys.argv) > 8 else None

instruction = load_task_instruction(task)
results = retrieve_for_task(
    task_name=task,
    task_instruction=instruction,
    index_dir=Path(index_dir_arg) if index_dir_arg else RAG_ROOT / "index" / "workflows",
    k=top_k,
    model_name=model_name,
    retrieval_scope=retrieval_scope,
    query_instruction=query_instruction,
)

output_base = Path(output_base_arg) if output_base_arg else RAG_ROOT / "outputs"
out_dir = output_base / task
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / "retrieval_results.json", "w") as f:
    json.dump(results, f, indent=2)

membank = Path(membank_arg) if membank_arg else RAG_ROOT / "membank" / "workflows.jsonl"
record_texts = load_record_texts(membank_path=membank)
generate_all_instructions(
    {task: results}, {task: instruction}, record_texts,
    output_base=output_base
)
print(f"  {task}: {len(results)} workflows retrieved")
