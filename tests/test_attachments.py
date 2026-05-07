"""Tests for attachments + memory + brand voice options on /api/chat-with-ai."""

from unittest.mock import Mock, patch

import llm_1min


def _conv_response():
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"conversation": {"uuid": "conv-att"}})
    return response


def _chat_response():
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"aiRecord": {"aiRecordDetail": {"resultObject": ["ok"]}}})
    return response


def _capture_payload(monkeypatch):
    """Patch requests.post and capture the chat payload for assertions."""
    captured = {}

    def fake_post(url, **kwargs):
        if "chat-with-ai" in url:
            captured["url"] = url
            captured["payload"] = kwargs["json"]
            return _chat_response()
        return _conv_response()

    monkeypatch.setattr("requests.post", fake_post)
    return captured


class TestAttachments:
    @patch("llm_1min.OneMinModel.get_key")
    def test_images_csv_to_list(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)
        mock_llm_prompt.options.images = "img/a.png,img/b.png, img/c.png "

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )

        attachments = captured["payload"]["promptObject"]["attachments"]
        assert attachments["images"] == ["img/a.png", "img/b.png", "img/c.png"]
        assert "files" not in attachments

    @patch("llm_1min.OneMinModel.get_key")
    def test_files_csv_to_list(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)
        mock_llm_prompt.options.files = "uuid-1,uuid-2"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )

        attachments = captured["payload"]["promptObject"]["attachments"]
        assert attachments["files"] == ["uuid-1", "uuid-2"]
        assert "images" not in attachments

    @patch("llm_1min.OneMinModel.get_key")
    def test_no_attachments_when_options_empty(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        assert "attachments" not in captured["payload"]["promptObject"]


class TestMemoryAndBrandVoice:
    @patch("llm_1min.OneMinModel.get_key")
    def test_with_memories_sets_settings_flag(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)
        mock_llm_prompt.options.with_memories = True

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        settings = captured["payload"]["promptObject"]["settings"]
        assert settings.get("withMemories") is True

    @patch("llm_1min.OneMinModel.get_key")
    def test_brand_voice_id_at_payload_root(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)
        mock_llm_prompt.options.brand_voice_id = "voice-123"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        assert captured["payload"]["brandVoiceId"] == "voice-123"

    @patch("llm_1min.OneMinModel.get_key")
    def test_history_settings_only_when_non_default(
        self, mock_get_key, monkeypatch, mock_llm_prompt
    ):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)
        mock_llm_prompt.options.history_mixed = True
        mock_llm_prompt.options.history_limit = 25

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        history = captured["payload"]["promptObject"]["settings"]["historySettings"]
        assert history == {"isMixed": True, "historyMessageLimit": 25}


class TestEndpointSelection:
    @patch("llm_1min.OneMinModel.get_key")
    def test_chat_uses_chat_with_ai(self, mock_get_key, monkeypatch, mock_llm_prompt):
        mock_get_key.return_value = "k"
        captured = _capture_payload(monkeypatch)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        assert "/api/chat-with-ai" in captured["url"]
        assert captured["payload"]["type"] == "UNIFY_CHAT_WITH_AI"

    @patch("llm_1min.OneMinModel.get_key")
    def test_code_generator_uses_features_endpoint(
        self, mock_get_key, monkeypatch, mock_llm_prompt
    ):
        mock_get_key.return_value = "k"
        captured = {}

        def fake_post(url, **kwargs):
            if "/features" in url:
                captured["url"] = url
                captured["payload"] = kwargs["json"]
                return _chat_response()
            return _conv_response()

        monkeypatch.setattr("requests.post", fake_post)
        mock_llm_prompt.options.conversation_type = "CODE_GENERATOR"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )
        assert "/api/features" in captured["url"]
        assert captured["payload"]["type"] == "CODE_GENERATOR"
        # CodeGen path uses flat promptObject (no nested settings)
        assert "settings" not in captured["payload"]["promptObject"]
        assert "attachments" not in captured["payload"]["promptObject"]


class TestExtractResultText:
    """Edge cases for the response-body extractor."""

    def test_list_result_joined_with_newlines(self):
        body = {"aiRecord": {"aiRecordDetail": {"resultObject": ["one", "two", "three"]}}}
        assert llm_1min.OneMinModel._extract_result_text(body) == "one\ntwo\nthree"

    def test_empty_list_returns_empty_string(self):
        # Architect-flagged: a `.get(...)` falsy check would skip the empty list.
        # Use `is not None` so the empty list is honored as a valid empty result.
        body = {"aiRecord": {"aiRecordDetail": {"resultObject": []}}}
        assert llm_1min.OneMinModel._extract_result_text(body) == ""

    def test_string_result_returned_verbatim(self):
        body = {"aiRecord": {"aiRecordDetail": {"resultObject": "plain"}}}
        assert llm_1min.OneMinModel._extract_result_text(body) == "plain"

    def test_missing_resultobject_falls_back_to_raw_body(self):
        body = {"unexpected": "shape"}
        out = llm_1min.OneMinModel._extract_result_text(body)
        assert "unexpected" in out and "shape" in out
