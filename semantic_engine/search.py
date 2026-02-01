import faiss
import numpy as np

def search(query, model, index, descriptions):
    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_emb)

    scores, idxs = index.search(q_emb, 3)

    results = []
    for score, idx in zip(scores[0], idxs[0]):
        results.append({
            "description": descriptions[idx],
            "confidence": float(score)
        })

    return results
