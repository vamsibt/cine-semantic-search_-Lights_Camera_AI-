from faster_whisper import WhisperModel
import json
import os

def transcribe(audio_path, out_path):
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path)

    transcript = []
    for seg in segments:
        transcript.append({
            "text": seg.text,
            "start": seg.start,
            "end": seg.end
        })

    with open(out_path, "w") as f:
        json.dump(transcript, f, indent=2)


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    transcribe("outputs/audio.wav", "outputs/transcript.json")
    print("✅ Transcript generated")
