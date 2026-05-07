# llm-1minai

[![PyPI](https://img.shields.io/pypi/v/llm-1minai.svg)](https://pypi.org/project/llm-1minai/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/gl0bal01/llm-1minai/blob/main/LICENSE)
[![Tests](https://github.com/gl0bal01/llm-1minai/workflows/Tests/badge.svg)](https://github.com/gl0bal01/llm-1minai/actions)
[![Code Quality](https://github.com/gl0bal01/llm-1minai/workflows/Code%20Quality/badge.svg)](https://github.com/gl0bal01/llm-1minai/actions)

Plugin for [LLM](https://llm.datasette.io/) adding support for [1min.ai](https://1min.ai) AI models.

Access **75+ AI models** through a single API: Claude 4.6 Sonnet/Opus, Claude 4.5 Haiku, GPT-5.4, GPT-5.1 Codex, o3 / o4, Gemini 3.1, Qwen3, DeepSeek V3.2, Mistral, LLaMA 4, Grok 4, Sonar, and more.

Built on the unified `/api/chat-with-ai` endpoint with SSE streaming, image and file attachments, AI memory across conversations, brand voice, and structured prompt settings.

> **Looking for a standalone CLI?** [`omi`](https://github.com/gl0bal01/omi) is a single-binary Go port of this plugin. No Python required, sub-20ms startup, same `API-KEY` and same routing (UNIFY_CHAT_WITH_AI for chat / vision / docs, CODE_GENERATOR + SPEECH_TO_TEXT on `/api/features`). Run `go install github.com/gl0bal01/omi/cmd/omi@latest`.

## Installation

### Using LLM's Plugin Manager (Recommended)

Install this plugin in the same environment as LLM:

```bash
llm install llm-1minai
```

### Using pipx

If you installed LLM with pipx, inject the plugin into the LLM environment:

```bash
pipx inject llm llm-1minai
```

Or install both LLM and the plugin with pipx:

```bash
pipx install llm
pipx inject llm llm-1minai
```

### From Source (Development)

Install from source for development:

```bash
git clone https://github.com/gl0bal01/llm-1minai
cd llm-1minai
llm install -e .
```

Or with pipx:

```bash
git clone https://github.com/gl0bal01/llm-1minai
cd llm-1minai
pipx inject llm -e .
```

## Upgrade or Uninstall

### Upgrade an existing install

```bash
# Plugin-manager install
llm install -U llm-1minai

# pipx-injected install
pipx runpip llm install -U llm-1minai

# Editable / source install
cd llm-1minai && git pull && llm install -e .
```

### Uninstall

```bash
# Plugin-manager install
llm uninstall llm-1minai

# pipx-injected install
pipx uninject llm llm-1minai

# Editable / source install
pip uninstall llm-1minai
```

### Verify removal

```bash
llm models list | grep 1min   # should print nothing
llm plugins | grep 1min       # should print nothing
```

### Wipe local data (optional)

The plugin keeps user settings and the conversation-UUID map at
`~/.config/llm-1min/`. Remove them after uninstall if you want a clean slate:

```bash
rm -rf ~/.config/llm-1min/
```

The 1min.ai API key is stored separately by LLM, not under that directory:

```bash
llm keys remove 1min
unset ONEMIN_API_KEY  # if you exported it
```

### Migrating to the standalone Go CLI

If you're switching to [`omi`](https://github.com/gl0bal01/omi), it uses a
different config dir (`~/.config/omi/`) and won't conflict with leftover
Python-plugin state. After uninstalling above:

```bash
go install github.com/gl0bal01/omi/cmd/omi@latest
omi config set api_key sk-...
```

## Configuration

You need a 1min.ai API key to use this plugin. Get one from [1min.ai](https://1min.ai).

Set your API key using:

```bash
llm keys set 1min
# Paste your API key when prompted
```

Or set it as an environment variable:

```bash
export ONEMIN_API_KEY="your-api-key-here"
```

## Available Models

### Quick View

See all 1min.ai models in your terminal:

```bash
# Show all LLM models (look for "1min.ai:" prefix)
llm models list | grep "1min.ai"

# Or use our dedicated command with descriptions
llm 1min models
```

### Model Categories

**75+ models across 10 providers (v0.4.0):**

- **OpenAI** (~25 models): GPT-3.5/4/4.1/4o, GPT-5, GPT-5.1, GPT-5.1 Codex /
  Codex Mini, GPT-5.2 / 5.2 Pro, GPT-5.4 / Mini / Nano / Pro, o3 / o3 Pro /
  o3 Deep Research, o4 Mini / o4 Mini Deep Research
- **Anthropic** (8 models): Claude 4 / 4.5 / 4.6 Sonnet,
  Claude 4 / 4.1 / 4.5 / 4.6 Opus, Claude 4.5 Haiku
- **Google** (5 models): Gemini 2.5 Flash / Pro,
  Gemini 3 Flash / 3.1 Flash Lite / 3.1 Pro (Preview)
- **Alibaba (Qwen)** (10 models): Qwen3 Max / VL Plus / VL Flash /
  Coder Plus / Coder Flash, Qwen Max / Plus / Flash / VL Max / VL Plus
- **DeepSeek** (2 models): DeepSeek V3.2 Chat, DeepSeek V3.2 Reasoner
- **xAI** (6 models): Grok 3 / 3 Mini, Grok 4, Grok 4 Fast Reasoning /
  Non-Reasoning, Grok Code Fast 1
- **Mistral** (7 models): Mistral Small / Medium 3.1 / Large 2,
  Magistral Small / Medium 1.2, Ministral 14B, Open Mistral Nemo
- **Meta / open-source** (6 models): LLaMA 2 70b, LLaMA 3 70b,
  LLaMA 4 Scout / Maverick, GPT OSS 20b / 120b
- **Cohere** (1 model): Command R
- **Perplexity** (4 models): Sonar, Sonar Pro, Sonar Reasoning Pro,
  Sonar Deep Research

**Important**: Use `llm 1min models` to see all available models with descriptions.

For a complete model reference with IDs and usage examples, see [MODEL_SELECTION.md](./MODEL_SELECTION.md).

## Usage

### List Available Models

First, see what models are available:

```bash
# See model IDs and friendly names
llm 1min models

# Or see just the model IDs
llm models list | grep "1min.ai"
# Output example:
# 1min.ai: gpt-4o-mini          ← Use this ID with -m flag
# 1min.ai: claude-sonnet-4-20250514
```

### Basic Usage

Use the model ID (shown after "1min.ai:") with the `-m` flag:

```bash
# Fast and efficient - GPT-4o Mini
llm -m 1min/gpt-4o-mini "Explain quantum computing in simple terms"

# Most powerful - Claude 4 Opus or GPT-5
llm -m 1min/claude-4-opus "Design a complex system architecture"
llm -m 1min/gpt-5 "Advanced reasoning task"

# Best for coding - Claude 4 Sonnet
llm -m 1min/claude-4-sonnet "Write a REST API with FastAPI"

# Best for reasoning - O4 Mini or DeepSeek R1
llm -m 1min/o4-mini "Solve this logic puzzle"
llm -m 1min/deepseek-reasoner "Complex math problem"

# Web-aware - Sonar or Sonar Reasoning
llm -m 1min/sonar "What are the latest AI developments?"
llm -m 1min/sonar-reasoning-pro "Research topic with citations"

# Fast responses - Claude 4.5 Haiku or Gemini Flash
llm -m 1min/claude-4-5-haiku "Quick question"
llm -m 1min/gemini-2.5-flash "Fast response needed"
```

### Debug Mode (Troubleshooting)

See exactly what's being sent to the API:

```bash
# Enable debug to see all options and API payload
llm -m 1min/gpt-4o -o debug true "test prompt"

# Or use environment variable
LLM_1MIN_DEBUG=1 llm -m 1min/gpt-4o "test prompt"

# See all available options for any model
llm models --options | grep -A 8 "1min/gpt-4o"
```

**Note**: The `-d` flag is already used by LLM for database operations, so debug uses `-o debug true`.
Debug output redacts prompt text, attachment keys/IDs, and brand voice IDs by default.
For more details, see [DEBUG_USAGE.md](DEBUG_USAGE.md)

### Conversation Mode (Chat)

Continue a conversation with context using the `-c` flag:

```bash
# Start a conversation
llm -m 1min/gpt-4o "Hello, I need help with Python"

# Continue the conversation (uses -c flag)
llm -m 1min/gpt-4o -c "What are list comprehensions?"

# Keep going - model is remembered automatically
llm -c "Show me an example"

# Resume a specific conversation by ID
llm -c --cid <conversation-id> "Continue this topic"

# View conversation history
llm logs -n 5
```

**Important:** The `-c` flag is handled by the LLM framework, not this plugin. Each continuation re-sends prior messages to maintain context.

See the [LLM chat documentation](https://llm.datasette.io/en/stable/usage.html#continuing-a-conversation) for more details.

### Code Generation

Code-focused models automatically use `CODE_GENERATOR` mode by default:

```bash
# These models auto-use CODE_GENERATOR (no -o needed)
llm -m 1min/claude-4-6-sonnet "Create a REST API with FastAPI"
llm -m 1min/qwen3-coder-plus "Create a simple REST API with Go"
llm -m 1min/grok-code-fast-1 "Optimize this algorithm"
llm -m 1min/deepseek-reasoner "Refactor this function"

# Explicitly set for other models
llm -m 1min/gpt-4o \
  -o conversation_type CODE_GENERATOR \
  "Write a binary search function"
```

**Built-in defaults** (see `llm 1min options defaults`):
- **Code models**: `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5-20251001`,
  `qwen3-coder-plus`, `qwen3-coder-flash`, `grok-code-fast-1`,
  `gpt-5.1-codex`, `gpt-5.1-codex-mini`, `deepseek-reasoner` → `CODE_GENERATOR`
- **Web-aware models**: `sonar`, `sonar-pro`, `sonar-reasoning-pro`,
  `sonar-deep-research`, `o3-deep-research`, `o4-mini-deep-research` → `web_search=true`

### Advanced Options

#### Available Options

- **conversation_type**: `UNIFY_CHAT_WITH_AI` (default) or `CODE_GENERATOR`
- **web_search**: Enable real-time web search (true/false, default: false)
- **num_of_site**: Number of sites to search when web_search is enabled (1-10, default: 3)
- **max_word**: Maximum words from web search results (100-10000, default: 1000)
- **history_mixed**: Mix context between different models (true/false, default: false)
  *(renamed from `is_mixed` in v0.4.0; run `llm 1min options migrate` to update saved configs)*
- **history_limit**: Max history messages included as context (1-50, default: 10)
- **with_memories**: Enable AI memory across conversations (true/false, default: false)
- **brand_voice_id**: Brand voice ID for response style (string, default: none)
- **images**: Comma-separated image asset keys from Asset API (string, default: none)
- **files**: Comma-separated file IDs from Asset API (string, default: none)
- **debug**: Show detailed API request information (true/false, default: false)
  - Use: `-o debug true` (Note: `-d` is taken by LLM's database option)
  - See: [DEBUG_USAGE.md](DEBUG_USAGE.md) for details

#### One-Time Usage (CLI Flags)

```bash
# Enable web search for any model
llm -m 1min/gpt-4o \
  -o web_search true \
  -o num_of_site 5 \
  "What's the latest in AI?"

# Use code generator mode
llm -m 1min/gpt-4o \
  -o conversation_type CODE_GENERATOR \
  "Write a binary search algorithm"

# Mix context between models
# Start a conversation first (no -c needed for the first turn)
llm -m 1min/gpt-4o "My name is Fabien"

# Continue with a different model: -c reuses the LLM conversation,
# history_mixed=true shares the 1min.ai conversation UUID across models.
llm -m 1min/claude-4-6-opus -c -o history_mixed true "What is my name?"

# Stream responses (SSE) - streaming is the default for `llm prompt`
llm -m 1min/gpt-4o "Explain transformers in 200 words"

# Disable streaming with --no-stream
llm -m 1min/gpt-4o --no-stream "Explain transformers in 200 words"

# Image attachments — upload first to get an asset key
KEY=$(llm 1min upload -q photo.png)
llm -m 1min/gpt-4o -o images "$KEY" "What do you see in this image?"

# Or upload interactively (prints key + usage hint)
llm 1min upload photo.png

# Cross-conversation memory
llm -m 1min/gpt-4o -o with_memories true "Remember I prefer Python over JS"

# Debug mode - see what's being sent to the API
llm -m 1min/gpt-4o -o debug true "test prompt"

# Alternative: environment variable
LLM_1MIN_DEBUG=1 llm -m 1min/gpt-4o "test prompt"

# Or set as default (useful for troubleshooting)
llm 1min options set debug true
```

#### Persistent Configuration

Set default options that apply automatically:

```bash
# Set global defaults
llm 1min options set web_search true
llm 1min options set num_of_site 5

# Now web search is enabled by default
llm -m 1min/gpt-4o "Latest AI news"  # Uses web_search=true automatically

# Set per-model options
llm 1min options set --model gpt-4o web_search true
llm 1min options set --model sonar num_of_site 10

# View all options
llm 1min options list

# View specific option
llm 1min options get web_search

# Remove an option
llm 1min options unset web_search

# Reset everything
llm 1min options reset
```

**Priority hierarchy** (highest to lowest):
1. CLI flags (`-o web_search true`)
2. Per-model config (`--model gpt-4o`)
3. Global defaults
4. Code defaults

### List 1min.ai Models

```bash
# Show 1min.ai models with descriptions
llm 1min models

# Or see all models (including non-1min.ai)
llm models list | grep "1min.ai"
```

### View Logs

```bash
# View last response
llm logs -n 1

# View last 5 responses
llm logs -n 5
```

### Options Management

Manage persistent options that apply automatically to your models:

```bash
# Set global defaults
llm 1min options set web_search true
llm 1min options set num_of_site 5
llm 1min options set max_word 1000

# Set per-model options
llm 1min options set --model gpt-4o web_search true
llm 1min options set --model sonar num_of_site 10

# List all options
llm 1min options list

# List options for specific model
llm 1min options list --model gpt-4o

# Get specific option value
llm 1min options get web_search
llm 1min options get --model gpt-4o web_search

# Remove options
llm 1min options unset web_search
llm 1min options unset --model gpt-4o num_of_site

# Export/import configuration
llm 1min options export --output my-config.json
llm 1min options import my-config.json

# Reset all options
llm 1min options reset
```

**Example config file** (`~/.config/llm-1min/config.json`):
```json
{
  "defaults": {
    "web_search": true,
    "num_of_site": 3
  },
  "models": {
    "gpt-4o": {
      "web_search": true,
      "num_of_site": 5
    },
    "sonar": {
      "num_of_site": 10
    }
  }
}
```

### Conversation Management

The plugin provides commands to manage your 1min.ai conversations:

```bash
# List all active conversations
llm 1min conversations

# Clear conversation for a specific model
llm 1min clear --model gpt-4o-mini

# Clear all conversations
llm 1min clear --all
```

**Advanced Conversation Management:**

Use the included utility script for more options:

```bash
# List all conversations on 1min.ai server
python manage_conversations.py list

# Get details of a specific conversation
python manage_conversations.py get <conversation-uuid>

# Delete a specific conversation
python manage_conversations.py delete <conversation-uuid>

# Clear all conversations from server
python manage_conversations.py clear --all

# Export conversations to JSON
python manage_conversations.py export --output my-conversations.json
```

## Features

- ✅ **75+ AI models** from 10 providers through a single API
- ✅ **Latest models**: Claude 4.6 Sonnet/Opus, Claude 4.5 Haiku, GPT-5.4 / 5.1 Codex,
  o3 / o4 (incl. deep-research), Gemini 3.1, Qwen3 Max / Coder, DeepSeek V3.2,
  Grok 4, LLaMA 4, Magistral, Sonar
- ✅ **Unified chat endpoint** (`/api/chat-with-ai`) with structured `settings`
- ✅ **SSE streaming**: stream `content` chunks live via `llm chat --stream`
- ✅ **Attachments**: pass image keys / file IDs via `images` and `files` options
- ✅ **AI memory**: cross-conversation memory via `with_memories`
- ✅ **Brand voice**: per-call `brand_voice_id`
- ✅ **Web search**: real-time grounding on any model
- ✅ **Mixed history**: share conversation history across models (`history_mixed`)
- ✅ **Persistent options**: global and per-model defaults; `options migrate` for upgrades
- ✅ **Test suite**: 144 tests, 55% coverage
- ✅ **CI/CD**: GitHub Actions for automated testing on Python 3.8-3.12
- ✅ Conversation history tracking and management
- ✅ Specialized code generation mode
- ✅ Automatic conversation management
- ✅ List, export, and clear conversations
- ✅ Secure API key management
- ✅ Proper error handling with helpful messages
- ✅ Comprehensive model documentation

## How It Works

This plugin uses the 1min.ai API v2 (`/api/chat-with-ai`) for chat models and
the legacy `/api/features` endpoint for code generation:

1. **Conversation Creation**: When you start a chat, the plugin creates a
   conversation of type `UNIFY_CHAT_WITH_AI` on 1min.ai.
2. **Chat Messages**: Chat prompts POST to `/api/chat-with-ai` with structured
   `promptObject.settings` (web search, history, memory) and optional
   `attachments` (images, files).
3. **Code Generation**: When `conversation_type=CODE_GENERATOR`, prompts go to
   the legacy `/api/features` endpoint with the flat `promptObject` shape.
4. **Streaming**: Pass `--stream` (`llm chat --stream ...`) to receive
   server-sent events (`content` chunks streamed live; `done` terminates).
5. **Context Management**: Conversations are tracked per model in
   `~/.config/llm-1min/conversations.json`.

### API Endpoints Used

- `POST https://api.1min.ai/api/chat-with-ai` — chat (UNIFY_CHAT_WITH_AI),
  add `?isStreaming=true` for SSE streaming
- `POST https://api.1min.ai/api/features` — CODE_GENERATOR only
- `POST https://api.1min.ai/api/conversations` — create conversation context
- `GET  https://api.1min.ai/api/conversations` — list all conversations
- `GET  https://api.1min.ai/api/conversations/{uuid}` — get specific conversation
- `DELETE https://api.1min.ai/api/conversations/{uuid}` — delete/clear a conversation
- `POST https://api.1min.ai/api/assets` — upload images/files (use the asset
  key returned in responses with the `images` / `files` options)

### Authentication

The plugin uses the `API-KEY` header format (not OAuth/Bearer tokens).

## Security Best Practices

### API Key Management

- ✅ **Never hardcode API keys** in scripts or code
- ✅ Use environment variables: `export ONEMIN_API_KEY="your-key"`
- ✅ Or use LLM's secure key storage: `llm keys set 1min`
- ✅ Add `.env` files to `.gitignore` if used
- ✅ Rotate keys periodically

### Script Security

All scripts in this repository follow security best practices:
- API keys are read from environment variables only
- No credentials are logged or printed
- Proper timeout values on all HTTP requests
- Error handling prevents information leakage
- Input validation where applicable

## Development

### Project Structure

```
llm-1min/
├── llm_1min.py              # Main plugin implementation
├── manage_conversations.py  # Conversation management utility
├── test_api.py              # API testing utility
├── tests/                   # Test suite (144 tests)
│   ├── test_options_config.py    # Options + legacy-key rejection (28 tests)
│   ├── test_model_execution.py   # Model execution + payload shape (18 tests)
│   ├── test_cli_commands.py      # CLI command tests (30 tests)
│   ├── test_streaming.py         # SSE parser tests (4 tests)
│   ├── test_attachments.py       # Attachments / memory / brand voice (8 tests)
│   ├── test_web_search_config.py # Nested settings.webSearchSettings (4 tests)
│   ├── test_web_search_debug.py  # Debug payload inspection (3 tests)
│   ├── test_debug_option.py      # Debug option behavior (3 tests)
│   ├── test_integration.py       # Integration + edge cases (42 tests)
│   ├── conftest.py               # Shared fixtures
│   └── fixtures/                 # Mock API responses
├── .github/workflows/       # CI/CD pipelines (144 tests passing)
│   ├── test.yml            # Automated testing (Python 3.8-3.12)
│   └── lint.yml            # Code quality checks
├── pyproject.toml          # Package configuration
├── README.md               # Main documentation
├── MODEL_SELECTION.md      # Comprehensive model guide
├── TESTING.md              # Testing documentation
├── CHANGELOG.md            # Version history
├── LICENSE                 # Apache 2.0 license
└── .gitignore             # Git ignore rules
```

### Running Tests

This project includes a comprehensive test suite with 144 unit tests covering all major functionality:

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=llm_1min --cov-report=term-missing

# Run specific test file
pytest tests/test_options_config.py -v

# Run specific test
pytest tests/test_options_config.py::TestOptionsConfigSetters::test_set_option_global -v
```

**Test Coverage:**
- ✅ 144/144 tests passing (100%)
- ✅ 55% code coverage
- ✅ Options configuration + legacy-key rejection (28 tests)
- ✅ Model execution + payload shape (18 tests)
- ✅ CLI commands (30 tests)
- ✅ SSE streaming parser (4 tests)
- ✅ Attachments / memory / brand voice (8 tests)
- ✅ Web search config + debug (7 tests)
- ✅ Debug option behavior (3 tests)
- ✅ Integration and edge cases (42 tests)

See [TESTING.md](./TESTING.md) for complete testing documentation.

### Testing the Plugin

1. Install in development mode:
   ```bash
   cd llm-1min
   llm install -e .
   ```

2. Verify installation:
   ```bash
   llm models list | grep 1min
   ```

3. Test with a simple prompt:
   ```bash
   llm -m 1min/gpt-4o-mini "Hello, world!"
   ```

4. Check logs for debugging:
   ```bash
   llm logs -n 1
   ```

### Testing the API Directly

Use the included test script to verify API connectivity:

```bash
export ONEMIN_API_KEY="your-api-key"
python test_api.py
```

## Comparison with Other Providers

### Why Use 1min.ai?

**Advantages:**
- 🎯 **Multi-model access**: One API key for 75+ models across 10 providers
- 💰 **Cost-effective**: Often offers lifetime subscription deals
- 🔄 **Model flexibility**: Switch between OpenAI, Anthropic, Google, xAI, Mistral, Meta, etc.
- 🚀 **Latest models**: Quick access to Claude 4.6, GPT-5.4 / 5.1 Codex, o3 / o4, Gemini 3.1, Qwen3, DeepSeek V3.2, Grok 4, LLaMA 4
- 🌐 **Diverse capabilities**: From fast responses to complex reasoning to web-aware answers

**Use Cases:**
- Comparing responses from different models and providers
- Cost optimization by choosing the right model per task
- Avoiding vendor lock-in with multi-provider access
- Testing different reasoning approaches (O4, DeepSeek R1, Grok 4)
- Accessing models not available through direct APIs (Grok, Sonar)

## Troubleshooting

### "Authentication failed" Error

- Verify your API key is correct: `llm keys set 1min`
- Check that your 1min.ai account is active

### "Rate limit exceeded" Error

- Wait a few moments before retrying
- Check your 1min.ai usage limits

### No Response or Timeout

- Some models (like O3, O1) may take longer for complex reasoning
- Try increasing timeout or using a faster model

### Model Not Found

- Ensure you're using the exact model ID from the Available Models list
- Check 1min.ai documentation for model availability

### Debugging API Requests

To see exactly what's being sent to the API:

```bash
# Use debug option
llm -m 1min/gpt-4o -o debug true "your prompt"

# Or use environment variable
LLM_1MIN_DEBUG=1 llm -m 1min/gpt-4o "your prompt"
```

This will show:
- Options loaded from config files
- Options passed via CLI
- Final merged options
- Complete API payload being sent

Useful for troubleshooting:
- Why web_search isn't working as expected
- Which options are being applied
- Configuration conflicts between global and per-model settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache 2.0

## Related Projects

- [**omi**](https://github.com/gl0bal01/omi) — Standalone Go CLI sharing the same routing and API key. Single static binary, no Python runtime, sub-20ms cold start. Drop-in replacement when you don't need the LLM ecosystem.

## Resources

- [LLM Documentation](https://llm.datasette.io/)
- [1min.ai](https://1min.ai/)
- [Plugin Development Tutorial](https://llm.datasette.io/en/stable/plugins/tutorial-model-plugin.html)

## Credits

Based on the [LLM plugin architecture](https://llm.datasette.io/) by Simon Willison.

Powered by [1min.ai](https://1min.ai) - Multi-model AI API platform.
