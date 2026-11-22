import hashlib
import json

import httpx
from fastapi.testclient import TestClient

from nestor.services.memory import model_setup


def test_ocr_setup_downloads_and_checks_language_files(tmp_path, monkeypatch):
    def probe():
        return True, {name for name in ("vie", "eng") if (tmp_path / f"{name}.traineddata").is_file()}

    packages = {name: name.encode() for name in ("vie", "eng")}
    monkeypatch.setattr(model_setup, "_probe_ocr", probe)
    monkeypatch.setattr(model_setup.pdf_ocr, "managed_tessdata", lambda: tmp_path)
    monkeypatch.setattr(model_setup, "_DATA_HASH", {name: hashlib.sha256(data).hexdigest() for name, data in packages.items()})
    client = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=packages[request.url.path.split("/")[-1].split(".")[0]])
    ))
    monkeypatch.setattr(model_setup.httpx, "Client", lambda **_: client)
    job = model_setup.SetupJob()
    model_setup.install_ocr(job)
    assert model_setup.ocr_status()["ready"]
    assert (tmp_path / "vie.traineddata").read_bytes() == packages["vie"]


def test_embedding_pull_uses_ollama_and_reports_progress(tmp_env, monkeypatch):
    monkeypatch.setattr(model_setup.embeddings, "ollama_url", lambda _: "http://localhost:11434")

    def respond(request):
        assert request.url.path == "/api/pull"
        assert json.loads(request.content) == {"model": "bge-m3", "stream": True}
        return httpx.Response(200, text='{"total":100,"completed":45}\n{"status":"success"}\n')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(model_setup.httpx, "stream", lambda method, url, **kwargs: client.stream(method, url, json=kwargs["json"]))
        job = model_setup.SetupJob()
        model_setup.pull_embedding(job, "bge-m3")
    assert job.snapshot()["percent"] == 45


def test_embedding_pull_rejects_custom_registry(tmp_env):
    from nestor.main import app

    response = TestClient(app).post("/api/memory/model-pull", json={"model": "example.test:5000/library/model"})
    assert response.status_code == 422
