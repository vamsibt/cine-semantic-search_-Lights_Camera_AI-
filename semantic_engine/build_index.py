import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def build_index(descriptions):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(descriptions, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return model, index
