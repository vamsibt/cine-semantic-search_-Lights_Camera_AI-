import os
import json
from semantic_search import infer_emotion_from_dialogue

TRANSCRIPTS_DIR = "transcripts"
SHOTS_DIR = "shots"

os.makedirs(SHOTS_DIR, exist_ok=True)


def transcript_to_signals(timeline):
    dialogue = []
    silences = []

    for item in timeline:
        if item["type"] == "Speech":
            dialogue.append(item.get("text", "").strip())
        elif item["type"] == "Silence":
            silences.append(item["duration"])

    full_dialogue = " ".join(dialogue)
    emotion = infer_emotion_from_dialogue(full_dialogue)

    return {
        "dialogue": full_dialogue,
        "pause_duration": max(silences) if silences else 0,
        "emotion": emotion["emotion"],
        "emotional_intensity": emotion["emotional_intensity"],
        "tone": emotion["tone"],
    }


# 🔥 LOAD EXISTING SHOTS (IMPORTANT)
existing_videos = set()

for file in os.listdir(SHOTS_DIR):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(SHOTS_DIR, file), "r") as f:
        shot = json.load(f)

    video_file_name = shot.get(
        "video_file_name",
        os.path.basename(shot.get("source_video", ""))
    )

    if video_file_name:
        existing_videos.add(video_file_name)



shot_counter = len(existing_videos) + 1

for file in sorted(os.listdir(TRANSCRIPTS_DIR)):
    if not file.endswith("_timeline.json"):
        continue

    video_name = file.replace("_timeline.json", "")
    video_file_name = f"{video_name}.mp4"

    # 🔥 SKIP IF SHOT ALREADY EXISTS
    if video_file_name in existing_videos:
        print(f"⏭️ Skipping {video_file_name} (shot already exists)")
        continue

    with open(os.path.join(TRANSCRIPTS_DIR, file), "r") as f:
        timeline = json.load(f)

    shot_data = {
        "shot_id": f"shot{shot_counter}",
        "source_video": f"data/{video_file_name}",
        "start_time": 0.0,
        "end_time": max(seg["end"] for seg in timeline),
        "source_timeline": file,
        "signals": transcript_to_signals(timeline),
    }

    shot_path = os.path.join(SHOTS_DIR, f"shot{shot_counter}.json")

    with open(shot_path, "w") as f:
        json.dump(shot_data, f, indent=2)

    print(f"✅ Created {shot_path}")

    shot_counter += 1
    existing_videos.add(video_file_name)
