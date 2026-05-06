# omi — Go CLI for 1min.ai

**Date:** 2026-05-06  
**Status:** Approved  
**Author:** gl0bal01

## Summary

Standalone Go binary `omi` that wraps the 1min.ai API. Replaces the Python `llm` plugin. Ships as a single static binary — no Python, no venv, no pip.

Goals:
- Single binary distribution
- Fast startup (~5ms vs ~300ms)
- Not tied to Simon Willison's `llm` framework
- Shell autocomplete for models and sessions
- Default model fallback chain
- Minimal friction: `omi "question"` works immediately

---

## Architecture

```
cmd/omi/main.go

internal/
  api/
    client.go        HTTP client, API-KEY auth, timeout, retry
    chat.go          POST /api/chat-with-ai  (SSE streaming)
    vision.go        POST /api/features      CHAT_WITH_IMAGE
    code.go          POST /api/features      CODE_GENERATOR
    assets.go        POST /api/assets        multipart upload
    speech.go        POST /api/features      SPEECH_TO_TEXT
    conversations.go POST /api/conversations create conversation
  config/
    config.go        load/save ~/.config/omi/config.json
  session/
    session.go       load/save ~/.config/omi/sessions.json (name → UUID)
  models/
    registry.go      alias resolution, capability validation
  stream/
    sse.go           SSE event parser (content/result/done/error)
  cmd/
    root.go          default command = chat
    code.go
    transcribe.go
    upload.go
    models.go
    session.go
    config.go
    completion.go    cobra shell completion
```

---

## API Routing

| Command | Endpoint | Type | Streaming |
|---|---|---|---|
| `omi "prompt"` | `POST /api/chat-with-ai` | `UNIFY_CHAT_WITH_AI` | SSE |
| `omi -f img.jpg "..."` | `POST /api/assets` → `POST /api/features` | `CHAT_WITH_IMAGE` | no |
| `omi -f doc.pdf "..."` | `POST /api/assets` → `POST /api/chat-with-ai` | `UNIFY_CHAT_WITH_AI` | SSE |
| `omi code "..."` | `POST /api/features` | `CODE_GENERATOR` | no |
| `omi transcribe f.mp3` | `POST /api/assets` → `POST /api/features` | `SPEECH_TO_TEXT` | no |
| `omi upload f.pdf` | `POST /api/assets` | multipart | no |

Authentication: `API-KEY: <key>` header on all requests.  
Key source: `OMI_API_KEY` env var OR `~/.config/omi/config.json`.

---

## Command Surface

### Chat (root command — no subcommand needed)

```bash
omi "what is Go?"                         # stream, default model
omi -m claude "explain this"              # alias
omi -m claude-sonnet-4-6 "explain this"  # full ID also works
omi -s myproject "continue from before"  # named session
omi -w "latest Go news"                  # web search (--web)
omi -f photo.jpg "describe this"         # vision attachment
omi -f photo.jpg -m qwen-vl "analyze"   # force vision model
omi -f doc.pdf "summarize"              # file attachment
omi -M "prompt"                          # --mix: isMixed=true
omi --no-stream "prompt"                 # wait for full response
omi                                       # REPL loop (empty prompt)
```

Flags:
| Flag | Short | Default | Description |
|---|---|---|---|
| `--model` | `-m` | config or `gpt-4o-mini` | Model alias or full ID |
| `--session` | `-s` | — | Named session (persists conversation) |
| `--web` | `-w` | false | Enable web search |
| `--file` | `-f` | — | Attach file or image (uploads via Asset API) |
| `--mix` | `-M` | false | isMixed=true (cross-model context) |
| `--no-stream` | — | false | Disable SSE streaming |
| `--num-sites` | — | 3 | Sites to search (requires --web) |
| `--max-words` | — | 1000 | Max words per site (requires --web) |

### Code

```bash
omi code "write a Go HTTP client"
omi code -m codex "optimize this algo"
omi code -m r1 "solve this problem"
omi code -s myproject "add error handling"
omi code -M -s shared "continue with claude" -m claude
```

Same flags as chat minus `--web`, `--file`. Default model: `gpt-5.1-codex`.

### Transcribe

```bash
omi transcribe audio.mp3
omi transcribe -l fr meeting.wav
omi transcribe -l en-US interview.m4a
```

Flags:
| Flag | Short | Default | Description |
|---|---|---|---|
| `--lang` | `-l` | auto | Language code (en, fr, de, zh, ...) |

Model hardcoded: `elevenlabs-speech-to-text`. No `-m` flag exposed.  
Flow: upload file via Asset API → get path → call SPEECH_TO_TEXT with path.

### Upload

```bash
omi upload file.pdf
omi upload photo.jpg
```

Prints returned asset `path` to stdout. Use the path in other tools.

### Meta Commands

```bash
omi models                   # all curated models with aliases
omi models chat              # filter: chat capability
omi models code              # filter: code capability
omi models vision            # filter: vision capability

omi session list             # show all named sessions
omi session clear myproject  # delete session UUID (local + API)
omi session clear --all      # clear all sessions

omi config set model claude          # set default chat model
omi config set code-model codex      # set default code model
omi config set web true              # enable web search globally
omi config set mix true              # enable isMixed globally
omi config set api-key <key>         # store API key in config
omi config get model
omi config list

omi completion zsh           # print zsh completion script
omi completion bash
omi completion fish
```

---

## Model Registry

### Capability Types

```go
type Capability uint8
const (
    CapChat   Capability = 1 << iota  // UNIFY_CHAT_WITH_AI
    CapCode                            // CODE_GENERATOR
    CapVision                          // CHAT_WITH_IMAGE (requires -f image)
)
```

### Curated Chat Models (alias → API model ID)

| Alias | API Model ID | Provider |
|---|---|---|
| `mini` *(default)* | `gpt-4o-mini` | OpenAI |
| `gpt4` | `gpt-4o` | OpenAI |
| `gpt5` | `gpt-5` | OpenAI |
| `claude` | `claude-sonnet-4-6` | Anthropic |
| `opus` | `claude-opus-4-6` | Anthropic |
| `haiku` | `claude-haiku-4-5-20251001` | Anthropic |
| `gemini` | `gemini-2.5-pro` | GoogleAI |
| `flash` | `gemini-2.5-flash` | GoogleAI |
| `qwen` | `qwen3-max` | Alibaba |
| `r1` | `deepseek-reasoner` | DeepSeek |
| `deepseek` | `deepseek-chat` | DeepSeek |
| `grok` | `grok-4-0709` | xAI |
| `sonar` | `sonar-pro` | Perplexity |
| `mistral` | `mistral-large-latest` | Mistral |

### Curated Code Models

| Alias | API Model ID | Provider |
|---|---|---|
| `codex` *(default)* | `gpt-5.1-codex` | OpenAI |
| `codex-mini` | `gpt-5.1-codex-mini` | OpenAI |
| `claude` | `claude-sonnet-4-6` | Anthropic |
| `r1` | `deepseek-reasoner` | DeepSeek |
| `qwen-coder` | `qwen3-coder-plus` | Alibaba |
| `grok-code` | `grok-code-fast-1` | xAI |

### Vision-Only Models (only valid with `-f <image>`)

| Alias | API Model ID | Provider |
|---|---|---|
| `qwen-vl` | `qwen3-vl-plus` | Alibaba |
| `qwen-vl-flash` | `qwen3-vl-flash` | Alibaba |

Vision-capable general models (also usable for text chat):  
`gpt4`, `gpt5`, `claude`, `opus`, `haiku`, `gemini`, `flash`, `grok`

### Resolution Logic

1. Try alias lookup in capability-appropriate set
2. If not found as alias, use as raw API model ID (pass-through)
3. If `-f <image>` present, validate model is vision-capable — error if not
4. If `omi code`, validate model is in code set — error if not

---

## Config & Session Storage

### `~/.config/omi/config.json`

```json
{
  "api_key": "optional, prefer OMI_API_KEY env",
  "model": "mini",
  "code_model": "codex",
  "web": false,
  "mix": false,
  "num_sites": 3,
  "max_words": 1000
}
```

### `~/.config/omi/sessions.json`

```json
{
  "myproject": "550e8400-e29b-41d4-a716-446655440000",
  "work": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

One UUID per named session. The `--mix` flag controls `isMixed` in `promptObject` — not a session-level property. This lets the caller decide per-invocation whether to cross-pollinate model context.

---

## isMixed Behavior

When `--mix` / `-M` is set:
- `promptObject.isMixed = true` sent to API
- Same session UUID used (no change to session storage)
- Any model can continue the conversation thread
- The 1min.ai API mixes context across models in that conversation

Example cross-model workflow:
```bash
omi -s research -m claude "analyze this paper"
omi -s research -m gemini --mix "now critique from a different angle"
omi -s research -m r1 --mix "reason through the contradictions"
```

---

## Default Model Fallback Chain

```
-m flag  →  OMI_MODEL env  →  config.json "model"  →  "gpt-4o-mini"
```

For code:
```
-m flag  →  OMI_CODE_MODEL env  →  config.json "code_model"  →  "gpt-5.1-codex"
```

---

## Shell Autocomplete

Generated by cobra: `omi completion zsh|bash|fish|powershell`

Completions registered:
- `-m` / `--model`: all aliases for the current command's capability set
- `-s` / `--session`: existing session names from `sessions.json`
- `omi session clear <TAB>`: session names
- `omi config set <TAB>`: known config keys
- `omi models <TAB>`: `chat`, `code`, `vision`
- `omi completion <TAB>`: `zsh`, `bash`, `fish`, `powershell`

Install (zsh):
```bash
omi completion zsh >> ~/.zshrc && source ~/.zshrc
```

---

## Error UX

Wrong model for capability:
```
$ omi -m sonar -f photo.jpg "describe"
error: model "sonar-pro" does not support vision
vision models: gpt4, gpt5, claude, opus, gemini, flash, grok, qwen-vl
```

```
$ omi code -m sonar "write a func"
error: model "sonar-pro" not in code model set
code models: codex, codex-mini, claude, r1, qwen-coder, grok-code
```

Missing API key:
```
error: no API key found
set via: export OMI_API_KEY=<key>  OR  omi config set api-key <key>
```

API errors surface with status code and message.

---

## Streaming (SSE)

Chat uses `POST /api/chat-with-ai?isStreaming=true`.

SSE events:
| Event | Action |
|---|---|
| `content` | print chunk to stdout |
| `result` | ignore (full record, already printed via chunks) |
| `done` | flush and exit |
| `error` | print to stderr and exit non-zero |

`--no-stream` uses `POST /api/chat-with-ai` (no query param) and prints full `resultObject` on completion.

---

## File Attachment Flow

When `-f <path>` is provided:

1. Detect MIME type from extension
2. Upload via `POST /api/assets` (multipart)
3. Receive `path` from response
4. If image (jpg/png/webp/gif): route to `CHAT_WITH_IMAGE` via `/api/features`, `imageList: [path]`
5. If document (pdf/txt/docx/csv): route to `UNIFY_CHAT_WITH_AI` via `/api/chat-with-ai`, `attachments.files: [path]` — any chat model valid, no capability restriction

---

## REPL Mode

`omi` with no arguments → interactive loop:

```
$ omi
omi> what is Go?
Go is a statically typed, compiled language...
omi> how does it compare to Rust?
...
omi> exit
```

Uses unnamed session (no persistence between REPL runs unless `-s` flag).  
`exit`, `quit`, or Ctrl+C to end.

---

## Out of Scope (v1)

- Image generation
- Video generation  
- Text-to-speech
- Conversation history export
- Multiple file attachments in one call
- YouTube URL analysis
- Brand voice / memories API
