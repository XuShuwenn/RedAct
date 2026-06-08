"""
build_index.py
==============
Build FAISS index from embedded JSONL records.
Saves index to ../index/{index_name}/index.faiss
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HF_CACHE_DIR = os.environ.get("HF_CACHE_DIR", str(Path.home() / ".cache" / "huggingface"))


def load_embeddings_and_meta(data_dir, embedding_prefix="embeddings_workflows"):
    """Load embeddings and metadata from data directory."""
    import faiss

    # Resolve embedding_prefix the same way embed.py does
    emb_prefix_path = Path(embedding_prefix)
    if not emb_prefix_path.is_absolute() and emb_prefix_path.parts and emb_prefix_path.parts[0] == "attackers":
        project_root = Path(__file__).parent.parent.parent.parent
        emb_prefix_path = project_root / emb_prefix_path

    emb_path = data_dir / f"{emb_prefix_path.name}.npy"
    meta_path = data_dir / f"{emb_prefix_path.name}_meta.jsonl"

    if not emb_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Embeddings not found at {emb_path}. Run embed.py first.")

    embeddings = np.load(emb_path)
    records_meta = []
    with open(meta_path) as f:
        for line in f:
            records_meta.append(json.loads(line))

    return embeddings, records_meta


def build_faiss_index(embeddings, metric="cosine"):
    """Build FAISS index from embeddings."""
    try:
        import faiss
    except ImportError:
        raise ImportError("pip install faiss-cpu or faiss-gpu")

    dim = embeddings.shape[1]
    num_vectors = embeddings.shape[0]

    if metric == "cosine":
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings_norm = embeddings / norms
        index = faiss.IndexFlatIP(dim)  # Inner product (cosine for normalized)
        index.add(embeddings_norm.astype(np.float32))
    else:
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings.astype(np.float32))

    return index


def save_index(index, output_path):
    """Save FAISS index to disk."""
    import faiss
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    faiss.write_index(index, str(output_path))
    print(f"Index saved to: {output_path}")


def build_task_index(data_dir, task_name=None, embedding_prefix="embeddings_workflows", index_name=None):
    """Build FAISS index for embedded records."""
    embeddings, records_meta = load_embeddings_and_meta(data_dir, embedding_prefix=embedding_prefix)

    index = build_faiss_index(embeddings)
    print(f"Index built with {index.ntotal} vectors, dim={embeddings.shape[1]}")

    # Save index
    if index_name is None:
        index_name = task_name or "all"
    # Save index to attackers/RAG/index/{index_name}/ (not under data_dir.parent)
    project_root = Path(__file__).parent.parent.parent.parent
    index_dir = project_root / "attackers" / "RAG" / "index" / index_name
    os.makedirs(str(index_dir), exist_ok=True)
    index_path = index_dir / "index.faiss"
    save_index(index, str(index_path))

    # Save metadata mapping
    meta_map_path = index_dir / "record_meta.json"
    with open(meta_map_path, "w") as f:
        json.dump(records_meta, f, indent=2)
    print(f"Record metadata saved to: {meta_map_path}")

    return index_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="attackers/RAG/membank")
    parser.add_argument("--task", type=str, default=None, help="Task name (optional)")
    parser.add_argument("--embedding_prefix", type=str, default="embeddings_workflows")
    parser.add_argument("--index_name", type=str, default="workflows")
    args = parser.parse_args()

    base = Path(__file__).parent.parent.parent.parent
    data_dir = base / args.data_dir

    build_task_index(
        data_dir,
        task_name=args.task,
        embedding_prefix=args.embedding_prefix,
        index_name=args.index_name,
    )
