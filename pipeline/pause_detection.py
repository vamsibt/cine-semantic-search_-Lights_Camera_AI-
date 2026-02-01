import json

INPUT_TRANSCRIPT = "outputs/transcript.json"
OUTPUT_TIMELINE = "outputs/timeline.json"


def detect_silence_from_transcript(transcript, video_end_time=None):
    timeline = []

    for i in range(len(transcript)):
        current = transcript[i]

        # Add speech segment
        timeline.append({
            "type": "Speech",
            "start": round(current["start"], 2),
            "end": round(current["end"], 2),
            "text": current.get("text", "")
        })

        # Add silence between speeches
        if i < len(transcript) - 1:
            next_seg = transcript[i + 1]
            if next_seg["start"] > current["end"]:
                timeline.append({
                    "type": "Silence",
                    "start": round(current["end"], 2),
                    "end": round(next_seg["start"], 2),
                    "duration": round(next_seg["start"] - current["end"], 2)
                })

    # Optional silence after last speech
    if video_end_time is not None:
        last_end = transcript[-1]["end"]
        if video_end_time > last_end:
            timeline.append({
                "type": "Silence",
                "start": round(last_end, 2),
                "end": round(video_end_time, 2),
                "duration": round(video_end_time - last_end, 2)
            })

    return timeline


if __name__ == "__main__":
    with open(INPUT_TRANSCRIPT, "r") as f:
        transcript = json.load(f)

    timeline = detect_silence_from_transcript(transcript)

    with open(OUTPUT_TIMELINE, "w") as f:
        json.dump(timeline, f, indent=2)

    # Debug print
    for seg in timeline:
        if seg["type"] == "Silence":
            print(f'[SILENCE] {seg["start"]}s → {seg["end"]}s ({seg["duration"]}s)')
