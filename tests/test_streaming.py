"""Tests for SSE streaming on /api/chat-with-ai (v0.4.0)."""

from unittest.mock import Mock, patch

import llm
import pytest

import llm_1min


def _sse_response(events):
    """Build a Mock that mimics requests.post(stream=True) with given SSE events.

    `events` is a list of (event_name, data_str) tuples. Each emits two lines
    (event:, data:) plus a blank delimiter line, matching the SSE wire format.
    """
    lines = []
    for name, data in events:
        lines.append(f"event: {name}")
        lines.append(f"data: {data}")
        lines.append("")  # delimiter

    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    response.iter_lines = Mock(return_value=iter(lines))
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


def _conv_response():
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"conversation": {"uuid": "conv-uuid-stream"}})
    return response


@pytest.fixture
def streaming_post(monkeypatch):
    """Patch requests.post to return conversation creation, then SSE stream."""

    def _factory(events):
        sse = _sse_response(events)
        conv = _conv_response()

        def fake_post(url, **kwargs):
            if "chat-with-ai" in url:
                return sse
            return conv

        monkeypatch.setattr("requests.post", fake_post)
        return sse

    return _factory


class TestSSEStreaming:
    @patch("llm_1min.OneMinModel.get_key")
    def test_yields_content_chunks_and_terminates_on_done(
        self, mock_get_key, streaming_post, mock_llm_prompt
    ):
        mock_get_key.return_value = "test-api-key"
        streaming_post(
            [
                ("content", '{"content": "Hello "}'),
                ("content", '{"content": "world"}'),
                ("content", '{"content": "!"}'),
                ("result", '{"aiRecord": {"uuid": "x"}}'),
                ("done", '{"message": "Stream completed"}'),
            ]
        )

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        chunks = list(
            model.execute(prompt=mock_llm_prompt, stream=True, response=Mock(), conversation=None)
        )

        assert chunks == ["Hello ", "world", "!"]

    @patch("llm_1min.OneMinModel.get_key")
    def test_error_event_raises_modelerror(self, mock_get_key, streaming_post, mock_llm_prompt):
        mock_get_key.return_value = "test-api-key"
        streaming_post(
            [
                ("content", '{"content": "partial"}'),
                ("error", '{"message": "Server overload"}'),
            ]
        )

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        with pytest.raises(llm.ModelError, match="Server overload"):
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=True,
                    response=Mock(),
                    conversation=None,
                )
            )

    @patch("llm_1min.OneMinModel.get_key")
    def test_streaming_url_has_is_streaming_query(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "test-api-key"
        captured_urls = []

        sse = _sse_response([("done", "{}")])
        conv = _conv_response()

        def fake_post(url, **kwargs):
            captured_urls.append(url)
            if "chat-with-ai" in url:
                return sse
            return conv

        monkeypatch.setattr("requests.post", fake_post)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(model.execute(prompt=mock_llm_prompt, stream=True, response=Mock(), conversation=None))

        chat_urls = [u for u in captured_urls if "chat-with-ai" in u]
        assert chat_urls, "expected at least one chat-with-ai POST"
        assert "isStreaming=true" in chat_urls[0]

    @patch("llm_1min.OneMinModel.get_key")
    def test_non_streaming_does_not_use_is_streaming_query(
        self, mock_get_key, monkeypatch, mock_llm_prompt
    ):
        mock_get_key.return_value = "test-api-key"
        captured = []

        non_stream = Mock()
        non_stream.status_code = 200
        non_stream.raise_for_status = Mock()
        non_stream.json = Mock(
            return_value={"aiRecord": {"aiRecordDetail": {"resultObject": ["full reply"]}}}
        )
        conv = _conv_response()

        def fake_post(url, **kwargs):
            captured.append(url)
            if "chat-with-ai" in url:
                return non_stream
            return conv

        monkeypatch.setattr("requests.post", fake_post)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        chunks = list(
            model.execute(
                prompt=mock_llm_prompt,
                stream=False,
                response=Mock(),
                conversation=None,
            )
        )
        assert chunks == ["full reply"]
        chat_urls = [u for u in captured if "chat-with-ai" in u]
        assert chat_urls
        assert "isStreaming=true" not in chat_urls[0]
