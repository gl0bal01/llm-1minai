"""
Tests for OneMinModel execution and option merging.
"""

from unittest.mock import Mock, patch

import pytest

import llm_1min


class TestOneMinModelInitialization:
    """Test OneMinModel initialization."""

    def test_model_init_with_all_params(self):
        """Test model initialization with all parameters."""
        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        assert model.model_id == "1min/gpt-4o"
        assert model.api_model_id == "gpt-4o"
        assert model.display_name == "GPT-4o"

    def test_model_init_default_display_name(self):
        """Test model initialization with default display name."""
        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o")
        assert model.display_name == "gpt-4o"

    def test_model_str_representation(self):
        """Test model string representation."""
        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        assert str(model) == "1min.ai: 1min/gpt-4o"


class TestOneMinModelExecution:
    """Test OneMinModel execute method."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_basic_execution_without_options(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test basic model execution with default options."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Execute
        result = list(
            model.execute(prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None)
        )

        assert len(result) == 1
        assert "test response" in result[0].lower()

    @patch("llm_1min.OneMinModel.get_key")
    def test_execution_with_web_search(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test execution with web search enabled."""
        mock_get_key.return_value = "test-api-key"
        mock_llm_prompt.options.web_search = True
        mock_llm_prompt.options.num_of_site = 5
        mock_llm_prompt.options.max_word = 1000

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture the API call
        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify web search params were included
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["webSearch"] is True
            assert payload["promptObject"]["numOfSite"] == 5
            assert payload["promptObject"]["maxWord"] == 1000

    @patch("llm_1min.OneMinModel.get_key")
    def test_execution_with_mixed_context(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test execution with mixed context enabled."""
        mock_get_key.return_value = "test-api-key"
        mock_llm_prompt.options.is_mixed = True

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture the API call
        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify is_mixed was included
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["isMixed"] is True

    @patch("llm_1min.OneMinModel.get_key")
    def test_execution_with_code_generator_type(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test execution with CODE_GENERATOR conversation type."""
        mock_get_key.return_value = "test-api-key"
        mock_llm_prompt.options.conversation_type = "CODE_GENERATOR"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Capture the API call
        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify conversation type
            call_args = mock_post.call_args_list
            conv_call = [
                call
                for call in call_args
                if "conversations" in call[0][0] and "features" not in call[0][0]
            ][0]
            conv_payload = conv_call[1]["json"]

            assert conv_payload["type"] == "CODE_GENERATOR"


class TestOptionPriorityMerging:
    """Test option priority merging (CLI > per-model > global > defaults)."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_cli_options_override_config(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that CLI options override config options."""
        mock_get_key.return_value = "test-api-key"

        # Set config: global web_search=False
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", False)

        # CLI: web_search=True (should override)
        mock_llm_prompt.options.web_search = True

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify CLI value was used
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["webSearch"] is True

    @patch("llm_1min.OneMinModel.get_key")
    def test_per_model_options_override_global(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that per-model options override global defaults."""
        mock_get_key.return_value = "test-api-key"

        # Set config: global num_of_site=3, per-model num_of_site=10
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)  # Global
        config.set_option("num_of_site", 3)  # Global
        config.set_option("num_of_site", 10, model_id="gpt-4o")  # Per-model (should win)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify per-model value was used
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["webSearch"] is True
            assert payload["promptObject"]["numOfSite"] == 10  # Per-model value

    @patch("llm_1min.OneMinModel.get_key")
    def test_global_defaults_used_when_no_overrides(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Test that global defaults are used when no overrides exist."""
        mock_get_key.return_value = "test-api-key"

        # Set only global config
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 7)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Verify global values were used
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["webSearch"] is True
            assert payload["promptObject"]["numOfSite"] == 7


class TestConversationManagement:
    """Test conversation creation and reuse."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_conversation_creation(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test that conversation is created on first request."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # First call - should create conversation
            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Check conversation was created
            assert len(llm_1min._conversation_mapping) > 0

    @patch("llm_1min.OneMinModel.get_key")
    def test_conversation_reuse(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_llm_conversation
    ):
        """Test that existing conversation is reused."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # First call
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Get conversation UUID
            first_uuid = llm_1min._conversation_mapping.get(
                f"{mock_llm_conversation.id}_1min/gpt-4o"
            )

            # Second call - should reuse conversation
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Verify same UUID is used
            second_uuid = llm_1min._conversation_mapping.get(
                f"{mock_llm_conversation.id}_1min/gpt-4o"
            )
            assert first_uuid == second_uuid


class TestErrorHandling:
    """Test error handling in model execution."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_authentication_error_401(self, mock_get_key, mock_llm_prompt):
        """Test handling of 401 authentication error."""
        mock_get_key.return_value = "invalid-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            # Mock 401 error
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = Exception("401")
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )

    @patch("llm_1min.OneMinModel.get_key")
    def test_rate_limit_error_429(self, mock_get_key, mock_llm_prompt):
        """Test handling of 429 rate limit error."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            # Mock 429 error
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = Exception("429")
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )


class TestOptionsValidation:
    """Test Options class validators."""

    def test_conversation_type_valid(self):
        """Test valid conversation types."""
        options = llm_1min.OneMinModel.Options()
        options.conversation_type = "CHAT_WITH_AI"
        assert options.conversation_type == "CHAT_WITH_AI"

        options.conversation_type = "CODE_GENERATOR"
        assert options.conversation_type == "CODE_GENERATOR"

    def test_conversation_type_invalid(self):
        """Test invalid conversation type raises error."""
        with pytest.raises(ValueError):
            options = llm_1min.OneMinModel.Options()
            options.conversation_type = "INVALID_TYPE"
            # Trigger validation
            options.model_validate(options.model_dump())

    def test_num_of_site_valid_range(self):
        """Test num_of_site within valid range."""
        options = llm_1min.OneMinModel.Options()
        options.num_of_site = 1
        assert options.num_of_site == 1

        options.num_of_site = 10
        assert options.num_of_site == 10

    def test_num_of_site_invalid_range(self):
        """Test num_of_site outside valid range raises error."""
        with pytest.raises(ValueError):
            options = llm_1min.OneMinModel.Options()
            options.num_of_site = 0  # Too low
            options.model_validate(options.model_dump())

        with pytest.raises(ValueError):
            options = llm_1min.OneMinModel.Options()
            options.num_of_site = 11  # Too high
            options.model_validate(options.model_dump())
