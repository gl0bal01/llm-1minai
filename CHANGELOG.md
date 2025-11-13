# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-10

### Added
- **Web Search for All Models**: Enable real-time web search with any model using `web_search`, `num_of_site`, and `max_word` options
- **Mixed Model Context**: Share conversation context between different models with `is_mixed` option
- **Persistent Options Management**: Complete configuration system with 8 new commands:
  - `llm 1min options set` - Set global or per-model defaults
  - `llm 1min options get` - Retrieve option values
  - `llm 1min options list` - View all configurations
  - `llm 1min options unset` - Remove options
  - `llm 1min options reset` - Reset all to defaults
  - `llm 1min options export` - Backup configuration
  - `llm 1min options import` - Restore configuration
- **54 New Models** - Expanded from 12 to 66 models:
  - OpenAI: GPT-3.5 Turbo, GPT-4 Turbo, GPT-4.1 variants, GPT-5 variants, O4 Mini
  - Anthropic: Claude 3 Haiku, Claude 4 Opus
  - Google: Gemini 2.0 Flash, Gemini 2.5 variants
  - xAI: Grok 3, Grok 4 variants
  - Mistral: Open Mistral Nemo, Mistral Small/Large, Pixtral 12B
  - Meta/LLaMA: LLaMA 2/3/3.1/4 variants, GPT OSS models
  - Cohere: Command R
- **New Provider Support**: Mistral, Meta/LLaMA, Cohere (now 9 providers total)
- **Comprehensive Test Suite**: 112 unit tests with 50% code coverage
  - `tests/test_options_config.py` - 19 tests for options management
  - `tests/test_model_execution.py` - 12 tests for model execution and API integration
  - `tests/test_cli_commands.py` - 30 tests for CLI commands
  - `tests/test_integration.py` - 51 tests for integration and edge cases
  - `tests/conftest.py` - Shared fixtures and mocks
  - `tests/fixtures/sample_responses.json` - Mock API responses
- **GitHub Actions CI/CD**: Automated testing and code quality
  - `.github/workflows/test.yml` - Tests on Python 3.8-3.12
  - `.github/workflows/lint.yml` - Code formatting (black) and linting (ruff)
  - Parallel test execution across multiple Python versions
  - Coverage reporting and validation
- **Testing Documentation**: Complete guide in `TESTING.md`
  - How to run tests locally
  - Test structure and organization
  - Coverage reports and CI/CD integration
  - Contributing guidelines for tests
- Configuration storage at `~/.config/llm-1min/config.json` with XDG standard compliance
- Option priority hierarchy: CLI flags > per-model config > global defaults > code defaults
- Comprehensive documentation for advanced features

### Changed
- Expanded model count from 12 to 66 models across 9 providers
- Enhanced `execute()` method to merge options from multiple sources
- Updated README.md with Options Management section and advanced usage examples
- Updated MODEL_SELECTION.md with Advanced Features section
- Improved .gitignore to exclude user configuration files and test artifacts
- Enhanced security documentation with best practices
- Updated pyproject.toml with test dependencies and pytest configuration

### Fixed
- Options now properly validated with pydantic validators
- Mock configuration in tests properly handles multiple API endpoints

## [0.1.0] - 2025-11-09

### Added
- Initial release of llm-1min plugin
- Support for 12 AI models from 1min.ai:
  - OpenAI: GPT-4o Mini, GPT-4o, O3 Mini, O1 Mini
  - Anthropic: Claude 3.7 Sonnet, Claude 4 Sonnet
  - Google: Gemini 1.5 Pro
  - DeepSeek: DeepSeek Chat, DeepSeek R1
  - Perplexity: Sonar, Sonar Reasoning
  - xAI: Grok 2
- Conversation management:
  - `llm 1min conversations` - List active conversations
  - `llm 1min clear` - Clear conversations
- Model discovery: `llm 1min models` - List available models with descriptions
- Secure API key management via `llm keys set 1min`
- Two conversation types: `CHAT_WITH_AI` and `CODE_GENERATOR`
- Automatic conversation tracking per model
- Response parsing from 1min.ai API
- Advanced conversation management utility script (`manage_conversations.py`):
  - List all conversations from server
  - Get conversation details
  - Delete specific conversations
  - Export conversations to JSON
- API testing utility (`test_api.py`)
- Comprehensive documentation:
  - README.md with usage examples
  - MODEL_SELECTION.md with model selection guide
- Error handling with helpful messages
- Apache 2.0 license

### Security
- API keys stored securely via LLM's key management
- Support for `ONEMIN_API_KEY` environment variable
- Proper timeout values on all HTTP requests
- No credential logging or exposure

## [Unreleased]

### Planned
- Streaming support for real-time responses
- Image generation and variation support
- PDF and YouTube video chat capabilities
- Additional model providers as they become available

---

## Version History

- **0.2.0** (2025-11-10): Major feature release - Web search, mixed context, 66 models, persistent options
- **0.1.0** (2025-11-09): Initial release - 12 models, basic conversation management

## Migration Guide

### Upgrading from 0.1.0 to 0.2.0

**No breaking changes!** All existing functionality continues to work.

**New capabilities you can use:**

```bash
# Enable web search globally
llm 1min options set web_search true

# Set per-model defaults
llm 1min options set --model gpt-4o num_of_site 5

# Use new models
llm -m 1min/gpt-5 "Your prompt"
llm -m 1min/claude-4-opus "Your prompt"
llm -m 1min/gemini-2.5-pro "Your prompt"

# Share context between models
llm -m 1min/gpt-4o -o is_mixed true "Start discussion"
llm -m 1min/claude-4-opus -o is_mixed true "Continue"
```

**Configuration location:**
- Stored at: `~/.config/llm-1min/config.json` (or `~/.llm-1min.json` as fallback)
- Not committed to git (automatically ignored)

## Contributing

See [README.md](README.md) for contribution guidelines.

## Links

- [GitHub Repository](https://github.com/gl0bal01/llm-1min)
- [PyPI Package](https://pypi.org/project/llm-1min/)
- [1min.ai](https://1min.ai)
- [LLM Documentation](https://llm.datasette.io/)
