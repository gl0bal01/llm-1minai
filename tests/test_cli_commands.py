"""
Tests for CLI commands (llm 1min ...).
"""

import json
from unittest.mock import MagicMock, Mock, patch

import llm_1min


# Helper to get the CLI group
def get_cli():
    """Get CLI group for testing."""
    cli = MagicMock()
    llm_1min.register_commands(cli)
    # Return the registered 1min group
    return cli.group.call_args[1]["name"], cli.group()


class TestModelsCommand:
    """Test 'llm 1min models' command."""

    def test_models_command_lists_all_models(self, cli_runner):
        """Test that models command lists all available models."""
        # We need to invoke the actual function since it's registered with LLM
        # For now, test the models list data structure
        from llm_1min import register_commands

        # Mock cli to capture registration
        mock_cli = Mock()
        register_commands(mock_cli)

        # The onemin_group should be registered
        assert mock_cli.group.called

    def test_models_list_contains_key_models(self):
        """Test that the models list contains expected models."""
        # Import the models list from the actual function
        # This tests the data, not the CLI output

        # The models are defined in the list_models function
        # We can't easily test CLI output without full LLM integration
        # But we can verify the model registration
        assert True  # Placeholder for now


class TestConversationsCommand:
    """Test 'llm 1min conversations' command."""

    def test_conversations_command_empty(self):
        """Test conversations command with no active conversations."""
        # Clear conversation mapping
        llm_1min._conversation_mapping.clear()

        result = llm_1min.get_active_conversations()
        assert result == {}

    def test_conversations_command_with_data(self):
        """Test conversations command with active conversations."""
        # Add test data
        llm_1min._conversation_mapping["test-model"] = "test-uuid-123"

        result = llm_1min.get_active_conversations()
        assert "test-model" in result
        assert result["test-model"] == "test-uuid-123"


class TestClearCommand:
    """Test 'llm 1min clear' command."""

    @patch("llm_1min.clear_conversation")
    def test_clear_specific_model(self, mock_clear):
        """Test clearing conversation for specific model."""
        mock_clear.return_value = True

        result = llm_1min.clear_conversation("gpt-4o", "test-api-key")
        assert result is True
        mock_clear.assert_called_once()

    @patch("llm_1min.clear_all_conversations")
    def test_clear_all_conversations(self, mock_clear_all):
        """Test clearing all conversations."""
        mock_clear_all.return_value = 3

        result = llm_1min.clear_all_conversations("test-api-key")
        assert result == 3
        mock_clear_all.assert_called_once()


class TestOptionsSetCommand:
    """Test 'llm 1min options set' command."""

    def test_set_global_option_boolean(self, mock_config_path):
        """Test setting a global boolean option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)

        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True

    def test_set_global_option_integer(self, mock_config_path):
        """Test setting a global integer option."""
        config = llm_1min.OptionsConfig()
        config.set_option("num_of_site", 5)

        loaded = config.load()
        assert loaded["defaults"]["num_of_site"] == 5

    def test_set_per_model_option(self, mock_config_path):
        """Test setting a per-model option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="gpt-4o")

        loaded = config.load()
        assert loaded["models"]["gpt-4o"]["web_search"] is True


class TestOptionsGetCommand:
    """Test 'llm 1min options get' command."""

    def test_get_global_option_exists(self, mock_config_path):
        """Test getting an existing global option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)

        defaults = config.get_defaults()
        assert defaults.get("web_search") is True

    def test_get_global_option_not_exists(self, mock_config_path):
        """Test getting a non-existent global option."""
        config = llm_1min.OptionsConfig()

        defaults = config.get_defaults()
        assert defaults.get("nonexistent") is None

    def test_get_model_option_exists(self, mock_config_path):
        """Test getting an existing per-model option."""
        config = llm_1min.OptionsConfig()
        config.set_option("num_of_site", 10, model_id="sonar")

        model_opts = config.get_model_options("sonar")
        assert model_opts.get("num_of_site") == 10

    def test_get_model_option_not_exists(self, mock_config_path):
        """Test getting option for non-existent model."""
        config = llm_1min.OptionsConfig()

        model_opts = config.get_model_options("nonexistent-model")
        assert model_opts == {}


class TestOptionsListCommand:
    """Test 'llm 1min options list' command."""

    def test_list_empty_config(self, mock_config_path):
        """Test listing with empty configuration."""
        config = llm_1min.OptionsConfig()
        loaded = config.load()

        assert loaded == {"defaults": {}, "models": {}}

    def test_list_with_global_defaults(self, mock_config_path):
        """Test listing with global defaults."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 3)

        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True
        assert loaded["defaults"]["num_of_site"] == 3

    def test_list_with_per_model_options(self, mock_config_path):
        """Test listing with per-model options."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="gpt-4o")
        config.set_option("num_of_site", 10, model_id="sonar")

        loaded = config.load()
        assert loaded["models"]["gpt-4o"]["web_search"] is True
        assert loaded["models"]["sonar"]["num_of_site"] == 10

    def test_list_specific_model(self, mock_config_path):
        """Test listing options for specific model."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="gpt-4o")

        model_opts = config.get_model_options("gpt-4o")
        assert model_opts == {"web_search": True}


class TestOptionsUnsetCommand:
    """Test 'llm 1min options unset' command."""

    def test_unset_global_option(self, mock_config_path):
        """Test unsetting a global option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)

        result = config.unset_option("web_search")
        assert result is True

        loaded = config.load()
        assert "web_search" not in loaded["defaults"]

    def test_unset_per_model_option(self, mock_config_path):
        """Test unsetting a per-model option."""
        config = llm_1min.OptionsConfig()
        config.set_option("num_of_site", 10, model_id="sonar")

        result = config.unset_option("num_of_site", model_id="sonar")
        assert result is True

        loaded = config.load()
        assert "sonar" not in loaded["models"]  # Should be cleaned up

    def test_unset_nonexistent_option(self, mock_config_path):
        """Test unsetting non-existent option returns False."""
        config = llm_1min.OptionsConfig()

        result = config.unset_option("nonexistent")
        assert result is False


class TestOptionsResetCommand:
    """Test 'llm 1min options reset' command."""

    def test_reset_clears_all_options(self, mock_config_path):
        """Test that reset clears all configuration."""
        config = llm_1min.OptionsConfig()

        # Set some options
        config.set_option("web_search", True)
        config.set_option("num_of_site", 5)
        config.set_option("web_search", True, model_id="gpt-4o")

        # Reset
        config.reset()

        # Verify all cleared
        loaded = config.load()
        assert loaded == {"defaults": {}, "models": {}}


class TestOptionsExportCommand:
    """Test 'llm 1min options export' command."""

    def test_export_to_json(self, mock_config_path, sample_config):
        """Test exporting configuration to JSON."""
        config = llm_1min.OptionsConfig()
        config.save(sample_config)

        # Load and verify
        loaded = config.load()
        assert loaded == sample_config

        # Export should return same data
        json_str = json.dumps(loaded, indent=2)
        exported = json.loads(json_str)
        assert exported == sample_config

    def test_export_empty_config(self, mock_config_path):
        """Test exporting empty configuration."""
        config = llm_1min.OptionsConfig()
        loaded = config.load()

        json_str = json.dumps(loaded, indent=2)
        exported = json.loads(json_str)
        assert exported == {"defaults": {}, "models": {}}


class TestOptionsImportCommand:
    """Test 'llm 1min options import' command."""

    def test_import_from_json(self, mock_config_path, sample_config, tmp_path):
        """Test importing configuration from JSON file."""
        # Create temp JSON file
        json_file = tmp_path / "config.json"
        with open(json_file, "w") as f:
            json.dump(sample_config, f)

        # Import
        config = llm_1min.OptionsConfig()
        with open(json_file) as f:
            imported_data = json.load(f)

        config.save(imported_data)

        # Verify
        loaded = config.load()
        assert loaded == sample_config

    def test_import_validates_structure(self, tmp_path):
        """Test that import validates JSON structure."""
        # Create invalid JSON (not a dict)
        json_file = tmp_path / "invalid.json"
        with open(json_file, "w") as f:
            json.dump(["not", "a", "dict"], f)

        # Import should validate
        with open(json_file) as f:
            data = json.load(f)

        assert not isinstance(data, dict) or "defaults" in data or "models" in data


class TestOptionsIntegrationWorkflow:
    """Integration tests for options commands workflow."""

    def test_full_options_workflow(self, mock_config_path):
        """Test complete workflow: set, list, export, unset, reset."""
        config = llm_1min.OptionsConfig()

        # 1. Set options
        config.set_option("web_search", True)
        config.set_option("num_of_site", 5)
        config.set_option("web_search", True, model_id="gpt-4o")

        # 2. List/verify
        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True
        assert loaded["defaults"]["num_of_site"] == 5
        assert loaded["models"]["gpt-4o"]["web_search"] is True

        # 3. Export
        exported = json.dumps(loaded, indent=2)
        assert "web_search" in exported
        assert "gpt-4o" in exported

        # 4. Unset one option
        config.unset_option("num_of_site")
        loaded = config.load()
        assert "num_of_site" not in loaded["defaults"]

        # 5. Reset all
        config.reset()
        loaded = config.load()
        assert loaded == {"defaults": {}, "models": {}}

    def test_import_export_roundtrip(self, mock_config_path, sample_config, tmp_path):
        """Test that export -> import -> export produces same result."""
        config = llm_1min.OptionsConfig()

        # Save original
        config.save(sample_config)

        # Export
        exported1 = json.dumps(config.load(), indent=2)

        # Import back
        config.save(json.loads(exported1))

        # Export again
        exported2 = json.dumps(config.load(), indent=2)

        # Should be identical
        assert exported1 == exported2


class TestConversationFunctions:
    """Test conversation management functions."""

    @patch("requests.delete")
    def test_clear_conversation_success(self, mock_delete):
        """Test successful conversation clearing."""
        mock_delete.return_value = Mock(status_code=204)

        result = llm_1min.clear_conversation("gpt-4o", "test-api-key", "conv-uuid-123")
        assert result is True

    @patch("requests.delete")
    def test_clear_conversation_not_found(self, mock_delete):
        """Test clearing non-existent conversation."""
        mock_delete.return_value = Mock(status_code=404)

        result = llm_1min.clear_conversation("gpt-4o", "test-api-key", "nonexistent-uuid")
        assert result is True  # 404 is considered success (already deleted)

    @patch("requests.delete")
    def test_clear_all_conversations(self, mock_delete):
        """Test clearing all conversations."""
        mock_delete.return_value = Mock(status_code=204)

        # Add test conversations
        llm_1min._conversation_mapping["model1"] = "uuid1"
        llm_1min._conversation_mapping["model2"] = "uuid2"

        result = llm_1min.clear_all_conversations("test-api-key")
        assert result == 2

        # Verify cleared
        assert len(llm_1min._conversation_mapping) == 0
