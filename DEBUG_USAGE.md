# How to Use Debug Mode

The `debug` option is available for all 1min.ai models.

## ⚠️ Note: `-d` is taken
The `-d` flag is already used by LLM for `--database`, so we use `-o debug true` instead.

## Usage

### Method 1: CLI Option (Recommended)
```bash
llm -m 1min/gpt-4o -o debug true "your prompt"
```

### Method 2: Environment Variable
```bash
LLM_1MIN_DEBUG=1 llm -m 1min/gpt-4o "your prompt"
```

### Method 3: Set as Default
```bash
# Enable debug globally
llm 1min options set debug true

# Now all requests show debug info
llm -m 1min/gpt-4o "test"

# Disable when done
llm 1min options unset debug
```

## See Available Options

```bash
# List all options for 1min models
llm models --options | grep -A 10 "1min/gpt-4o"
```

Output shows:
```
1min.ai: 1min/gpt-4o
  Options:
    conversation_type: str
    web_search: boolean
    num_of_site: int
    max_word: int
    is_mixed: boolean
    debug: boolean          ← Debug option is visible!
```

## What Debug Shows

When enabled, debug mode displays:
```
======================================================================
[DEBUG] 1min.ai API Request Details
======================================================================
Model: gpt-4o

Options loaded from config:
  Global options: {'web_search': True, 'num_of_site': 3}
  Model-specific options: {'web_search': True, 'num_of_site': 5}

Options from CLI:
  CLI options: {}

Final merged options:
  {'web_search': True, 'num_of_site': 5}
======================================================================

======================================================================
[DEBUG] API Request Payload
======================================================================
Endpoint: https://api.1min.ai/api/features

Payload:
{
  "type": "CHAT_WITH_AI",
  "model": "gpt-4o",
  "conversationId": "...",
  "promptObject": {
    "prompt": "your prompt",
    "webSearch": true,
    "numOfSite": 5,
    "maxWord": 500
  }
}
======================================================================
```

## Shell Alias (Optional Shortcut)

If you want a shorter command, add this to your `~/.bashrc` or `~/.zshrc`:

```bash
# Shortcut for debug mode
alias llm-debug='llm -o debug true'

# Or with a specific model
alias llm-debug-4o='llm -m 1min/gpt-4o -o debug true'
```

Then use:
```bash
llm-debug -m 1min/gpt-4o "test"
# or
llm-debug-4o "test"
```

## Quick Reference

```bash
# See all available options
llm models --options | grep -A 8 "1min/"

# Check current debug setting
llm 1min options get debug

# See all your settings
llm 1min options list
```
