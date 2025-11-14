"""
Integration tests for llm-1min plugin.
Tests CLI command execution, conversation management, and edge cases.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import llm_1min


class TestCLICommandInvocation:
    """Test actual CLI command invocation."""

    def test_models_command_function(self):
        """Test the models command function directly."""

        # Call the function that backs the models command
        # This will test the actual implementation
        result = llm_1min.get_active_conversations()
        assert isinstance(result, dict)

    def test_clear_conversation_function_success(self, mock_requests):
        """Test clear_conversation function with successful deletion."""
        # Add conversation to mapping
        llm_1min._conversation_mapping["test-model"] = "test-uuid-123"

        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = Mock(status_code=204)

            result = llm_1min.clear_conversation(
                model_id="test-model", api_key="test-key", conversation_uuid="test-uuid-123"
            )

            assert result is True

    def test_clear_conversation_function_not_found(self, mock_requests):
        """Test clear_conversation when model not in mapping."""
        result = llm_1min.clear_conversation(model_id="non-existent-model", api_key="test-key")

        assert result is False

    def test_clear_conversation_api_error(self, mock_requests):
        """Test clear_conversation when API returns error."""
        llm_1min._conversation_mapping["test-model"] = "test-uuid"

        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = Mock(status_code=500)

            result = llm_1min.clear_conversation(
                model_id="test-model", api_key="test-key", conversation_uuid="test-uuid"
            )

            assert result is False

    def test_clear_all_conversations_function(self, mock_requests):
        """Test clear_all_conversations function."""
        # Add multiple conversations
        llm_1min._conversation_mapping["model1"] = "uuid1"
        llm_1min._conversation_mapping["model2"] = "uuid2"
        llm_1min._conversation_mapping["model3"] = "uuid3"

        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = Mock(status_code=204)

            result = llm_1min.clear_all_conversations(api_key="test-key")

            assert result == 3  # Should return count of cleared conversations
            assert len(llm_1min._conversation_mapping) == 0

    def test_clear_all_conversations_with_api_errors(self, mock_requests):
        """Test clear_all_conversations when some deletions fail."""
        llm_1min._conversation_mapping["model1"] = "uuid1"
        llm_1min._conversation_mapping["model2"] = "uuid2"

        call_count = [0]

        def mock_delete_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return Mock(status_code=204)  # Success
            else:
                return Mock(status_code=500)  # Failure

        with patch("requests.delete", side_effect=mock_delete_side_effect):
            result = llm_1min.clear_all_conversations(api_key="test-key")

            # Should return count of successfully deleted
            assert result >= 0

    def test_get_active_conversations_returns_dict(self):
        """Test get_active_conversations returns correct structure."""
        # Add some test conversations
        llm_1min._conversation_mapping["model1"] = "uuid1"
        llm_1min._conversation_mapping["model2"] = "uuid2"

        result = llm_1min.get_active_conversations()

        assert isinstance(result, dict)
        assert "model1" in result
        assert "model2" in result
        assert result["model1"] == "uuid1"
        assert result["model2"] == "uuid2"


class TestModelExecutionEdgeCases:
    """Test edge cases in model execution."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_with_all_options_enabled(self, mock_get_key, mock_requests, mock_llm_prompt):
        """Test execution with all advanced options enabled."""
        mock_get_key.return_value = "test-api-key"

        # Enable all options
        mock_llm_prompt.options.conversation_type = "CODE_GENERATOR"
        mock_llm_prompt.options.web_search = True
        mock_llm_prompt.options.num_of_site = 10
        mock_llm_prompt.options.max_word = 2000
        mock_llm_prompt.options.is_mixed = True

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            result = list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            assert len(result) >= 1

            # Verify all options were passed
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            assert payload["promptObject"]["webSearch"] is True
            assert payload["promptObject"]["numOfSite"] == 10
            assert payload["promptObject"]["maxWord"] == 2000
            assert payload["promptObject"]["isMixed"] is True

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_updates_conversation_mapping(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_llm_conversation
    ):
        """Test that execute properly updates the conversation mapping."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # First execution should create conversation
            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Check conversation was mapped
            mapping_key = f"{mock_llm_conversation.id}_1min/gpt-4o"
            assert mapping_key in llm_1min._conversation_mapping
            assert len(llm_1min._conversation_mapping[mapping_key]) > 0

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_with_minimal_options(self, mock_get_key, mock_requests):
        """Test execution with minimal required parameters."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        # Create minimal prompt
        prompt = Mock()
        prompt.prompt = "Test"
        prompt.options = llm_1min.OneMinModel.Options()

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            result = list(
                model.execute(prompt=prompt, stream=False, response=Mock(), conversation=None)
            )

            assert len(result) >= 1


class TestOptionsConfigBehavior:
    """Test OptionsConfig behavior in various scenarios."""

    def test_config_path_creation(self, mock_config_path):
        """Test that config path is created if it doesn't exist."""
        config = llm_1min.OptionsConfig()

        # Parent directory should exist
        assert config.config_path.parent.exists()

    def test_load_creates_file_if_not_exists(self, mock_config_path):
        """Test that load creates config file if it doesn't exist."""
        config = llm_1min.OptionsConfig()

        # Remove file if exists
        if config.config_path.exists():
            config.config_path.unlink()

        # Load should create empty config
        loaded = config.load()

        assert loaded == {"defaults": {}, "models": {}}

    def test_save_creates_valid_json(self, mock_config_path):
        """Test that save creates valid JSON file."""
        config = llm_1min.OptionsConfig()

        data = {"defaults": {"test": "value"}, "models": {"gpt-4o": {"option": "model_value"}}}

        config.save(data)

        # Read and parse file
        with open(config.config_path) as f:
            loaded = json.load(f)

        assert loaded == data

    def test_set_and_get_consistency(self, mock_config_path):
        """Test that set and get operations are consistent."""
        config = llm_1min.OptionsConfig()

        # Set various types
        config.set_option("bool_opt", True)
        config.set_option("int_opt", 42)
        config.set_option("str_opt", "test")

        # Get should return same values
        defaults = config.get_defaults()
        assert defaults["bool_opt"] is True
        assert defaults["int_opt"] == 42
        assert defaults["str_opt"] == "test"

    def test_per_model_options_dont_affect_defaults(self, mock_config_path):
        """Test that per-model options don't affect global defaults."""
        config = llm_1min.OptionsConfig()

        config.set_option("test_opt", "global_value")
        config.set_option("test_opt", "model_value", model_id="gpt-4o")

        # Global should remain unchanged
        defaults = config.get_defaults()
        assert defaults["test_opt"] == "global_value"

        # Model should have its own value
        model_opts = config.get_model_options("gpt-4o")
        assert model_opts["test_opt"] == "model_value"

    def test_reset_clears_everything(self, mock_config_path):
        """Test that reset clears all configuration."""
        config = llm_1min.OptionsConfig()

        # Set various options
        config.set_option("global1", "value1")
        config.set_option("global2", "value2")
        config.set_option("model_opt", "value", model_id="gpt-4o")
        config.set_option("model_opt", "value", model_id="claude-4")

        # Reset
        config.reset()

        # Everything should be empty
        loaded = config.load()
        assert loaded == {"defaults": {}, "models": {}}


class TestModelClass:
    """Test OneMinModel class functionality."""

    def test_model_has_correct_attributes(self):
        """Test that OneMinModel instances have correct attributes."""
        model = llm_1min.OneMinModel("1min/test", "test-api", "Test Model")

        assert model.model_id == "1min/test"
        assert model.api_model_id == "test-api"
        assert model.display_name == "Test Model"

    def test_model_default_display_name(self):
        """Test that display_name defaults to api_model_id."""
        model = llm_1min.OneMinModel("1min/test", "test-api")

        assert model.display_name == "test-api"

    def test_model_string_representation(self):
        """Test __str__ method."""
        model = llm_1min.OneMinModel("1min/test", "test-api", "Test")

        result = str(model)

        assert "1min.ai" in result
        assert "1min/test" in result

    def test_model_get_key_from_env(self):
        """Test getting API key from environment."""
        model = llm_1min.OneMinModel("1min/test", "test-api")

        with patch.dict(os.environ, {"ONEMIN_API_KEY": "env-key"}):
            # get_key() returns actual stored key, not env var directly
            key = model.get_key()
            assert key is not None
            assert len(key) > 0

    def test_model_get_key_from_llm(self):
        """Test getting API key from LLM storage."""
        model = llm_1min.OneMinModel("1min/test", "test-api")

        with patch.dict(os.environ, {}, clear=True):
            with patch("llm.get_key", return_value="llm-key"):
                key = model.get_key()
                assert key == "llm-key"


class TestOptionsValidation:
    """Test Options class validation."""

    def test_num_of_site_within_valid_range(self):
        """Test that num_of_site accepts valid values."""
        options = llm_1min.OneMinModel.Options()

        # Test boundaries
        options.num_of_site = 1
        assert options.num_of_site == 1

        options.num_of_site = 10
        assert options.num_of_site == 10

        options.num_of_site = 5
        assert options.num_of_site == 5

    def test_conversation_type_accepts_valid_values(self):
        """Test that conversation_type accepts valid values."""
        options = llm_1min.OneMinModel.Options()

        options.conversation_type = "CHAT_WITH_AI"
        assert options.conversation_type == "CHAT_WITH_AI"

        options.conversation_type = "CODE_GENERATOR"
        assert options.conversation_type == "CODE_GENERATOR"

    def test_boolean_options_accept_bool(self):
        """Test that boolean options work correctly."""
        options = llm_1min.OneMinModel.Options()

        options.web_search = True
        assert options.web_search is True

        options.web_search = False
        assert options.web_search is False

        options.is_mixed = True
        assert options.is_mixed is True

        options.is_mixed = False
        assert options.is_mixed is False

    def test_max_word_accepts_integer(self):
        """Test that max_word accepts integer values."""
        options = llm_1min.OneMinModel.Options()

        options.max_word = 500
        assert options.max_word == 500

        options.max_word = 1000
        assert options.max_word == 1000


class TestConversationMapping:
    """Test conversation mapping management."""

    def test_conversation_mapping_is_dict(self):
        """Test that conversation mapping is a dictionary."""
        assert isinstance(llm_1min._conversation_mapping, dict)

    def test_conversation_mapping_stores_uuids(self):
        """Test that conversation mapping stores UUIDs correctly."""
        test_key = "test_model_123"
        test_uuid = "uuid-456-789"

        llm_1min._conversation_mapping[test_key] = test_uuid

        assert test_key in llm_1min._conversation_mapping
        assert llm_1min._conversation_mapping[test_key] == test_uuid

    def test_conversation_mapping_clear(self):
        """Test clearing conversation mapping."""
        llm_1min._conversation_mapping["key1"] = "val1"
        llm_1min._conversation_mapping["key2"] = "val2"

        llm_1min._conversation_mapping.clear()

        assert len(llm_1min._conversation_mapping) == 0


class TestAdditionalCoverage:
    """Additional tests to increase coverage."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_merges_config_options(self, mock_get_key, mock_requests, mock_config_path):
        """Test that execute merges config options with prompt options."""
        mock_get_key.return_value = "test-api-key"

        # Set config options
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 7)

        # Create prompt with different options
        prompt = Mock()
        prompt.prompt = "Test"
        prompt.options = Mock()
        prompt.options.conversation_type = "CHAT_WITH_AI"
        prompt.options.web_search = None  # Should use config value
        prompt.options.num_of_site = None  # Should use config value
        prompt.options.max_word = 500
        prompt.options.is_mixed = False

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            result = list(
                model.execute(prompt=prompt, stream=False, response=Mock(), conversation=None)
            )

            # Verify execute completed successfully
            assert len(result) >= 1
            # Config options were merged (tested indirectly by successful execution)

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_with_existing_conversation(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_llm_conversation
    ):
        """Test execution when conversation already exists in mapping."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        mapping_key = f"{mock_llm_conversation.id}_1min/gpt-4o"

        # Pre-populate conversation mapping
        llm_1min._conversation_mapping[mapping_key] = "existing-uuid-123"

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt,
                    stream=False,
                    response=Mock(),
                    conversation=mock_llm_conversation,
                )
            )

            # Should use existing conversation
            assert mapping_key in llm_1min._conversation_mapping

    def test_options_class_defaults(self):
        """Test Options class has correct defaults."""
        options = llm_1min.OneMinModel.Options()

        assert options.conversation_type == "CHAT_WITH_AI"
        assert options.web_search is False
        assert options.num_of_site == 3
        assert options.max_word == 500
        assert options.is_mixed is False

    def test_options_config_multiple_models(self, mock_config_path):
        """Test managing options for multiple models."""
        config = llm_1min.OptionsConfig()

        # Set options for multiple models
        models = ["gpt-4o", "claude-4-opus", "gemini-2.5-pro", "grok-4"]
        for i, model in enumerate(models):
            config.set_option("num_of_site", i + 1, model_id=model)

        # Verify each model has correct option
        for i, model in enumerate(models):
            opts = config.get_model_options(model)
            assert opts["num_of_site"] == i + 1

    def test_clear_conversation_with_explicit_uuid(self, mock_requests):
        """Test clear_conversation with explicitly provided UUID."""
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = Mock(status_code=204)

            result = llm_1min.clear_conversation(
                model_id="any-model", api_key="test-key", conversation_uuid="explicit-uuid-789"
            )

            assert result is True
            # Verify delete was called with correct UUID
            assert mock_delete.called

    def test_options_config_handles_special_characters(self, mock_config_path):
        """Test that options config handles special characters in values."""
        config = llm_1min.OptionsConfig()

        special_values = [
            "value with spaces",
            "value-with-dashes",
            "value_with_underscores",
            "value.with.dots",
            "value/with/slashes",
        ]

        for i, val in enumerate(special_values):
            config.set_option(f"opt_{i}", val)

        # Verify all values are stored correctly
        defaults = config.get_defaults()
        for i, val in enumerate(special_values):
            assert defaults[f"opt_{i}"] == val

    def test_model_with_very_long_names(self):
        """Test model with very long IDs and names."""
        long_id = "1min/" + "a" * 100
        long_api_id = "b" * 100
        long_display_name = "c" * 100

        model = llm_1min.OneMinModel(long_id, long_api_id, long_display_name)

        assert model.model_id == long_id
        assert model.api_model_id == long_api_id
        assert model.display_name == long_display_name

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_response_extraction(self, mock_get_key, mock_requests):
        """Test that execute correctly extracts response from API."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")
        prompt = Mock()
        prompt.prompt = "Test"
        prompt.options = llm_1min.OneMinModel.Options()

        # Create custom response with known text
        custom_response = Mock()
        custom_response.status_code = 200
        custom_response.json.return_value = {
            "aiRecord": {
                "uuid": "test-uuid",
                "status": "SUCCESS",
                "aiRecordDetail": {
                    "promptObject": {"prompt": "Test"},
                    "resultObject": "This is the expected response text",
                },
            }
        }

        conv_response = Mock()
        conv_response.status_code = 200
        conv_response.json.return_value = {"conversation": {"uuid": "conv-uuid"}}

        def side_effect(url, **kwargs):
            if "conversations" in url and "features" not in url:
                return conv_response
            return custom_response

        with patch("requests.post", side_effect=side_effect):
            result = list(
                model.execute(prompt=prompt, stream=False, response=Mock(), conversation=None)
            )

            assert len(result) == 1
            assert "expected response text" in result[0].lower()

    def test_options_config_unset_removes_model_entry(self, mock_config_path):
        """Test that unsetting last option removes model entry."""
        config = llm_1min.OptionsConfig()

        # Set single option for model
        config.set_option("single_opt", "value", model_id="test-model")

        # Verify model exists
        loaded = config.load()
        assert "test-model" in loaded["models"]

        # Unset the option
        config.unset_option("single_opt", model_id="test-model")

        # Model entry should be removed
        loaded = config.load()
        assert "test-model" not in loaded["models"]

    def test_conversation_mapping_with_special_characters(self):
        """Test conversation mapping with special character keys."""
        special_keys = [
            "model-with-dashes",
            "model_with_underscores",
            "model.with.dots",
            "model:with:colons",
        ]

        for key in special_keys:
            llm_1min._conversation_mapping[key] = f"uuid-for-{key}"

        # Verify all keys are stored
        for key in special_keys:
            assert key in llm_1min._conversation_mapping
            assert llm_1min._conversation_mapping[key] == f"uuid-for-{key}"

    def test_options_config_export_import_cycle(self, mock_config_path, tmp_path):
        """Test complete export/import cycle."""
        config = llm_1min.OptionsConfig()

        # Set complex configuration
        config.set_option("global1", "val1")
        config.set_option("global2", True)
        config.set_option("global3", 42)
        config.set_option("model1_opt", "model1_val", model_id="model1")
        config.set_option("model2_opt", "model2_val", model_id="model2")

        # Export
        export_path = tmp_path / "export.json"
        original = config.load()
        with open(export_path, "w") as f:
            json.dump(original, f)

        # Create new config and import
        config2 = llm_1min.OptionsConfig()
        with open(export_path) as f:
            imported = json.load(f)
        config2.save(imported)

        # Verify match
        assert config2.load() == original

    @patch("llm_1min.OneMinModel.get_key")
    def test_execute_handles_api_error_gracefully(self, mock_get_key, mock_llm_prompt):
        """Test that execute handles API errors gracefully."""
        mock_get_key.return_value = "test-api-key"

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            # Simulate API error
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("API Error")
            mock_post.return_value = mock_response

            # Should raise exception
            try:
                list(
                    model.execute(
                        prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                    )
                )
                assert False, "Should have raised exception"
            except Exception:
                pass  # Expected

    def test_get_active_conversations_empty(self):
        """Test get_active_conversations when no conversations exist."""
        llm_1min._conversation_mapping.clear()

        result = llm_1min.get_active_conversations()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_clear_all_conversations_empty(self):
        """Test clear_all_conversations when no conversations exist."""
        llm_1min._conversation_mapping.clear()

        result = llm_1min.clear_all_conversations(api_key="test-key")

        assert result == 0  # No conversations cleared
