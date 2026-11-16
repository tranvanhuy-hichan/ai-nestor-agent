import base64
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from nestor.api import live_translate as live
from nestor.core.config import ProviderCfg


def body(**kwargs):
    return live.TranslateBody(**({"audio": base64.b64encode(b"audio" * 20).decode(), "mime": "audio/webm", "targets": ["vi", "en"], "source": "auto", "transcriber": "groq", "translator": "groq"} | kwargs))


@pytest.fixture
def upstream(monkeypatch):
    provider = ProviderCfg(base_url="https://api.groq.com/openai/v1", model="chat", api_key="fake")
    monkeypatch.setattr(live.cfgmod, "load", lambda: SimpleNamespace(providers={"groq": provider}))
    calls, responses = [], []

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, url, **kwargs):
            calls.append((url, kwargs))
            return responses.pop(0)

    monkeypatch.setattr(live.httpx, "Client", Client)
    return calls, responses


def test_transcribe_then_multilingual_translation(upstream):
    calls, responses = upstream
    responses.extend([httpx.Response(200, json={"text": "Hello"}), httpx.Response(200, json={"choices": [{"message": {"content": '{"vi":"Xin chào","en":"Hello"}'}}]})])
    result = live.translate(body())
    assert result == {"text": "Hello", "translations": {"vi": "Xin chào", "en": "Hello"}}
    assert calls[0][0].endswith("/audio/transcriptions")
    assert calls[0][1]["files"]["file"][2] == "audio/webm"
    assert "language" not in calls[0][1]["data"]
    assert len(calls[1][1]["json"]["messages"]) == 2
    assert "tools" not in calls[1][1]["json"]


def test_silence_does_not_invent_translation(upstream):
    calls, responses = upstream
    responses.append(httpx.Response(200, json={"text": "Thank you", "segments": [{"no_speech_prob": .99}]}))
    assert live.translate(body()) == {"text": "", "translations": {}}
    assert len(calls) == 1


def test_missing_language_rejected(upstream):
    _, responses = upstream
    responses.extend([httpx.Response(200, json={"text": "Hello"}), httpx.Response(200, json={"choices": [{"message": {"content": '{"en":"Hello"}'}}]})])
    with pytest.raises(HTTPException) as error:
        live.translate(body())
    assert error.value.status_code == 502


def test_limit_and_key_errors_are_clear(upstream):
    _, responses = upstream
    for status in [401, 429]:
        responses.append(httpx.Response(status, text="private details"))
        with pytest.raises(HTTPException) as error:
            live.translate(body())
        assert error.value.status_code in [429, 502]
        assert "private" not in error.value.detail


def test_inputs():
    for kwargs in [{"targets": []}, {"targets": ["vi", "vi"]}, {"targets": ["bad"]}, {"source": "bad"}, {"mime": "text/html"}, {"audio": "x" * 2_000_001}]:
        with pytest.raises(ValidationError):
            body(**kwargs)


def test_unknown_provider_and_invalid_audio(upstream):
    for data in [body(transcriber="unknown"), body(audio="not base64 data")]:
        with pytest.raises(HTTPException) as error:
            live.translate(data)
        assert error.value.status_code in [400, 422]


def test_busy(upstream):
    live._slots.acquire(); live._slots.acquire()
    try:
        with pytest.raises(HTTPException) as error:
            live.translate(body())
        assert error.value.status_code == 429
    finally:
        live._slots.release(); live._slots.release()


def answer(ready, carry, translations):
    import json
    return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"ready": ready, "carry": carry, "translations": translations})}}]})


def test_unfinished_clause_is_carried_without_translation(upstream):
    calls, responses = upstream
    responses.extend([httpx.Response(200, json={"text": "Before we begin, I want to."}), answer("", "Before we begin, I want to.", {})])
    result = live.translate(body(coherent=True))
    assert result == {"text": "", "carry": "Before we begin, I want to.", "translations": {}}
    assert 'pending_speech' in calls[1][1]['json']['messages'][1]['content']


def test_continuation_forms_one_sentence_without_losing_words(upstream):
    calls, responses = upstream
    source = "Before we begin, I want to remind you about the subtitles."
    responses.extend([httpx.Response(200, json={"text": "remind you about the subtitles."}), answer(source, "", {"vi": "Trước khi bắt đầu, tôi muốn nhắc bạn về phụ đề.", "en": source})])
    result = live.translate(body(coherent=True, carry="Before we begin, I want to."))
    assert result['text'] == source and result['carry'] == ''
    assert calls[0][1]['data']['prompt'].endswith('I want to.')


def test_complete_sentence_and_unfinished_tail_are_partitioned(upstream):
    _, responses = upstream
    responses.extend([httpx.Response(200, json={"text": "Hello everyone. Today we are going to"}), answer("Hello everyone.", "Today we are going to", {"vi": "Chào mọi người.", "en": "Hello everyone."})])
    result = live.translate(body(coherent=True))
    assert result['text'] == "Hello everyone." and result['carry'] == "Today we are going to"


def test_coherence_must_not_drop_or_invent_source(upstream):
    _, responses = upstream
    for ready in ['Hello', 'Hello everyone extra']:
        responses.extend([httpx.Response(200, json={"text": "Hello everyone"}), answer(ready, "", {"vi": "Xin chào", "en": ready})])
        with pytest.raises(HTTPException) as error:
            live.translate(body(coherent=True))
        assert error.value.status_code == 502


def test_final_flush_keeps_all_remaining_speech(upstream):
    calls, responses = upstream
    responses.append(answer('And the final example', '', {'vi': 'Và ví dụ cuối cùng', 'en': 'And the final example'}))
    result = live.flush(live.FlushBody(text='And the final example', targets=['vi','en'], translator='groq'))
    assert result['carry'] == '' and result['text'] == 'And the final example'
    assert len(calls) == 1 and calls[0][0].endswith('/chat/completions')
    assert '"final": true' in calls[0][1]['json']['messages'][1]['content']


def test_flush_cannot_leave_an_untranslated_tail(upstream):
    _, responses = upstream
    responses.append(answer('', 'unfinished', {}))
    with pytest.raises(HTTPException) as error:
        live.flush(live.FlushBody(text='unfinished', targets=['vi'], translator='groq'))
    assert error.value.status_code == 502


def test_silence_preserves_buffered_phrase(upstream):
    _, responses = upstream
    responses.append(httpx.Response(200, json={'text':'', 'segments':[]}))
    assert live.translate(body(coherent=True, carry='I want to')) == {'text':'', 'translations':{}, 'carry':'I want to'}


def test_transcribe_returns_source_only(upstream):
    calls, responses = upstream
    responses.append(httpx.Response(200, json={"text": " Hello there "}))
    result = live.transcribe(live.TranscribeBody(audio=body().audio, mime="audio/webm", transcriber="groq"))
    assert result["text"] == "Hello there" and len(calls) == 1


def test_stream_emits_deltas_and_done(monkeypatch):
    import json as _json
    provider = ProviderCfg(base_url="https://api.groq.com/openai/v1", model="chat", api_key="fake")
    monkeypatch.setattr(live.cfgmod, "load", lambda: SimpleNamespace(providers={"groq": provider}))
    lines = ['data: ' + _json.dumps({"choices": [{"delta": {"content": w}}]}) for w in ("Xin ", "chào")] + ["data: [DONE]"]

    class Resp:
        status_code = 200
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def iter_lines(self): return iter(lines)

    class Client:
        def __init__(self, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def stream(self, *a, **k): return Resp()

    monkeypatch.setattr(live.httpx, "Client", Client)
    response = live.stream(live.StreamBody(text="Hello", target="vi", translator="groq"))
    import asyncio

    async def collect():
        return [_json.loads(x) async for x in response.body_iterator]

    events = asyncio.run(collect())
    assert [e.get("delta") for e in events[:2]] == ["Xin ", "chào"] and events[-1] == {"done": True}


def test_transcribe_drops_hallucinated_segments(upstream):
    _, responses = upstream
    responses.append(httpx.Response(200, json={"language": "vi", "text": "x", "segments": [
        {"text": " Chào mừng các bạn", "no_speech_prob": .9, "avg_logprob": -.2, "compression_ratio": 1},
        {"text": " real speech", "no_speech_prob": .1, "avg_logprob": -.3, "compression_ratio": 1.2}]}))
    result = live.transcribe(live.TranscribeBody(audio=body().audio, mime="audio/webm", transcriber="groq"))
    assert result["text"] == "real speech"


def test_refine_prompt_translates_whole_sentence():
    body = live.StreamBody(text="Before we begin, I want to say hi.", target="vi", translator="groq", refine=True)
    assert "COMPLETE sentence" in live._stream_prompt(body)
    assert "FRAGMENT" in live._stream_prompt(live.StreamBody(text="x", target="vi", translator="groq"))
