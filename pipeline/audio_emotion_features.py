import os
import json
import numpy as np
import librosa
import tensorflow as tf

# ================= CONFIG =================
AUDIO_PATH = "outputs/audio.wav"
TRANSCRIPT_PATH = "outputs/transcript.json"
MODEL_PATH = "models/model3_2.h5"
OUTPUT_PATH = "outputs/audio_emotion_segments.json"

SAMPLE_RATE = 22050
N_MELS = 128
TARGET_FRAMES = 282

EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust"]
# ==========================================


def extract_mel_segment(y, sr):
    mel = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=N_MELS,
        fmax=8000
    )

    mel_db = librosa.power_to_db(mel, ref=np.max)

    # pad / trim time axis
    if mel_db.shape[1] < TARGET_FRAMES:
        pad_width = TARGET_FRAMES - mel_db.shape[1]
        mel_db = np.pad(mel_db, ((0, 0), (0, pad_width)))
    else:
        mel_db = mel_db[:, :TARGET_FRAMES]

    mel_db = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min() + 1e-6)

    mel_db = np.expand_dims(mel_db, axis=-1)
    mel_db = np.expand_dims(mel_db, axis=0)

    return mel_db


def main():
    print("🔥 Segment-level audio emotion extraction 🔥")

    model = tf.keras.models.load_model(MODEL_PATH)

    y, sr = librosa.load(AUDIO_PATH, sr=SAMPLE_RATE)

    with open(TRANSCRIPT_PATH, "r") as f:
        transcript = json.load(f)

    results = []

    for seg in transcript:
        start = float(seg["start"])
        end = float(seg["end"])

        start_sample = int(start * sr)
        end_sample = int(end * sr)

        if end_sample <= start_sample:
            continue

        y_seg = y[start_sample:end_sample]

        # skip tiny segments
        if len(y_seg) < sr * 0.3:
            continue

        features = extract_mel_segment(y_seg, sr)

        preds = model.predict(features, verbose=0)[0]
        idx = int(np.argmax(preds))

        results.append({
            "start": start,
            "end": end,
            "text": seg["text"],
            "emotion": EMOTIONS[idx],
            "confidence": float(preds[idx]),
            "scores": {
                EMOTIONS[i]: float(preds[i]) for i in range(len(preds))
            }
        })

    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Saved {len(results)} segment emotions → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
