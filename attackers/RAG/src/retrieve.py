"""
retrieve.py
===========
Offline top-k retrieval for RAG-based attacker.
Retrieves AWM-style workflow memories from the MemBank index.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HF_CACHE_DIR = os.environ.get("HF_CACHE_DIR", str(Path.home() / ".cache" / "huggingface"))


def load_index_and_meta(index_dir):
    """Load FAISS index and workflow metadata."""
    index_path = index_dir / "index.faiss"
    meta_path = index_dir / "record_meta.json"

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found at {index_path}. Run build_index.py first.")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found at {meta_path}.")

    import faiss
    index = faiss.read_index(str(index_path))

    with open(meta_path) as f:
        records_meta = json.load(f)

    return index, records_meta


def format_query(query, query_instruction=None):
    if not query_instruction:
        return query
    return f"Instruct: {query_instruction}\nQuery: {query}"


def get_query_embedding(query, model_name, use_api=False, api_base=None, api_key=None, query_instruction=None):
    """Get embedding for a query string."""
    query = format_query(query, query_instruction=query_instruction)
    if use_api:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=api_base)
        response = client.embeddings.create(model=model_name, input=[query])
        return np.array(response.data[0].embedding, dtype=np.float32)
    else:
        from sentence_transformers import SentenceTransformer
        model_path = HF_CACHE_DIR if Path(HF_CACHE_DIR).exists() else model_name
        try:
            encoder = SentenceTransformer(model_path, cache_folder=HF_CACHE_DIR, trust_remote_code=True)
        except TypeError:
            encoder = SentenceTransformer(model_path, cache_folder=HF_CACHE_DIR)
        emb = encoder.encode([query])
        return np.array(emb[0], dtype=np.float32)


def retrieve_top_k(query, index, records_meta, k=5, model_name=None, use_api=False,
                   api_base=None, api_key=None, query_instruction=None, search_k=None):
    """Retrieve top-k records for a query."""
    # Get query embedding
    query_emb = get_query_embedding(query, model_name, use_api, api_base, api_key, query_instruction)
    query_emb = query_emb.reshape(1, -1).astype(np.float32)

    # Normalize if using cosine
    norms = np.linalg.norm(query_emb, axis=1, keepdims=True)
    norms[norms == 0] = 1
    query_emb_norm = query_emb / norms

    # Search
    if search_k is None:
        search_k = k
    search_k = min(search_k, index.ntotal)
    D, I = index.search(query_emb_norm, search_k)

    results = []
    for rank, (dist, idx) in enumerate(zip(D[0], I[0])):
        if 0 <= idx < len(records_meta):
            meta = records_meta[idx]
            item = dict(meta)
            item.update({
                "rank": rank + 1,
                "record_id": meta.get("workflow_id", ""),
                "workflow_id": meta.get("workflow_id", ""),
                "task": meta.get("task", ""),
                "trajectory_id": meta.get("trajectory_id", ""),
                "source_trajectory_id": meta.get("source_trajectory_id", meta.get("trajectory_id", "")),
                "source_file": meta.get("source_file", ""),
                "agent_name": meta.get("agent_name", ""),
                "model_name": meta.get("model_name", ""),
                "reward": meta.get("reward"),
                "distance": float(dist),
                "text": ""  # Text loaded later by generate_instruction
            })
            results.append(item)
            if len(results) >= k:
                break

    return results


def retrieve_for_task(task_name, task_instruction, index_dir, k=5, model_name=None,
                      use_api=False, api_base=None, api_key=None,
                      retrieval_scope="same_task", query_instruction=None):
    """
    Retrieve top-k records for a task given its instruction.
    Returns list of top-k result dicts (without text - text loaded separately).
    """
    index, records_meta = load_index_and_meta(index_dir)

    if retrieval_scope not in {"same_task", "global"}:
        raise ValueError("retrieval_scope must be 'same_task' or 'global'")

    search_k = index.ntotal if retrieval_scope == "same_task" else k
    all_results = retrieve_top_k(
        task_instruction,
        index,
        records_meta,
        k=search_k,
        model_name=model_name,
        use_api=use_api,
        api_base=api_base,
        api_key=api_key,
        query_instruction=query_instruction,
        search_k=search_k,
    )

    results = []
    for r in all_results:
        if retrieval_scope == "global" or r["task"] == task_name:
            results.append(r)
            if len(results) >= k:
                break

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, help="Task name")
    parser.add_argument("--instruction", type=str, required=True, help="Task instruction text")
    parser.add_argument("--index_dir", type=str, default="attackers/RAG/index/workflows")
    parser.add_argument("--k", type=int, default=5, help="Number of workflow memories to retrieve")
    parser.add_argument("--model_name", type=str, default="BAAI/bge-m3")
    parser.add_argument("--retrieval_scope", type=str, default="same_task", choices=["same_task", "global"])
    parser.add_argument("--query_instruction", type=str,
                        default="Retrieve reusable workflow memories that help solve the given benchmark task.")
    parser.add_argument("--use_api", action="store_true")
    parser.add_argument("--api_base", type=str, default=None)
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    base = Path(__file__).parent.parent.parent.parent
    index_dir = base / args.index_dir

    results = retrieve_for_task(
        task_name=args.task,
        task_instruction=args.instruction,
        index_dir=index_dir,
        k=args.k,
        model_name=args.model_name,
        use_api=args.use_api,
        api_base=args.api_base,
        api_key=args.api_key,
        retrieval_scope=args.retrieval_scope,
        query_instruction=args.query_instruction,
    )

    print(f"\nTop {len(results)} retrieved records for task: {args.task}")
    for r in results:
        print(f"  [{r['rank']}] id={r['record_id']}, task={r['task']}, dist={r['distance']:.4f}")

    if args.output:
        output_path = base / args.output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_path}")
