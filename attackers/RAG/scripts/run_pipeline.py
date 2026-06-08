"""
run_pipeline.py
===============
Main pipeline script that orchestrates the full RAG attack build:
  1. copy_and_filter: copy trajectories, filter reward=1, select diverse 8 per task
  2. induce_workflows: compress successful trajectories into MemBank workflows
  3. embed: embed workflow memories
  4. build_index: build FAISS index
  5. retrieve: pre-compute top-k retrieval results (offline)
  6. generate_instruction: create instruction.md files

Usage:
  python -m attackers.RAG.scripts.run_pipeline --top_k 5 --model_name BAAI/bge-m3
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

base = project_root / "attackers" / "RAG"


def load_task_instruction(task_name):
    fpath = project_root / "data" / "tasks" / task_name / "instruction.md"
    if fpath.exists():
        return fpath.read_text().strip()
    return f"[Task: {task_name}]"


def run_step(name, cmd, check=True):
    """Run a shell command and report."""
    print(f"\n{'='*60}")
    print(f"Step: {name}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    result = __import__('subprocess').run(cmd, cwd=str(project_root))
    if check and result.returncode != 0:
        print(f"ERROR: Step '{name}' failed with code {result.returncode}")
        sys.exit(1)
    print(f"Step '{name}' completed successfully")
    return result


def run_pipeline(args):
    """Run the full pipeline."""
    # Step 1: Copy and filter
    source_dir = project_root / args.source_dir
    data_dir = base / "membank" / "source_trajectories"
    outputs_dir = base / "outputs"
    membank_path = base / "membank" / "workflows.jsonl"

    run_step("Copy & Filter (reward=1, diverse up to 8 per task)",
             [sys.executable, "-m", "attackers.RAG.src.copy_and_filter",
              "--src_base", str(source_dir),
              "--dst_base", "attackers/RAG/membank/source_trajectories",
              "--max_per_task", str(args.max_per_task)])

    # Step 2: Induce workflow memories
    induce_cmd = [
        sys.executable, "-m", "attackers.RAG.src.induce_workflows",
        "--data_dir", "attackers/RAG/membank/source_trajectories",
        "--output", "attackers/RAG/membank/workflows.jsonl",
        "--max_per_task", str(args.max_per_task),
        "--max_trace_chars", str(args.max_trace_chars),
        "--max_new_tokens", str(args.max_new_tokens),
        "--generator_model", args.generator_model,
        "--max_retries", str(args.max_retries),
        "--retry_sleep", str(args.retry_sleep),
        "--workers", str(args.workers),
    ]
    if args.generator_api_base:
        induce_cmd.extend(["--api_base", args.generator_api_base])
    if args.generator_api_key:
        induce_cmd.extend(["--api_key", args.generator_api_key])

    run_step("Induce workflow memories", induce_cmd)

    embed_input = "attackers/RAG/membank/workflows.jsonl"
    embed_text_field = "text_for_embedding"
    embed_output_prefix = "embeddings_workflows"
    index_data_dir = "attackers/RAG/membank"
    embedding_prefix = "embeddings_workflows"
    index_name = "workflows"
    index_dir = base / "index" / index_name

    # Step 3: Embed
    embed_cmd = [
        sys.executable, "-m", "attackers.RAG.src.embed",
        "--input_path", embed_input,
        "--text_field", embed_text_field,
        "--output_prefix", embed_output_prefix,
        "--model_name", args.model_name,
        "--batch_size", str(args.batch_size)
    ]
    if args.use_api:
        embed_cmd.append("--use_api")
        if args.api_base:
            embed_cmd.extend(["--api_base", args.api_base])
        if args.api_key:
            embed_cmd.extend(["--api_key", args.api_key])

    run_step(f"Embed workflow records with {args.model_name}", embed_cmd)

    # Step 4: Build index
    run_step("Build FAISS index",
             [sys.executable, "-m", "attackers.RAG.src.build_index",
              "--data_dir", index_data_dir,
              "--embedding_prefix", embedding_prefix,
              "--index_name", index_name])

    # Step 5: Pre-compute top-k retrieval for each task
    print("\n" + "="*60)
    print("Step: Pre-compute top-k retrieval for each task")
    print("="*60)

    # Get all tasks
    tasks = sorted([d for d in os.listdir(str(data_dir))
                   if os.path.isdir(data_dir / d) and not d.startswith('.')])

    # Import retrieval inline to avoid path issues
    sys.path.insert(0, str(base / "src"))
    from retrieve import retrieve_for_task

    retrieve_results = {}
    for task in tasks:
        instruction = load_task_instruction(task)

        try:
            results = retrieve_for_task(
                task_name=task,
                task_instruction=instruction,
                index_dir=index_dir,
                k=args.top_k,
                model_name=args.model_name,
                use_api=args.use_api,
                api_base=args.api_base,
                api_key=args.api_key,
                retrieval_scope=args.retrieval_scope,
                query_instruction=args.query_instruction,
            )
        except Exception as e:
            print(f"  Warning: Retrieval failed for {task}: {e}")
            results = []

        retrieve_results[task] = results

        task_output_dir = outputs_dir / task
        task_output_dir.mkdir(parents=True, exist_ok=True)
        with open(task_output_dir / "retrieval_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"  Retrieved {len(results)} workflow records for task: {task}")

    # Step 6: Generate instruction.md files
    print("\n" + "="*60)
    print("Step: Generate instruction.md files")
    print("="*60)

    from generate_instruction import (
        generate_all_instructions, load_task_instruction, load_record_texts
    )

    record_texts = load_record_texts(
        membank_path=membank_path,
    )

    task_instructions = {}
    for task in tasks:
        task_instructions[task] = load_task_instruction(task)

    outputs = generate_all_instructions(
        retrieve_results,
        task_instructions,
        record_texts,
        output_base=outputs_dir,
    )

    print(f"\n{'='*60}")
    print("Pipeline Complete!")
    print(f"{'='*60}")
    print(f"Generated {len(outputs)} instruction.md files in:")
    print(f"  {outputs_dir}")
    print("\nNext step: Use these instruction.md files as input to the student agent evaluation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full RAG pipeline")
    parser.add_argument("--source_dir", type=str, default="attackers/RAG/data/conversations-clean",
                        help="Source trajectory tree to scan for reward=1 trajectories")
    parser.add_argument("--top_k", type=int, default=5,
                        help="Number of records to retrieve per task")
    parser.add_argument("--model_name", type=str, default="BAAI/bge-m3",
                        help="Embedding model name")
    parser.add_argument("--retrieval_scope", type=str, default="same_task", choices=["same_task", "global"])
    parser.add_argument("--query_instruction", type=str,
                        default="Retrieve reusable workflow memories that help solve the given benchmark task.")
    parser.add_argument("--use_api", action="store_true",
                        help="Use API for embedding instead of local model")
    parser.add_argument("--api_base", type=str, default=None,
                        help="API base URL for embedding")
    parser.add_argument("--api_key", type=str, default=None,
                        help="API key for embedding")
    parser.add_argument("--batch_size", type=int, default=32,
                        help="Batch size for embedding")
    parser.add_argument("--max_per_task", type=int, default=8,
                        help="Maximum successful trajectories/workflows per task")
    parser.add_argument("--generator_model", type=str, default="gpt-5.4",
                        help="OpenAI-compatible chat model for workflow induction")
    parser.add_argument("--generator_api_base", type=str, default=None,
                        help="OpenAI-compatible base URL for workflow induction; defaults to OPENAI_BASE_URL")
    parser.add_argument("--generator_api_key", type=str, default=None,
                        help="OpenAI-compatible API key for workflow induction; defaults to OPENAI_API_KEY")
    parser.add_argument("--max_trace_chars", type=int, default=12000)
    parser.add_argument("--max_new_tokens", type=int, default=1200)
    parser.add_argument("--max_retries", type=int, default=3)
    parser.add_argument("--retry_sleep", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=8,
                        help="Number of parallel workflow-induction API calls")

    args = parser.parse_args()
    run_pipeline(args)
