from moviepy.editor import VideoFileClip
import numpy as np
from moviepy.editor import AudioClip
import os


def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)

    if clip.audio is not None:
        clip.audio.write_audiofile(audio_path)
    else:
        duration = clip.duration

        def silence(t):
            return np.zeros((1,), dtype=np.float32)

        silent_audio = AudioClip(silence, duration=duration, fps=16000)
        silent_audio.write_audiofile(audio_path)

    clip.close()


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    extract_audio(
        "data\Best_Argument_Scene_in_Marriage_Story_Netflix_-_Part_1_720P.mp4",
        "outputs/audio.wav",
    )
    print("✅ Audio extracted")
