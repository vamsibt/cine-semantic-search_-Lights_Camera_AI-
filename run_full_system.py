import os
import json
import subprocess

from pipeline.extract_audio import extract_audio
from pipeline.transcribe_audio import transcribe
from pipeline.pause_detection import detect_silence_from_transcript

# ---------------- CONFIG ----------------
DATA_DIR = "data"
OUTPUTS_DIR = "outputs"

SEMANTIC_DIR = "semantic-transcript-search"
TRANSCRIPTS_DIR = os.path.join(SEMANTIC_DIR, "transcripts")

# ----------------------------------------

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)


def process_video(video_file):
    video_name = os.path.splitext(video_file)[0]
    video_path = os.path.join(DATA_DIR, video_file)

    print(f"\n🎬 Processing video: {video_file}")

    # per-video output dir
    video_out_dir = os.path.join(OUTPUTS_DIR, video_name)
    os.makedirs(video_out_dir, exist_ok=True)

    audio_path = os.path.join(video_out_dir, "audio.wav")
    transcript_path = os.path.join(video_out_dir, "transcript.json")
    timeline_path = os.path.join(video_out_dir, "timeline.json")

    if os.path.exists(timeline_path):
        print(f"⏭️ Skipping {video_file} (already processed)")
        return
    # 1️⃣ Extract audio
    extract_audio(video_path, audio_path)

    # 2️⃣ Transcribe
    transcribe(audio_path, transcript_path)

    # 3️⃣ Generate timeline
    with open(transcript_path) as f:
        transcript = json.load(f)

    timeline = detect_silence_from_transcript(transcript)

    with open(timeline_path, "w") as f:
        json.dump(timeline, f, indent=2)

    # 4️⃣ Push timeline into semantic pipeline
    semantic_timeline = os.path.join(
        TRANSCRIPTS_DIR, f"{video_name}_timeline.json"
    )

    with open(semantic_timeline, "w") as f:
        json.dump(timeline, f, indent=2)

    print(f"✅ Timeline ready for semantic search: {semantic_timeline}")


def run_semantic_pipeline():
    print("\n🧠 Building shots...")
    subprocess.run(
        ["python", "build_shots.py"],
        cwd=SEMANTIC_DIR,
        check=True
    )

    print("\n📦 Indexing shots into FAISS...")
    subprocess.run(
        ["python", "-c",
         "from semantic_search import ingest_shots_folder; ingest_shots_folder()"],
        cwd=SEMANTIC_DIR,
        check=True
    )


if __name__ == "__main__":
    print("\n🚀 STARTING FULL PIPELINE")

    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".mp4"):
            process_video(file)

    run_semantic_pipeline()

    print("\n✅ FULL SYSTEM COMPLETED SUCCESSFULLY")
