"""
Shared pytest fixtures for llm-1min tests.
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / ".config" / "llm-1min"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create a temporary config file path."""
    return temp_config_dir / "config.json"


@pytest.fixture
def sample_config():
    """Sample configuration data."""
    return {
        "defaults": {
            "web_search": True,
            "num_of_site": 3
        },
        "models": {
            "gpt-4o": {
                "web_search": True,
                "num_of_site": 5
            },
            "sonar": {
                "num_of_site": 10
            }
        }
    }


@pytest.fixture
def empty_config():
    """Empty configuration."""
    return {"defaults": {}, "models": {}}


@pytest.fixture
def mock_api_response_success():
    """Mock successful API response from 1min.ai."""
    return {
        "aiRecord": {
            "uuid": "test-uuid-123",
            "status": "SUCCESS",
            "aiRecordDetail": {
                "promptObject": {
                    "prompt": "Test prompt"
                },
                "resultObject": "This is a test response from the AI model."
            }
        }
    }


@pytest.fixture
def mock_conversation_response():
    """Mock conversation creation response."""
    return {
        "conversation": {
            "uuid": "conv-uuid-456",
            "title": "Test Conversation",
            "type": "CHAT_WITH_AI",
            "model": "gpt-4o"
        }
    }


@pytest.fixture
def mock_conversations_list():
    """Mock list of conversations."""
    return {
        "conversations": [
            {
                "uuid": "conv-1",
                "title": "Test Chat 1",
                "type": "CHAT_WITH_AI",
                "model": "gpt-4o",
                "createdAt": "2025-11-10T10:00:00Z"
            },
            {
                "uuid": "conv-2",
                "title": "Test Chat 2",
                "type": "CODE_GENERATOR",
                "model": "claude-4-sonnet",
                "createdAt": "2025-11-10T11:00:00Z"
            }
        ]
    }


@pytest.fixture
def mock_requests(monkeypatch, mock_api_response_success, mock_conversation_response):
    """Mock requests library for API calls."""
    import requests

    # Mock response object for API calls
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response_success
    mock_response.raise_for_status = Mock()

    # Mock conversation response
    mock_conv_response = Mock()
    mock_conv_response.status_code = 200
    mock_conv_response.json.return_value = mock_conversation_response
    mock_conv_response.raise_for_status = Mock()

    # Create a smart mock that handles both endpoints
    class SmartMockResponse:
        """Mock that returns different responses based on URL."""
        def __call__(self, url, **kwargs):
            if "conversations" in url and "features" not in url:
                return mock_conv_response
            return mock_response

    smart_mock = SmartMockResponse()

    # Mock POST for different endpoints
    def mock_post(url, **kwargs):
        if "conversations" in url and "features" not in url:
            return mock_conv_response
        return mock_response

    # Mock DELETE
    mock_delete_response = Mock()
    mock_delete_response.status_code = 204

    def mock_delete(url, **kwargs):
        return mock_delete_response

    # Apply monkeypatch
    monkeypatch.setattr("requests.post", mock_post)
    monkeypatch.setattr("requests.delete", mock_delete)
    monkeypatch.setattr("requests.get", lambda url, **kwargs: Mock(
        status_code=200,
        json=lambda: {"conversations": []}
    ))

    return {
        "post": smart_mock,  # Return the smart mock that handles both endpoints
        "delete": mock_delete,
        "response": mock_response,
        "conv_response": mock_conv_response
    }


@pytest.fixture
def mock_llm_prompt():
    """Mock LLM prompt object."""
    prompt = Mock()
    prompt.prompt = "Test prompt"
    prompt.options = Mock()
    prompt.options.conversation_type = "CHAT_WITH_AI"
    prompt.options.web_search = False
    prompt.options.num_of_site = 3
    prompt.options.max_word = 500
    prompt.options.is_mixed = False
    return prompt


@pytest.fixture
def mock_llm_conversation():
    """Mock LLM conversation object."""
    conversation = Mock()
    conversation.id = "test-conv-123"
    return conversation


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key retrieval."""
    monkeypatch.setenv("ONEMIN_API_KEY", "test-api-key-12345")
    return "test-api-key-12345"


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_conversation_mapping():
    """Reset global conversation mapping before each test."""
    import llm_1min
    llm_1min._conversation_mapping.clear()
    yield
    llm_1min._conversation_mapping.clear()


@pytest.fixture(autouse=True)
def mock_config_path(tmp_path, monkeypatch):
    """Override config path for all tests to use temp directory."""
    import llm_1min

    # Create temp config dir
    config_dir = tmp_path / ".config" / "llm-1min"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"

    # Patch OptionsConfig to use temp path
    original_init = llm_1min.OptionsConfig.__init__

    def patched_init(self):
        self.config_path = config_path

    monkeypatch.setattr(llm_1min.OptionsConfig, "__init__", patched_init)

    # Reset global config instance
    llm_1min._options_config = llm_1min.OptionsConfig()

    yield config_path

    # Cleanup
    if config_path.exists():
        config_path.unlink()
