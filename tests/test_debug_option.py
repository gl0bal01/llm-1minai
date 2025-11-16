"""
Test the debug option functionality.
"""

from io import StringIO
from unittest.mock import Mock, patch

import llm_1min


class TestDebugOption:
    """Test debug option shows API request details."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_debug_option_shows_details(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that -o debug true shows API request details."""
        mock_get_key.return_value = "test-api-key"

        # Set some config
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 5)

        # Enable debug via option
        mock_llm_prompt.options.debug = True

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture stderr
        captured_stderr = StringIO()

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            with patch("sys.stderr", captured_stderr):
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )

        # Verify debug output was printed
        debug_output = captured_stderr.getvalue()

        assert "[DEBUG] 1min.ai API Request Details" in debug_output
        assert "Model: gpt-4o" in debug_output
        assert "User global options:" in debug_output
        assert "Built-in model defaults:" in debug_output
        assert "web_search" in debug_output
        assert "[DEBUG] API Request Payload" in debug_output
        assert "webSearch" in debug_output

    @patch("llm_1min.OneMinModel.get_key")
    def test_debug_disabled_no_output(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that without debug option, no debug output is shown."""
        mock_get_key.return_value = "test-api-key"

        # Set debug to False explicitly
        mock_llm_prompt.options.debug = False

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture stderr
        captured_stderr = StringIO()

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            with patch("sys.stderr", captured_stderr):
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )

        # Verify NO debug output
        debug_output = captured_stderr.getvalue()
        assert "[DEBUG]" not in debug_output

    @patch("llm_1min.OneMinModel.get_key")
    def test_debug_env_var_also_works(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path, monkeypatch
    ):
        """Test that LLM_1MIN_DEBUG env var also enables debug."""
        mock_get_key.return_value = "test-api-key"

        # Set env var
        monkeypatch.setenv("LLM_1MIN_DEBUG", "1")

        # Debug option is False (but env var should enable it)
        mock_llm_prompt.options.debug = False

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture stderr
        captured_stderr = StringIO()

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            with patch("sys.stderr", captured_stderr):
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )

        # Verify debug output WAS printed (from env var)
        debug_output = captured_stderr.getvalue()
        assert "[DEBUG] 1min.ai API Request Details" in debug_output
