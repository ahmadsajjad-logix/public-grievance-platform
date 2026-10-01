"""Multilingual speech recognition on the app server, including Community Cloud.

Only public model weights are downloaded. Audio is processed in memory on the
host running Streamlit and is never sent to a separate transcription API.
"""
import io
import os
from functools import lru_cache
from pathlib import Path
from threading import Lock

MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
MODEL_DIR = Path(__file__).resolve().parents[1] / "data" / "models" / f"whisper-{MODEL_SIZE}"
MODEL_FILES = ("model.bin", "config.json", "tokenizer.json")
MAX_SECONDS = 120
_INFERENCE_LOCK = Lock()


def readiness():
    import importlib.util
    if importlib.util.find_spec("faster_whisper") is None:
        return False, "Speech recognition is not installed yet. The app owner needs to install the updated requirements.txt."
    if MODEL_SIZE not in ("base", "small"):
        return False, "Set WHISPER_MODEL_SIZE to base or small and restart the app."
    return True, "Urdu and English transcription is available. No API key is needed."


def download_model():
    from huggingface_hub import snapshot_download
    if MODEL_SIZE not in ("base", "small"):
        raise ValueError("WHISPER_MODEL_SIZE must be base or small.")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    # No authentication and no model code is executed from the remote repository.
    snapshot_download(repo_id=f"Systran/faster-whisper-{MODEL_SIZE}",
                      local_dir=str(MODEL_DIR), token=False,
                      allow_patterns=["config.json", "preprocessor_config.json", "model.bin", "tokenizer.json", "vocabulary.*"])


@lru_cache(maxsize=1)
def load_model():
    from faster_whisper import WhisperModel
    if not all((MODEL_DIR / filename).is_file() for filename in MODEL_FILES):
        try:
            download_model()
        except Exception as exc:
            raise ValueError("The speech model could not be downloaded. Please retry when the server has internet access. Your recording is retained.") from exc
    return WhisperModel(str(MODEL_DIR), device="cpu", compute_type="int8",
                        cpu_threads=2, num_workers=1, local_files_only=True)


def decode_recording(content):
    """Bound decoded memory and duration even for highly compressed uploads."""
    import av
    import numpy as np
    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks, samples = [], 0

    def append_frames(frames):
        nonlocal samples
        for frame in frames:
            samples += frame.samples
            if samples > MAX_SECONDS * 16000:
                raise ValueError(f"Please record up to {MAX_SECONDS // 60} minutes at a time.")
            chunks.append(frame.to_ndarray().reshape(-1))

    with av.open(io.BytesIO(content), mode="r") as container:
        for frame in container.decode(audio=0):
            frame.pts = None
            append_frames(resampler.resample(frame))
        append_frames(resampler.resample(None))
    if not chunks:
        raise ValueError("The recording contains no audio. Please record again.")
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def transcribe_local(content, language="ur"):
    if not content:
        raise ValueError("The recording is empty. Please record again.")
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("Please use a recording smaller than 10 MB.")
    if language not in ("ur", "en", None):
        raise ValueError("Choose Urdu, English or automatic language detection.")
    ready, message = readiness()
    if not ready:
        raise ValueError(message)
    # One inference at a time protects the memory budget of shared hosting.
    if not _INFERENCE_LOCK.acquire(blocking=False):
        raise ValueError("Another recording is being transcribed. Please try again shortly; your recording is retained.")
    try:
        audio = decode_recording(content)
        segments, _ = load_model().transcribe(
            audio, language=language, task="transcribe", beam_size=3,
            vad_filter=True, condition_on_previous_text=False,
        )
        # Consume within the lock: inference happens while iterating segments.
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
    finally:
        _INFERENCE_LOCK.release()
    if not text:
        raise ValueError("No clear speech was detected. Check playback and record again closer to the microphone.")
    return text
