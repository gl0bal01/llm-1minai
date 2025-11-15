"""
Simple test to verify web_search configuration works properly.
This test checks that web_search settings from config are correctly
applied to API requests.
"""

from unittest.mock import Mock, patch

import llm_1min


class TestWebSearchConfiguration:
    """Test web_search option handling from configuration."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_web_search_from_global_config(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that web_search=True from global config is applied to API request."""
        mock_get_key.return_value = "test-api-key"

        # Set global config: web_search=True
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 5)
        config.set_option("max_word", 1000)

        # Create model and execute WITHOUT passing web_search via CLI
        # (mock_llm_prompt has default values: web_search=False)
        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # Execute without CLI web_search option
            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify web search params were included in the API call
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            # These should be set from config
            assert (
                payload["promptObject"]["webSearch"] is True
            ), "webSearch should be True from global config"
            assert (
                payload["promptObject"]["numOfSite"] == 5
            ), "numOfSite should be 5 from global config"
            assert (
                payload["promptObject"]["maxWord"] == 1000
            ), "maxWord should be 1000 from global config"

    @patch("llm_1min.OneMinModel.get_key")
    def test_web_search_from_model_config(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that web_search=True from per-model config is applied."""
        mock_get_key.return_value = "test-api-key"

        # Set per-model config: web_search=True for gpt-4o
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="gpt-4o")
        config.set_option("num_of_site", 7, model_id="gpt-4o")

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify web search params from per-model config
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert (
                payload["promptObject"]["webSearch"] is True
            ), "webSearch should be True from model config"
            assert (
                payload["promptObject"]["numOfSite"] == 7
            ), "numOfSite should be 7 from model config"

    @patch("llm_1min.OneMinModel.get_key")
    def test_web_search_with_conversation(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_llm_conversation, mock_config_path
    ):
        """Test that web_search works correctly with conversations."""
        mock_get_key.return_value = "test-api-key"

        # Set global web_search=True
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # First message in conversation
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Verify first call has web_search
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]
            assert (
                payload["promptObject"]["webSearch"] is True
            ), "First call should have webSearch=True"

            # Second message in same conversation
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Verify second call also has web_search
            call_args = mock_post.call_args_list
            # Get the second features call (should be last one)
            features_calls = [call for call in call_args if "features" in call[0][0]]
            second_payload = features_calls[-1][1]["json"]
            assert (
                second_payload["promptObject"]["webSearch"] is True
            ), "Second call should also have webSearch=True"

    @patch("llm_1min.OneMinModel.get_key")
    def test_web_search_false_not_included_in_payload(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that when web_search=False, it's not included in API payload."""
        mock_get_key.return_value = "test-api-key"

        # Don't set any config (defaults to False)
        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify web search is NOT in payload when False
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert (
                "webSearch" not in payload["promptObject"]
            ), "webSearch should not be in payload when False"
            assert (
                "numOfSite" not in payload["promptObject"]
            ), "numOfSite should not be in payload when web_search is False"
            assert (
                "maxWord" not in payload["promptObject"]
            ), "maxWord should not be in payload when web_search is False"
