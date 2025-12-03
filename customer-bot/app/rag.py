# app/rag.py
from pathlib import Path
import json
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm
import numpy as np
from app.pdf_utils import extract_pdf_text, mask_text_simple
from typing import List, Tuple

MODEL_NAME = "all-MiniLM-L6-v2"
BASE = Path(__file__).resolve().parents[1]
INDEX_PATH = BASE / "data" / "faiss_index.bin"
DOCS_PATH = BASE / "data" / "rag_docs.json"
EMB_PATH = BASE / "data" / "embeddings.npy"

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    words = text.split()
    i = 0
    chunks = []
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def build_index(docs_dir: str = "data/docs", model_name: str = MODEL_NAME):
    docs_dir = Path(docs_dir)
    model = SentenceTransformer(model_name)
    texts = []
    metadata = []

    files = sorted([p for p in docs_dir.iterdir() if p.suffix.lower() in (".pdf", ".txt")])
    if not files:
        raise RuntimeError("No docs found to index in data/docs/")

    for f in tqdm(files, desc="Batches"):
        fname = f.name
        customer_id = None
        if fname.startswith("cust_"):
            parts = fname.split("_")
            if len(parts) >= 2:
                customer_id = parts[1]

        if f.suffix.lower() == ".pdf":
            plain = extract_pdf_text(f)
        else:
            plain = f.read_text(encoding="utf8")
        if not plain.strip():
            continue
        masked_plain = mask_text_simple(plain)
        chunks = _chunk_text(masked_plain, chunk_size=300, overlap=50)
        for idx, c in enumerate(chunks):
            texts.append(c)
            metadata.append({"source": str(fname), "chunk": idx, "customer_id": customer_id})

    if not texts:
        raise RuntimeError("No text chunks were generated for indexing.")

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(DOCS_PATH, "w", encoding="utf8") as fh:
        json.dump({"texts": texts, "metadata": metadata}, fh, ensure_ascii=False)
    np.save(str(EMB_PATH), embeddings)
    print(f"Index built with {len(texts)} chunks. Saved to {INDEX_PATH}")

def load_index(model_name: str = MODEL_NAME):
    if not INDEX_PATH.exists() or not DOCS_PATH.exists():
        raise RuntimeError("Index or docs not found. Run: python -m app.rag build")
    model = SentenceTransformer(model_name)
    index = faiss.read_index(str(INDEX_PATH))
    with open(DOCS_PATH, "r", encoding="utf8") as fh:
        data = json.load(fh)
    return model, index, data["texts"], data["metadata"]

def query(text: str, k: int = 3, model_name: str = MODEL_NAME, customer_id: str | None = None) -> List[Tuple[str, dict, float]]:
    """
    Returns top-k (text_chunk, metadata, score) optionally filtered by customer_id.
    """
    model, index, texts, metad = load_index(model_name)
    q_emb = model.encode([text], convert_to_numpy=True)
    D, I = index.search(q_emb, k * 5)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(texts):
            continue
        md = metad[idx]
        if customer_id and md.get("customer_id") != customer_id:
            continue
        results.append((texts[idx], md, float(score)))
        if len(results) >= k:
            break
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build_index()
    else:
        print("Usage: python -m app.rag build")
