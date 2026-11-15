from fastapi import FastAPI
from fastapi.testclient import TestClient

from argus.api import speech


def client():
    app = FastAPI()
    app.include_router(speech.router, prefix="/api")
    return TestClient(app)


def test_audio_and_language(monkeypatch):
    calls = []

    class Voice:
        def __init__(self, text, **kwargs):
            calls.append((text, kwargs))

        def stream(self):
            yield b"ID3audio"

    monkeypatch.setattr(speech, "gTTS", Voice)
    r = client().post("/api/speech", json={"text": "Xin chào", "lang": "vi"})
    assert r.status_code == 200 and r.content == b"ID3audio"
    assert r.headers["content-type"] == "audio/mpeg"
    assert r.headers["cache-control"] == "no-store"
    assert calls[0][1]["lang"] == "vi"
    assert calls[0][1]["timeout"] == (5, 10)


def test_input_validation():
    for text, lang in [("", "vi"), ("   ", "vi"), ("a" * 601, "vi"), ("hi", "arbitrary")]:
        assert client().post("/api/speech", json={"text": text, "lang": lang}).status_code == 422


def test_failure_does_not_leak_content_and_releases_slot(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("private user content")

    monkeypatch.setattr(speech, "gTTS", fail)
    for _ in range(3):
        r = client().post("/api/speech", json={"text": "Xin chào"})
        assert r.status_code == 503
        assert "private" not in r.text


def test_empty_audio_rejected(monkeypatch):
    class Empty:
        def __init__(self, *args, **kwargs):
            pass

        def stream(self):
            return iter([])

    monkeypatch.setattr(speech, "gTTS", Empty)
    assert client().post("/api/speech", json={"text": "Xin chào"}).status_code == 503


def test_concurrency_limit():
    speech._slots.acquire()
    speech._slots.acquire()
    try:
        assert client().post("/api/speech", json={"text": "Xin chào"}).status_code == 429
    finally:
        speech._slots.release()
        speech._slots.release()
