# How to Select the Right Model

This document is regenerated from `register_models()` whenever the catalog changes. The canonical, runtime-correct list is `llm 1min models`.

**v0.4.0 — 75 models across 10 providers.**

## Quick Lookup

```bash
# Full catalog with [code] / [web] tags
llm 1min models

# LLM-tool IDs only
llm models list | grep '1min.ai'
```

## Tags
- 🚀 = `MODEL_DEFAULTS` sets `conversation_type=CODE_GENERATOR` (CODE_GENERATOR routes to /api/features)
- 🌐 = `MODEL_DEFAULTS` sets `web_search=True`

## OpenAI

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/gpt-3.5-turbo` | `gpt-3.5-turbo` | GPT-3.5 Turbo |
| `1min/gpt-4-turbo` | `gpt-4-turbo` | GPT-4 Turbo |
| `1min/gpt-4.1` | `gpt-4.1` | GPT-4.1 |
| `1min/gpt-4.1-mini` | `gpt-4.1-mini` | GPT-4.1 Mini |
| `1min/gpt-4.1-nano` | `gpt-4.1-nano` | GPT-4.1 Nano |
| `1min/gpt-4o-mini` | `gpt-4o-mini` | GPT-4o Mini |
| `1min/gpt-4o` | `gpt-4o` | GPT-4o |
| `1min/gpt-5` | `gpt-5` | GPT-5 |
| `1min/gpt-5-mini` | `gpt-5-mini` | GPT-5 Mini |
| `1min/gpt-5-nano` | `gpt-5-nano` | GPT-5 Nano |
| `1min/gpt-5-chat-latest` | `gpt-5-chat-latest` | GPT-5 Chat Latest |
| `1min/gpt-5.1` | `gpt-5.1` | GPT-5.1 |
| `1min/gpt-5.1-codex` | `gpt-5.1-codex` | GPT-5.1 Codex 🚀 |
| `1min/gpt-5.1-codex-mini` | `gpt-5.1-codex-mini` | GPT-5.1 Codex Mini 🚀 |
| `1min/gpt-5.2` | `gpt-5.2` | GPT-5.2 |
| `1min/gpt-5.2-pro` | `gpt-5.2-pro` | GPT-5.2 Pro |
| `1min/gpt-5.4` | `gpt-5.4` | GPT-5.4 |
| `1min/gpt-5.4-mini` | `gpt-5.4-mini` | GPT-5.4 Mini |
| `1min/gpt-5.4-nano` | `gpt-5.4-nano` | GPT-5.4 Nano |
| `1min/gpt-5.4-pro` | `gpt-5.4-pro` | GPT-5.4 Pro |
| `1min/o3` | `o3` | o3 |
| `1min/o3-mini` | `o3-mini` | o3 Mini |
| `1min/o3-pro` | `o3-pro` | o3 Pro |
| `1min/o3-deep-research` | `o3-deep-research` | o3 Deep Research 🌐 |
| `1min/o4-mini` | `o4-mini` | o4 Mini |
| `1min/o4-mini-deep-research` | `o4-mini-deep-research` | o4 Mini Deep Research 🌐 |

## Anthropic

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/claude-4-sonnet` | `claude-sonnet-4-20250514` | Claude 4 Sonnet |
| `1min/claude-4-5-sonnet` | `claude-sonnet-4-5-20250929` | Claude 4.5 Sonnet |
| `1min/claude-4-6-sonnet` | `claude-sonnet-4-6` | Claude 4.6 Sonnet 🚀 |
| `1min/claude-4-opus` | `claude-opus-4-20250514` | Claude 4 Opus |
| `1min/claude-4-1-opus` | `claude-opus-4-1-20250805` | Claude 4.1 Opus |
| `1min/claude-4-5-opus` | `claude-opus-4-5-20251101` | Claude 4.5 Opus |
| `1min/claude-4-6-opus` | `claude-opus-4-6` | Claude 4.6 Opus 🚀 |
| `1min/claude-4-5-haiku` | `claude-haiku-4-5-20251001` | Claude 4.5 Haiku 🚀 |

## Google

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/gemini-2.5-flash` | `gemini-2.5-flash` | Gemini 2.5 Flash |
| `1min/gemini-2.5-pro` | `gemini-2.5-pro` | Gemini 2.5 Pro |
| `1min/gemini-3-flash` | `gemini-3-flash-preview` | Gemini 3 Flash (Preview) |
| `1min/gemini-3.1-flash-lite` | `gemini-3.1-flash-lite-preview` | Gemini 3.1 Flash Lite (Preview) |
| `1min/gemini-3.1-pro` | `gemini-3.1-pro-preview` | Gemini 3.1 Pro (Preview) |

## Alibaba (Qwen)

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/qwen-flash` | `qwen-flash` | Qwen Flash |
| `1min/qwen-plus` | `qwen-plus` | Qwen Plus |
| `1min/qwen-max` | `qwen-max` | Qwen Max |
| `1min/qwen-vl-plus` | `qwen-vl-plus` | Qwen VL Plus |
| `1min/qwen-vl-max` | `qwen-vl-max` | Qwen VL Max |
| `1min/qwen3-max` | `qwen3-max` | Qwen3 Max |
| `1min/qwen3-vl-flash` | `qwen3-vl-flash` | Qwen3 VL Flash |
| `1min/qwen3-vl-plus` | `qwen3-vl-plus` | Qwen3 VL Plus |
| `1min/qwen3-coder-plus` | `qwen3-coder-plus` | Qwen3 Coder Plus 🚀 |
| `1min/qwen3-coder-flash` | `qwen3-coder-flash` | Qwen3 Coder Flash 🚀 |

## DeepSeek

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/deepseek-chat` | `deepseek-chat` | DeepSeek V3.2 Chat |
| `1min/deepseek-reasoner` | `deepseek-reasoner` | DeepSeek V3.2 Reasoner 🚀 |

## xAI

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/grok-3` | `grok-3` | Grok 3 |
| `1min/grok-3-mini` | `grok-3-mini` | Grok 3 Mini |
| `1min/grok-4` | `grok-4-0709` | Grok 4 |
| `1min/grok-4-fast-non-reasoning` | `grok-4-fast-non-reasoning` | Grok 4 Fast Non-Reasoning |
| `1min/grok-4-fast-reasoning` | `grok-4-fast-reasoning` | Grok 4 Fast Reasoning |
| `1min/grok-code-fast-1` | `grok-code-fast-1` | Grok Code Fast 1 🚀 |

## Mistral

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/open-mistral-nemo` | `open-mistral-nemo` | Mistral Open Nemo |
| `1min/mistral-small-latest` | `mistral-small-latest` | Mistral Small |
| `1min/mistral-medium-latest` | `mistral-medium-latest` | Mistral Medium 3.1 |
| `1min/mistral-large-latest` | `mistral-large-latest` | Mistral Large 2 |
| `1min/magistral-small-latest` | `magistral-small-latest` | Magistral Small 1.2 |
| `1min/magistral-medium-latest` | `magistral-medium-latest` | Magistral Medium 1.2 |
| `1min/ministral-14b-latest` | `ministral-14b-latest` | Ministral 14B |

## Cohere

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/command-r` | `command-r-08-2024` | Command R |

## Meta / Open Source

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/llama-2-70b` | `meta/llama-2-70b-chat` | LLaMA 2 70b |
| `1min/llama-3-70b` | `meta/meta-llama-3-70b-instruct` | LLaMA 3 70b |
| `1min/llama-4-scout` | `meta/llama-4-scout-instruct` | LLaMA 4 Scout |
| `1min/llama-4-maverick` | `meta/llama-4-maverick-instruct` | LLaMA 4 Maverick |
| `1min/gpt-oss-20b` | `openai/gpt-oss-20b` | GPT OSS 20b |
| `1min/gpt-oss-120b` | `openai/gpt-oss-120b` | GPT OSS 120b |

## Perplexity

| LLM ID | API model | Display name |
|--------|-----------|--------------|
| `1min/sonar` | `sonar` | Perplexity Sonar 🌐 |
| `1min/sonar-pro` | `sonar-pro` | Perplexity Sonar Pro 🌐 |
| `1min/sonar-reasoning-pro` | `sonar-reasoning-pro` | Perplexity Sonar Reasoning Pro 🌐 |
| `1min/sonar-deep-research` | `sonar-deep-research` | Perplexity Sonar Deep Research 🌐 |

## Selection Guide

### Code generation (auto-CODE_GENERATOR)
```bash
llm -m 1min/claude-4-6-sonnet 'Write a FastAPI endpoint'
llm -m 1min/qwen3-coder-plus 'Refactor this Go service'
llm -m 1min/grok-code-fast-1 'Optimize this algorithm'
llm -m 1min/deepseek-reasoner 'Debug this concurrency bug'
```

### Web-aware (auto-`web_search`)
```bash
llm -m 1min/sonar-pro 'Latest AI news with citations'
llm -m 1min/sonar-deep-research 'Multi-source research dive'
llm -m 1min/o3-deep-research 'Reasoning + web grounding'
```

### Cross-conversation memory
```bash
llm -m 1min/gpt-4o -o with_memories true 'Remember I use Postgres'
llm -c 'What database did I mention earlier?'
```

### Image / file attachments (upload first via Asset API)
```bash
llm -m 1min/gpt-4o \
    -o images 'images/2024_09_30_13_41_50_758_photo.png' \
    'Describe this image'

llm -m 1min/claude-4-6-sonnet \
    -o files '20ad0277-74df-4629-8c50-56a2549acbd7' \
    'Summarize this PDF'
```

### Mixed-model conversation history (renamed from is_mixed)
```bash
llm -m 1min/gpt-4o -c 'My name is Fabien'
llm -m 1min/claude-4-6-opus -c -o history_mixed true 'What is my name?'
```

### Streaming
```bash
llm chat --stream -m 1min/gpt-4o 'Explain quantum computing'
```

## Migrating from v0.3.x

If you previously used any of these IDs, switch to the listed replacement. Anything not listed below is unchanged.

| Removed in v0.4.0 | Replacement |
|-------------------|-------------|
| `1min/o1-mini` | `1min/o4-mini` or `1min/o3-mini` |
| `1min/claude-3-haiku` | `1min/claude-4-5-haiku` |
| `1min/claude-3-5-haiku` | `1min/claude-4-5-haiku` |
| `1min/claude-3-7-sonnet` | `1min/claude-4-5-sonnet` or `1min/claude-4-6-sonnet` |
| `1min/gemini-1.5-pro` | `1min/gemini-2.5-pro` or `1min/gemini-3.1-pro` |
| `1min/gemini-2.0-flash` | `1min/gemini-2.5-flash` or `1min/gemini-3-flash` |
| `1min/gemini-2.0-flash-lite` | `1min/gemini-3.1-flash-lite` |
| `1min/grok-2` | `1min/grok-3` or `1min/grok-4` |
| `1min/pixtral-12b` | `1min/qwen-vl-plus` or `1min/gpt-4o` (vision) |
| `1min/llama-3.1-405b` | `1min/llama-4-maverick` |
| `1min/sonar-reasoning` | `1min/sonar-reasoning-pro` |
| `1min/deepseek-r1` (renamed) | `1min/deepseek-reasoner` |

Saved configs that referenced `is_mixed` need a one-time rename:

```bash
llm 1min options migrate    # is_mixed → history_mixed
```

## Tips

- Tab-complete: type `llm -m 1min/` then Tab.
- Inspect built-ins: `llm 1min options defaults`.
- Inspect saved options: `llm 1min options list`.
- See API request payload: `llm -m 1min/<model> -o debug true 'test'` or `LLM_1MIN_DEBUG=1`.
