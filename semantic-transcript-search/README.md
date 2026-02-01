# Semantic Transcript Search (RAG)

This project enables semantic search over movie dialogue transcripts.
Each transcript file represents one shot.

## Pipeline

Transcript → Emotion Inference (Gemini)
→ Semantic Description (Gemini)
→ Embedding (SentenceTransformer)
→ FAISS Vector DB
→ Natural Language Search (Streamlit)

## Features

- No video required
- Emotion inferred from dialogue
- Fully local execution
- RAG-based semantic retrieval

## Run

pip install -r requirements.txt
python build_shots.py
python semantic_search.py
streamlit run app.py
