"""No downloads, API keys or real complaint recordings are used in tests."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from grievance import speech


def test_local_transcription_preserves_urdu_and_never_writes_audio(monkeypatch):
    model = Mock()
    model.transcribe.return_value = (iter([SimpleNamespace(text=" میرا بجلی کا بل "), SimpleNamespace(text="درست کریں۔")]), None)
    monkeypatch.setattr(speech, "readiness", lambda: (True, "Ready"))
    monkeypatch.setattr(speech, "load_model", lambda: model)
    monkeypatch.setattr(speech, "decode_recording", lambda content: content)
    assert speech.transcribe_local(b"audio", "ur") == "میرا بجلی کا بل درست کریں۔"
    args, kwargs = model.transcribe.call_args
    assert args[0] == b"audio"
    assert kwargs["language"] == "ur"
    assert kwargs["task"] == "transcribe"
    assert kwargs["vad_filter"] is True


def test_silent_recording_does_not_replace_complaint_with_empty_text(monkeypatch):
    model = Mock()
    model.transcribe.return_value = (iter([]), None)
    monkeypatch.setattr(speech, "readiness", lambda: (True, "Ready"))
    monkeypatch.setattr(speech, "load_model", lambda: model)
    monkeypatch.setattr(speech, "decode_recording", lambda content: content)
    with pytest.raises(ValueError, match="No clear speech"):
        speech.transcribe_local(b"audio")


def test_unconfigured_local_model_does_not_download(monkeypatch):
    loader = Mock()
    monkeypatch.setattr(speech, "readiness", lambda: (False, "Model missing"))
    monkeypatch.setattr(speech, "load_model", loader)
    with pytest.raises(ValueError, match="Model missing"):
        speech.transcribe_local(b"audio")
    loader.assert_not_called()


def test_missing_weights_are_downloaded_on_first_use(tmp_path, monkeypatch):
    faster_whisper = pytest.importorskip("faster_whisper")
    monkeypatch.setattr(speech, "MODEL_DIR", tmp_path)
    downloader = Mock()
    constructor = Mock()
    monkeypatch.setattr(speech, "download_model", downloader)
    monkeypatch.setattr(faster_whisper, "WhisperModel", constructor)
    speech.load_model.cache_clear()
    try:
        speech.load_model()
        speech.load_model()
        downloader.assert_called_once()
        constructor.assert_called_once()
        assert constructor.call_args.kwargs["device"] == "cpu"
        assert constructor.call_args.kwargs["compute_type"] == "int8"
    finally:
        speech.load_model.cache_clear()


def test_busy_server_keeps_recording_for_retry(monkeypatch):
    monkeypatch.setattr(speech, "readiness", lambda: (True, "Ready"))
    speech._INFERENCE_LOCK.acquire()
    try:
        with pytest.raises(ValueError, match="Another recording"):
            speech.transcribe_local(b"audio")
    finally:
        speech._INFERENCE_LOCK.release()


def test_duration_limit_rejects_audio_without_truncating(monkeypatch):
    import io
    import wave
    pytest.importorskip("av")
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 32000)
    monkeypatch.setattr(speech, "MAX_SECONDS", 1)
    with pytest.raises(ValueError, match="Please record up to"):
        speech.decode_recording(output.getvalue())


