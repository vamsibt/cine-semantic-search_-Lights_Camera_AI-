import os
import json
import faiss
import numpy as np
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv  
load_dotenv()
########################################
# CONFIG
########################################
BASE_PATH = os.getcwd()
FAISS_INDEX_FILE = os.path.join(BASE_PATH, "faiss.index")
METADATA_FILE = os.path.join(BASE_PATH, "metadata.json")

# 🔥 ADD YOUR REAL KEYS HERE
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "").split(",")

# Safety check
if not GEMINI_API_KEYS or GEMINI_API_KEYS == [""]:
    raise RuntimeError("❌ No Gemini API keys found in .env")

TOP_K_RESULTS = 1

########################################
# GLOBALS
########################################
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
_current_key_index = 0


########################################
# GEMINI CLIENT ROTATION
########################################
def get_gemini_client():
    global _current_key_index

    if _current_key_index >= len(GEMINI_API_KEYS):
        raise RuntimeError("❌ All Gemini API keys exhausted")

    return genai.Client(api_key=GEMINI_API_KEYS[_current_key_index])


def rotate_key():
    global _current_key_index
    _current_key_index += 1
    print(f"🔁 Switching to Gemini API key #{_current_key_index + 1}")


########################################
# 1. EMOTION INFERENCE
def infer_emotion_from_dialogue(dialogue: str) -> dict:
    prompt = f"""
Analyze the following movie dialogue.

Dialogue:
\"\"\"
{dialogue}
\"\"\"

Return STRICT JSON:
{{
  "emotion": one of [anger, sadness, fear, frustration, hope, resignation, affection, confidence, uncertainty],
  "emotional_intensity": one of [low, medium, high],
  "tone": string
}}
"""

    while True:
        try:
            client = get_gemini_client()

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1, response_mime_type="application/json"
                ),
            )

            if not response.text:
                raise ValueError("Empty response")

            return json.loads(response.text)

        except ClientError as e:
            msg = str(e)

            # 🔥 ROTATE KEY ON QUOTA OR INVALID KEY
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "API key" in msg:
                rotate_key()
                continue

            # Other Gemini errors → real failure
            raise e


########################################
# 2. SEMANTIC DESCRIPTION
########################################
def generate_semantic_description(signals: dict) -> str:
    prompt = f"""
You are analyzing a film scene for semantic search.

Signals:
- Dialogue: "{signals['dialogue']}"
- Dominant emotion: {signals['emotion']}
- Emotional intensity: {signals['emotional_intensity']}
- Tone: {signals['tone']}
- Longest silence: {signals['pause_duration']} seconds

Task:
Write ONE concise sentence describing the emotional intent
and narrative meaning of this moment.
Avoid metaphors. Use neutral language.
"""

    while True:
        try:
            client = get_gemini_client()

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2),
            )

            if not response.text:
                raise ValueError("Empty response")

            return response.text.strip()

        except ClientError as e:
            msg = str(e)

            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "API key" in msg:
                rotate_key()
                continue

            raise e


########################################
# 3. LOAD OR CREATE FAISS
########################################
def load_or_create_faiss():
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
    else:
        index = faiss.IndexFlatL2(embedding_model.get_sentence_embedding_dimension())
        metadata = []

    return index, metadata


########################################
# 4. INGEST SHOTS (INCREMENTAL)
########################################
def ingest_shots_folder(shots_dir="shots"):
    index, metadata = load_or_create_faiss()

    for file in sorted(os.listdir(shots_dir)):
        if not file.endswith(".json"):
            continue

        with open(os.path.join(shots_dir, file), "r") as f:
            shot = json.load(f)

        # 🔥 BACKWARD-COMPATIBLE VIDEO NAME
        video_file_name = shot.get(
            "video_file_name",
            os.path.basename(shot.get("source_video", ""))
        )

        if not video_file_name:
            print(f"⚠️ Skipping {file} (no video reference)")
            continue

        # 🔥 STABLE DEDUP
        if any(m.get("video_file_name") == video_file_name for m in metadata):
            continue

        desc = generate_semantic_description(shot["signals"])
        embedding = embedding_model.encode([desc], convert_to_numpy=True)

        index.add(embedding)

        metadata.append(
            {
                "shot_id": shot["shot_id"],
                "video_file_name": video_file_name,
                "source_video": shot.get("source_video"),
                "description": desc,
            }
        )

        print(f"📌 Indexed {video_file_name}")

    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ FAISS index updated")

########################################
# 5. SEMANTIC SEARCH
########################################
def semantic_search(query: str, index, metadata, k=TOP_K_RESULTS):
    if index.ntotal == 0:
        return []

    query_vec = embedding_model.encode([query], convert_to_numpy=True)
    k = min(k, index.ntotal)

    _, indices = index.search(query_vec, k)
    return [metadata[i] for i in indices[0] if i != -1]
