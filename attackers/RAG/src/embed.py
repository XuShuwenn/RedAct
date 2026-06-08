"""
embed.py
========
Embed JSONL records using local Sentence Transformers or API (OpenAI-compatible).

Usage:
  # Local embedding (downloads model on first run to ~/.cache/huggingface or specified dir)
  python -m attackers.RAG.src.embed --input_path attackers/RAG/membank/workflows.jsonl --model_name BAAI/bge-m3

  # API-based embedding
  python -m attackers.RAG.src.embed --use_api --api_base https://api.openai.com/v1 --api_key $OPENAI_API_KEY
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

HF_CACHE_DIR = os.environ.get("HF_CACHE_DIR", str(Path.home() / ".cache" / "huggingface"))


def get_embedding_model(model_name, use_api=False, api_base=None, api_key=None):
    """
    Get embedding model and encode function.
    use_api: if True, use OpenAI-compatible API for embedding.
    """
    if use_api:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("pip install openai")

        client = OpenAI(api_key=api_key, base_url=api_base)
        def encode_texts(texts, model=model_name):
            response = client.embeddings.create(
                model=model,
                input=texts
            )
            return [item.embedding for item in response.data]
        return encode_texts, "api", model_name
    else:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("pip install sentence-transformers")

        print(f"Loading embedding model: {model_name}")
        print(f"Cache dir: {HF_CACHE_DIR}")
        model_path = HF_CACHE_DIR if Path(HF_CACHE_DIR).exists() else model_name
        try:
            encoder = SentenceTransformer(model_path, cache_folder=HF_CACHE_DIR, trust_remote_code=True)
        except TypeError:
            encoder = SentenceTransformer(model_path, cache_folder=HF_CACHE_DIR)

        def encode_texts(texts, model=encoder):
            return model.encode(texts, show_progress_bar=True, batch_size=32).tolist()

        return encode_texts, "local", model_name


def load_records(input_path):
    """Load JSONL records."""
    records = []
    with open(input_path) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def flatten_metadata(record):
    """Remove heavy text fields before saving metadata."""
    meta = {k: v for k, v in record.items() if k not in {"text", "text_for_embedding", "raw_model_output"}}
    nested = meta.pop("metadata", None)
    if isinstance(nested, dict):
        for key, value in nested.items():
            meta.setdefault(key, value)
    return meta


def save_embeddings(records, embeddings, output_path):
    """Save embeddings alongside record metadata."""
    import numpy as np

    # Save numpy array
    emb_array = np.array(embeddings, dtype=np.float32)
    np.save(output_path.with_suffix(".npy"), emb_array)

    # Save metadata (use explicit suffix, not with_suffix which fails on no-suffix paths)
    meta_path = Path(str(output_path) + "_meta.jsonl")
    with open(meta_path, "w") as f:
        for record in records:
            f.write(json.dumps(flatten_metadata(record), ensure_ascii=False) + "\n")

    return output_path, meta_path


def embed_records(input_path, model_name, use_api=False, api_base=None, api_key=None,
                  batch_size=32, text_field="text", output_prefix=None):
    """Embed all records from a JSONL file and save."""
    input_path = Path(input_path)
    print(f"Loading records from: {input_path}")
    records = load_records(input_path)
    texts = [r.get(text_field) or r.get("text") or "" for r in records]
    print(f"Total records to embed: {len(texts)}")
    if not texts:
        raise ValueError(f"No records found in {input_path}")

    encode_fn, mode, model_id = get_embedding_model(model_name, use_api, api_base, api_key)
    print(f"Embedding mode: {mode}, model: {model_id}")

    # Batch embed
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        emb = encode_fn(batch)
        all_embeddings.extend(emb)
        print(f"  Embedded {min(i+batch_size, len(texts))}/{len(texts)} records")

    input_path = Path(input_path).resolve()
    if output_prefix is None:
        output_path = input_path.parent / f"embeddings_{input_path.stem}"
    else:
        output_path = Path(output_prefix)
        if output_path.is_absolute():
            pass
        elif output_path.parts and output_path.parts[0] == "attackers":
            # Path like "attackers/RAG/..." is project-root-relative
            output_path = Path(__file__).parent.parent.parent.parent / output_path
        else:
            output_path = input_path.parent / output_path
    emb_path, meta_path = save_embeddings(records, all_embeddings, output_path)
    print(f"\nEmbeddings saved to: {emb_path}")
    print(f"Metadata saved to: {meta_path}")
    print(f"Embedding shape: {len(all_embeddings)} x {len(all_embeddings[0])}")

    return emb_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, default="attackers/RAG/membank/workflows.jsonl")
    parser.add_argument("--text_field", type=str, default="text_for_embedding")
    parser.add_argument("--output_prefix", type=str, default=None,
                        help="Output prefix without .npy, relative to input directory if not absolute")
    parser.add_argument("--model_name", type=str, default="BAAI/bge-m3")
    parser.add_argument("--use_api", action="store_true")
    parser.add_argument("--api_base", type=str, default=None)
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    # Resolve relative path
    # __file__ = attackers/RAG/src/embed.py -> parent.parent = attackers/RAG -> parent.parent.parent = project_root
    project_root = Path(__file__).parent.parent.parent.parent
    input_path = project_root / args.input_path

    embed_records(
        input_path=str(input_path),
        model_name=args.model_name,
        use_api=args.use_api,
        api_base=args.api_base,
        api_key=args.api_key,
        batch_size=args.batch_size,
        text_field=args.text_field,
        output_prefix=args.output_prefix,
    )
