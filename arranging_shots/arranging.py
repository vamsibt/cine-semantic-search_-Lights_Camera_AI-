import os
import json
import re
from rapidfuzz import fuzz

SCRIPT_FILE = "Dark_Knight_Shots.txt"
SHOTS_DIR = "shots"


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Load script
with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
    raw_script = f.read()

# Split script by explicit Shot markers
shot_sections = re.split(r"(Shot\s+\d+\s*:)", raw_script)

script_shots = []
for i in range(1, len(shot_sections), 2):
    shot_title = shot_sections[i]
    shot_text = shot_sections[i + 1]
    shot_number = int(re.search(r"\d+", shot_title).group())
    script_shots.append({"shot_number": shot_number, "text": normalize(shot_text)})

results = []

for file in os.listdir(SHOTS_DIR):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(SHOTS_DIR, file), "r", encoding="utf-8") as f:
        shot = json.load(f)

    dialogue = normalize(shot["signals"]["dialogue"])
    shot_id = shot["shot_id"]

    best_score = 0
    best_script_shot = None

    for section in script_shots:
        score = fuzz.partial_ratio(dialogue, section["text"])
        if score > best_score:
            best_score = score
            best_script_shot = section["shot_number"]

    if best_score < 60:
        print(f"⚠️ Low confidence for {shot_id} (score={best_score})")
        continue

    results.append(
        {
            "shot_id": shot_id,
            "file": file,
            "script_shot": best_script_shot,
            "score": best_score,
        }
    )

# Sort by script shot number
results.sort(key=lambda x: x["script_shot"])

print("\n🎬 FINAL CORRECT SHOT ORDER:\n")
for i, r in enumerate(results, 1):
    print(
        f"{i}. {r['shot_id']} ({r['file']}) → Script Shot {r['script_shot']}  score={r['score']}"
    )
