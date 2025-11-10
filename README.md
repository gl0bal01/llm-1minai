# llm-1min

[![PyPI](https://img.shields.io/pypi/v/llm-1min.svg)](https://pypi.org/project/llm-1min/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/gl0bal01/llm-1min/blob/main/LICENSE)

Plugin for [LLM](https://llm.datasette.io/) adding support for [1min.ai](https://1min.ai) AI models.

Access **66+ AI models** through a single API: GPT-5, GPT-4, Claude 4 Opus, Claude 4 Sonnet, Gemini 2.5, Grok 4, DeepSeek R1, Mistral, LLaMA 4, and more!

## Installation

Install this plugin in the same environment as LLM:

```bash
llm install llm-1min
```

Or install from source for development:

```bash
git clone https://github.com/gl0bal01/llm-1min
cd llm-1min
llm install -e .
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

**66+ models across 9 providers:**

- **OpenAI** (14 models): GPT-3.5 Turbo, GPT-4 Turbo, GPT-4.1, GPT-4o, GPT-5, O1/O3/O4 Mini, and variants
- **Anthropic** (5 models): Claude 3 Haiku, Claude 3.5 Haiku, Claude 3.7 Sonnet, Claude 4 Sonnet, Claude 4 Opus
- **Google** (5 models): Gemini 1.5 Pro, Gemini 2.0 Flash, Gemini 2.5 Flash, Gemini 2.5 Pro
- **xAI** (7 models): Grok 2, Grok 3, Grok 4, Grok Code Fast, and variants
- **DeepSeek** (2 models): DeepSeek Chat, DeepSeek R1
- **Mistral** (4 models): Open Mistral Nemo, Mistral Small, Mistral Large 2, Pixtral 12B
- **Meta/LLaMA** (7 models): LLaMA 2/3/3.1/4, GPT OSS models
- **Cohere** (1 model): Command R
- **Perplexity** (2 models): Sonar, Sonar Reasoning

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
llm -m 1min/deepseek-r1 "Complex math problem"

# Web-aware - Sonar or Sonar Reasoning
llm -m 1min/sonar "What are the latest AI developments?"
llm -m 1min/sonar-reasoning "Research topic with citations"

# Fast responses - Claude 3.5 Haiku or Gemini Flash
llm -m 1min/claude-3-5-haiku "Quick question"
llm -m 1min/gemini-2.5-flash "Fast response needed"
```

### Conversation Mode

Continue a conversation with context:

```bash
# Start a conversation
llm -m 1min/gpt-4o "Hello, I need help with Python"

# Continue the conversation (uses -c flag)
llm -m 1min/gpt-4o -c "What are list comprehensions?"

# Keep going
llm -m 1min/gpt-4o -c "Show me an example"
```

### Code Generation

Use the CODE_GENERATOR conversation type for better code generation:

```bash
llm -m 1min/claude-4-sonnet \
  -o conversation_type CODE_GENERATOR \
  "Create a REST API with FastAPI"
```

### Advanced Options

#### Available Options

- **conversation_type**: `CHAT_WITH_AI` (default) or `CODE_GENERATOR`
- **web_search**: Enable real-time web search (true/false, default: false)
- **num_of_site**: Number of sites to search when web_search is enabled (1-10, default: 3)
- **max_word**: Maximum words from web search results (default: 500)
- **is_mixed**: Mix context between different models (true/false, default: false)

#### One-Time Usage (CLI Flags)

```bash
# Enable web search for any model
llm -m 1min/gpt-4o \
  -o web_search true \
  -o num_of_site 5 \
  "What's the latest in AI?"

# Use code generator mode
llm -m 1min/claude-4-sonnet \
  -o conversation_type CODE_GENERATOR \
  "Write a binary search algorithm"

# Mix context between models
llm -m 1min/gpt-4o -o is_mixed true "Start analysis"
llm -m 1min/claude-4-opus -o is_mixed true "Continue from previous"
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

- ✅ **66+ AI models** from 9 providers through single API
- ✅ **Latest models**: GPT-5, Claude 4 Opus, Gemini 2.5, Grok 4, LLaMA 4
- ✅ **Web search**: Enable real-time web search with any model
- ✅ **Mixed context**: Share conversation context between different models
- ✅ **Persistent options**: Set default preferences globally or per-model
- ✅ Conversation history tracking and management
- ✅ Specialized code generation mode
- ✅ Automatic conversation management
- ✅ List, export, and clear conversations
- ✅ Secure API key management
- ✅ Proper error handling with helpful messages
- ✅ Comprehensive model documentation

## How It Works

This plugin uses the 1min.ai API which provides access to multiple AI models through a unified interface:

1. **Conversation Creation**: When you start a chat, the plugin creates a conversation on 1min.ai
2. **Message Sending**: Your prompts are sent to the `/api/features` endpoint
3. **Context Management**: Conversations are automatically tracked per model
4. **Response Parsing**: The plugin extracts and formats the AI's response

### API Endpoints Used

- `POST https://api.1min.ai/api/conversations` - Create conversation contexts
- `POST https://api.1min.ai/api/features` - Send messages and get responses
- `GET https://api.1min.ai/api/conversations` - List all conversations
- `GET https://api.1min.ai/api/conversations/{uuid}` - Get specific conversation
- `DELETE https://api.1min.ai/api/conversations/{uuid}` - Delete/clear a conversation

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
├── llm_1min.py              # Main plugin implementation (21 KB)
├── manage_conversations.py  # Conversation management utility (6.6 KB)
├── test_api.py              # API testing utility (4.4 KB)
├── pyproject.toml          # Package configuration
├── README.md               # Main documentation
├── MODEL_SELECTION.md      # Comprehensive model guide
├── LICENSE                 # Apache 2.0 license
└── .gitignore             # Git ignore rules
```

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
- 🎯 **Multi-model access**: One API key for 66+ models across 9 providers
- 💰 **Cost-effective**: Often offers lifetime subscription deals
- 🔄 **Model flexibility**: Switch between OpenAI, Anthropic, Google, xAI, Mistral, Meta, etc.
- 🚀 **Latest models**: Quick access to GPT-5, Claude 4 Opus, Gemini 2.5, Grok 4, LLaMA 4
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache 2.0

## Resources

- [LLM Documentation](https://llm.datasette.io/)
- [1min.ai](https://1min.ai/)
- [Plugin Development Tutorial](https://llm.datasette.io/en/stable/plugins/tutorial-model-plugin.html)

## Credits

Based on the [LLM plugin architecture](https://llm.datasette.io/) by Simon Willison.

Powered by [1min.ai](https://1min.ai) - Multi-model AI API platform.
