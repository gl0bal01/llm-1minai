"""
Tests for OptionsConfig class - persistent configuration management.
"""

import json

import llm_1min


class TestOptionsConfigInitialization:
    """Test OptionsConfig initialization and path handling."""

    def test_config_uses_temp_path(self, mock_config_path):
        """Test that config uses temporary path in tests."""
        config = llm_1min.OptionsConfig()
        assert config.config_path == mock_config_path
        assert config.config_path.parent.exists()


class TestOptionsConfigLoadSave:
    """Test configuration loading and saving."""

    def test_load_nonexistent_file_returns_empty_config(self, mock_config_path):
        """Test loading when config file doesn't exist."""
        config = llm_1min.OptionsConfig()
        result = config.load()
        assert result == {"defaults": {}, "models": {}}

    def test_save_creates_config_file(self, mock_config_path, sample_config):
        """Test saving creates the config file."""
        config = llm_1min.OptionsConfig()
        config.save(sample_config)

        assert mock_config_path.exists()

        # Verify content
        with open(mock_config_path) as f:
            loaded = json.load(f)
        assert loaded == sample_config

    def test_load_existing_file_returns_content(self, mock_config_path, sample_config):
        """Test loading existing config file."""
        # Write config file
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        result = config.load()
        assert result == sample_config

    def test_load_corrupted_file_returns_empty_config(self, mock_config_path):
        """Test loading corrupted JSON returns empty config."""
        # Write invalid JSON
        with open(mock_config_path, "w") as f:
            f.write("{invalid json")

        config = llm_1min.OptionsConfig()
        result = config.load()
        assert result == {"defaults": {}, "models": {}}


class TestOptionsConfigGetters:
    """Test configuration getter methods."""

    def test_get_defaults_empty_config(self, mock_config_path):
        """Test get_defaults with empty config."""
        config = llm_1min.OptionsConfig()
        result = config.get_defaults()
        assert result == {}

    def test_get_defaults_with_data(self, mock_config_path, sample_config):
        """Test get_defaults with existing data."""
        # Save sample config
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        result = config.get_defaults()
        assert result == {"web_search": True, "num_of_site": 3}

    def test_get_model_options_nonexistent_model(self, mock_config_path):
        """Test get_model_options for non-existent model."""
        config = llm_1min.OptionsConfig()
        result = config.get_model_options("nonexistent-model")
        assert result == {}

    def test_get_model_options_existing_model(self, mock_config_path, sample_config):
        """Test get_model_options for existing model."""
        # Save sample config
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        result = config.get_model_options("gpt-4o")
        assert result == {"web_search": True, "num_of_site": 5}


class TestOptionsConfigSetters:
    """Test configuration setter methods."""

    def test_set_option_global(self, mock_config_path):
        """Test setting a global option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)

        # Verify saved
        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True

    def test_set_option_per_model(self, mock_config_path):
        """Test setting a per-model option."""
        config = llm_1min.OptionsConfig()
        config.set_option("num_of_site", 5, model_id="gpt-4o")

        # Verify saved
        loaded = config.load()
        assert loaded["models"]["gpt-4o"]["num_of_site"] == 5

    def test_set_multiple_options(self, mock_config_path):
        """Test setting multiple options."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 3)
        config.set_option("max_word", 1000)

        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True
        assert loaded["defaults"]["num_of_site"] == 3
        assert loaded["defaults"]["max_word"] == 1000

    def test_set_option_overwrite_existing(self, mock_config_path):
        """Test overwriting an existing option."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", False)
        config.set_option("web_search", True)  # Overwrite

        loaded = config.load()
        assert loaded["defaults"]["web_search"] is True

    def test_set_option_multiple_models(self, mock_config_path):
        """Test setting options for multiple models."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="gpt-4o")
        config.set_option("num_of_site", 10, model_id="sonar")

        loaded = config.load()
        assert loaded["models"]["gpt-4o"]["web_search"] is True
        assert loaded["models"]["sonar"]["num_of_site"] == 10


class TestOptionsConfigUnset:
    """Test configuration unset methods."""

    def test_unset_global_option(self, mock_config_path, sample_config):
        """Test unsetting a global option."""
        # Save sample config
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        result = config.unset_option("web_search")
        assert result is True

        loaded = config.load()
        assert "web_search" not in loaded["defaults"]

    def test_unset_nonexistent_option_returns_false(self, mock_config_path):
        """Test unsetting non-existent option returns False."""
        config = llm_1min.OptionsConfig()
        result = config.unset_option("nonexistent")
        assert result is False

    def test_unset_model_option(self, mock_config_path, sample_config):
        """Test unsetting a per-model option."""
        # Save sample config
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        result = config.unset_option("num_of_site", model_id="gpt-4o")
        assert result is True

        loaded = config.load()
        assert "num_of_site" not in loaded["models"]["gpt-4o"]

    def test_unset_cleans_up_empty_model(self, mock_config_path):
        """Test that unsetting last option removes empty model entry."""
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True, model_id="test-model")
        config.unset_option("web_search", model_id="test-model")

        loaded = config.load()
        assert "test-model" not in loaded["models"]


class TestOptionsConfigReset:
    """Test configuration reset."""

    def test_reset_clears_all_options(self, mock_config_path, sample_config):
        """Test reset clears all configuration."""
        # Save sample config
        with open(mock_config_path, "w") as f:
            json.dump(sample_config, f)

        config = llm_1min.OptionsConfig()
        config.reset()

        loaded = config.load()
        assert loaded == {"defaults": {}, "models": {}}

    def test_reset_on_empty_config(self, mock_config_path):
        """Test reset on already empty config."""
        config = llm_1min.OptionsConfig()
        config.reset()  # Should not raise error

        loaded = config.load()
        assert loaded == {"defaults": {}, "models": {}}


class TestOptionsConfigIntegration:
    """Integration tests for OptionsConfig."""

    def test_full_workflow(self, mock_config_path):
        """Test complete workflow: set, get, unset, reset."""
        config = llm_1min.OptionsConfig()

        # Set global
        config.set_option("web_search", True)
        assert config.get_defaults()["web_search"] is True

        # Set per-model
        config.set_option("num_of_site", 5, model_id="gpt-4o")
        assert config.get_model_options("gpt-4o")["num_of_site"] == 5

        # Unset
        config.unset_option("web_search")
        assert "web_search" not in config.get_defaults()

        # Reset
        config.reset()
        assert config.load() == {"defaults": {}, "models": {}}

    def test_global_and_per_model_options_coexist(self, mock_config_path):
        """Test that global and per-model options work together."""
        config = llm_1min.OptionsConfig()

        # Set global
        config.set_option("web_search", True)
        config.set_option("num_of_site", 3)

        # Set per-model (different value)
        config.set_option("num_of_site", 10, model_id="sonar")

        # Verify both exist
        defaults = config.get_defaults()
        assert defaults["web_search"] is True
        assert defaults["num_of_site"] == 3

        model_opts = config.get_model_options("sonar")
        assert model_opts["num_of_site"] == 10
