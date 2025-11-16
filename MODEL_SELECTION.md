# How to Select the Right Model

## Understanding Model IDs

When you run `llm models list`, you'll see:

```
1min.ai: gpt-4o-mini
1min.ai: claude-sonnet-4-20250514
1min.ai: deepseek-chat
```

**The text after "1min.ai:" is the model ID you use with `-m`**

## Two Ways to View Models

### Method 1: Quick List (Model IDs Only)

```bash
llm models list | grep "1min.ai"
```

**Output:**
```
1min.ai: gpt-4o-mini              ← Copy this ID
1min.ai: gpt-4o                   ← Copy this ID
1min.ai: claude-3-7-sonnet-20250219
...
```

### Method 2: Detailed View (IDs + Descriptions)

```bash
llm 1min models
```

**Output:**
```
Available 1min.ai models:

  gpt-4o-mini                     ← Copy this ID
    Name: GPT-4o Mini
    Description: Fast and cost-effective OpenAI model

  claude-sonnet-4-20250514        ← Copy this ID
    Name: Claude 4 Sonnet
    Description: Latest Anthropic model
```

## How to Use Model IDs

### Step 1: Find the Model ID

```bash
llm models list | grep "1min.ai"
```

Look for the text after "1min.ai:". For example:
- `1min.ai: 1min/gpt-4o-mini` → Model ID is **1min/gpt-4o-mini**
- `1min.ai: 1min/claude-4-sonnet` → Model ID is **1min/claude-4-sonnet**

### Step 2: Use with -m Flag

```bash
llm -m 1min/<model-name> "your prompt"
```

### Examples

```bash
# ✅ Correct - Using full model ID with 1min/ prefix
llm -m 1min/gpt-4o-mini "Hello"
llm -m 1min/claude-4-sonnet "Write code"
llm -m 1min/deepseek-chat "Explain AI"
llm -m 1min/grok-4 "Solve problem"
llm -m 1min/gemini-2.5-pro "Analyze document"
llm -m 1min/sonar "Latest AI news"

# ❌ Wrong - Missing 1min/ prefix
llm -m gpt-4o-mini "Hello"            # Won't work
llm -m claude-4-sonnet "Write code"   # Won't work

# ❌ Wrong - Using friendly name
llm -m "GPT-4o Mini" "Hello"          # Won't work
llm -m "Claude 4 Sonnet" "Write code" # Won't work
```

## Complete Model Reference

### OpenAI Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/gpt-3.5-turbo` | `1min/gpt-3.5-turbo` | GPT-3.5 Turbo |
| `1min.ai: 1min/gpt-4-turbo` | `1min/gpt-4-turbo` | GPT-4 Turbo |
| `1min.ai: 1min/gpt-4.1` | `1min/gpt-4.1` | GPT-4.1 |
| `1min.ai: 1min/gpt-4.1-mini` | `1min/gpt-4.1-mini` | GPT-4.1 Mini |
| `1min.ai: 1min/gpt-4.1-nano` | `1min/gpt-4.1-nano` | GPT-4.1 Nano |
| `1min.ai: 1min/gpt-4o-mini` | `1min/gpt-4o-mini` | GPT-4o Mini |
| `1min.ai: 1min/gpt-4o` | `1min/gpt-4o` | GPT-4o |
| `1min.ai: 1min/gpt-5` | `1min/gpt-5` | GPT-5 |
| `1min.ai: 1min/gpt-5-mini` | `1min/gpt-5-mini` | GPT-5 Mini |
| `1min.ai: 1min/gpt-5-nano` | `1min/gpt-5-nano` | GPT-5 Nano |
| `1min.ai: 1min/gpt-5-chat-latest` | `1min/gpt-5-chat-latest` | GPT-5 Chat Latest |
| `1min.ai: 1min/o1-mini` | `1min/o1-mini` | O1 Mini |
| `1min.ai: 1min/o3-mini` | `1min/o3-mini` | O3 Mini |
| `1min.ai: 1min/o4-mini` | `1min/o4-mini` | O4 Mini |

### Anthropic Models (🚀 = uses CODE_GENERATOR by default)
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/claude-3-haiku` | `1min/claude-3-haiku` | Claude 3 Haiku |
| `1min.ai: 1min/claude-3-5-haiku` | `1min/claude-3-5-haiku` | Claude 3.5 Haiku |
| `1min.ai: 1min/claude-3-7-sonnet` | `1min/claude-3-7-sonnet` | Claude 3.7 Sonnet 🚀 |
| `1min.ai: 1min/claude-4-sonnet` | `1min/claude-4-sonnet` | Claude 4 Sonnet 🚀 |
| `1min.ai: 1min/claude-4-opus` | `1min/claude-4-opus` | Claude 4 Opus |

### Google Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/gemini-1.5-pro` | `1min/gemini-1.5-pro` | Gemini 1.5 Pro |
| `1min.ai: 1min/gemini-2.0-flash` | `1min/gemini-2.0-flash` | Gemini 2.0 Flash |
| `1min.ai: 1min/gemini-2.0-flash-lite` | `1min/gemini-2.0-flash-lite` | Gemini 2.0 Flash Lite |
| `1min.ai: 1min/gemini-2.5-flash` | `1min/gemini-2.5-flash` | Gemini 2.5 Flash |
| `1min.ai: 1min/gemini-2.5-pro` | `1min/gemini-2.5-pro` | Gemini 2.5 Pro |

### DeepSeek Models (🚀 = uses CODE_GENERATOR by default)
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/deepseek-chat` | `1min/deepseek-chat` | DeepSeek Chat |
| `1min.ai: 1min/deepseek-r1` | `1min/deepseek-r1` | DeepSeek R1 🚀 |

### xAI Models (🚀 = uses CODE_GENERATOR by default)
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/grok-2` | `1min/grok-2` | Grok 2 |
| `1min.ai: 1min/grok-3` | `1min/grok-3` | Grok 3 |
| `1min.ai: 1min/grok-3-mini` | `1min/grok-3-mini` | Grok 3 Mini |
| `1min.ai: 1min/grok-4` | `1min/grok-4` | Grok 4 |
| `1min.ai: 1min/grok-4-fast-non-reasoning` | `1min/grok-4-fast-non-reasoning` | Grok 4 Fast Non-Reasoning |
| `1min.ai: 1min/grok-4-fast-reasoning` | `1min/grok-4-fast-reasoning` | Grok 4 Fast Reasoning |
| `1min.ai: 1min/grok-code-fast-1` | `1min/grok-code-fast-1` | Grok Code Fast 1 🚀 |

### Mistral Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/open-mistral-nemo` | `1min/open-mistral-nemo` | Mistral Open Nemo |
| `1min.ai: 1min/mistral-small-latest` | `1min/mistral-small-latest` | Mistral Small |
| `1min.ai: 1min/mistral-large-latest` | `1min/mistral-large-latest` | Mistral Large 2 |
| `1min.ai: 1min/pixtral-12b` | `1min/pixtral-12b` | Mistral Pixtral 12B |

### Cohere Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/command-r` | `1min/command-r` | Command R |

### Meta/LLaMA Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/llama-2-70b` | `1min/llama-2-70b` | LLaMA 2 70b |
| `1min.ai: 1min/llama-3-70b` | `1min/llama-3-70b` | LLaMA 3 70b |
| `1min.ai: 1min/llama-3.1-405b` | `1min/llama-3.1-405b` | LLaMA 3.1 405b |
| `1min.ai: 1min/llama-4-scout` | `1min/llama-4-scout` | LLaMA 4 Scout |
| `1min.ai: 1min/llama-4-maverick` | `1min/llama-4-maverick` | LLaMA 4 Maverick |
| `1min.ai: 1min/gpt-oss-20b` | `1min/gpt-oss-20b` | GPT OSS 20b |
| `1min.ai: 1min/gpt-oss-120b` | `1min/gpt-oss-120b` | GPT OSS 120b |

### Perplexity Models (🌐 = web_search enabled by default)
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: 1min/sonar` | `1min/sonar` | Sonar 🌐 |
| `1min.ai: 1min/sonar-reasoning` | `1min/sonar-reasoning` | Sonar Reasoning 🌐 |
| `1min.ai: 1min/sonar-reasoning-pro` | `1min/sonar-reasoning-pro` | Sonar Reasoning Pro 🌐 |

## Model Selection Guide

### For General Tasks (Fast & Cheap)
```bash
llm -m 1min/gpt-3.5-turbo "Quick question"
llm -m 1min/gpt-4o-mini "Fast response"
llm -m 1min/deepseek-chat "General chat"
llm -m 1min/mistral-small-latest "Efficient processing"
```

### For Coding (🚀 these auto-use CODE_GENERATOR)
```bash
llm -m 1min/claude-4-sonnet "Write a function"  # 🚀 auto CODE_GENERATOR
llm -m 1min/grok-code-fast-1 "Generate optimized code"  # 🚀 auto CODE_GENERATOR
llm -m 1min/deepseek-r1 "Debug this code"  # 🚀 auto CODE_GENERATOR
llm -m 1min/gpt-4o "Complex code analysis"
```

### For Reasoning/Logic
```bash
llm -m 1min/o3-mini "Solve logic puzzle"
llm -m 1min/o4-mini "Advanced reasoning"
llm -m 1min/deepseek-r1 "Complex math problem"
llm -m 1min/grok-4-fast-reasoning "Fast reasoning tasks"
llm -m 1min/sonar-reasoning "Research with reasoning"  # 🌐 auto web_search
```

### For Web-Aware Answers (🌐 these auto-enable web_search)
```bash
llm -m 1min/sonar "Latest news on AI"  # 🌐 auto web_search
llm -m 1min/sonar "Current events"
llm -m 1min/sonar-reasoning "Research with citations"  # 🌐 auto web_search
```

### For Complex Tasks
```bash
llm -m 1min/gpt-5 "Advanced reasoning and analysis"
llm -m 1min/gpt-5-chat-latest "Latest GPT-5 capabilities"
llm -m 1min/claude-4-opus "Most complex tasks"
llm -m 1min/claude-4-sonnet "Detailed explanation"  # 🚀 auto CODE_GENERATOR
llm -m 1min/gemini-2.5-pro "Long document analysis"
llm -m 1min/mistral-large-latest "Complex problem solving"
llm -m 1min/llama-3.1-405b "Open source large model"
```

### For Fast Responses
```bash
llm -m 1min/claude-3-haiku "Quick question"
llm -m 1min/claude-3-5-haiku "Fast Anthropic model"
llm -m 1min/gpt-4.1-nano "Ultra-fast responses"
llm -m 1min/gpt-5-nano "Fast GPT-5 variant"
llm -m 1min/gemini-2.0-flash-lite "Fast Google model"
llm -m 1min/grok-3-mini "Fast xAI model"
```

### For Vision Tasks
```bash
llm -m 1min/pixtral-12b "Analyze this image"
llm -m 1min/gpt-4o "Image and text analysis"
```

### For Open Source Models
```bash
llm -m 1min/llama-4-maverick "Latest Meta model"
llm -m 1min/llama-3.1-405b "Largest open model"
llm -m 1min/open-mistral-nemo "Open Mistral variant"
llm -m 1min/command-r "Cohere's retrieval model"
```

## Advanced Features

### Web Search with Any Model

Enable web search to get real-time information:

```bash
# One-time usage
llm -m 1min/gpt-4o -o web_search true "Latest AI developments"
llm -m 1min/claude-4-opus -o web_search true -o num_of_site 5 "Research topic"

# Set as default
llm 1min options set web_search true
llm 1min options set num_of_site 3

# Now any model uses web search by default
llm -m 1min/gpt-4o "Current events"
```

### Mixed Model Context

Share conversation context between different models:

```bash
# Start with GPT-4o
llm -m 1min/gpt-4o -o is_mixed true "Analyze this architecture design..."

# Continue with Claude (sees GPT's response)
llm -m 1min/claude-4-opus -o is_mixed true "What would you improve?"

# Get third opinion from Gemini
llm -m 1min/gemini-2.5-pro -o is_mixed true "Summarize the discussion"
```

### Per-Model Defaults

Configure specific models with custom settings:

```bash
# GPT-4o always uses web search with 5 sites
llm 1min options set --model gpt-4o web_search true
llm 1min options set --model gpt-4o num_of_site 5

# Sonar uses 10 sites (it's already web-aware)
llm 1min options set --model sonar num_of_site 10

# Claude uses code generator mode by default
llm 1min options set --model claude-4-sonnet conversation_type CODE_GENERATOR
```

## Tips

1. **Use tab completion**: Type `llm -m ` and press Tab to see available models
2. **Bookmark your favorites**: Create aliases in your shell
   ```bash
   alias llm-claude='llm -m 1min/claude-sonnet-4-20250514'
   alias llm-gpt='llm -m 1min/gpt-4o-mini'
   alias llm-web='llm -o web_search true -o num_of_site 5'
   ```
3. **Check the list often**: Run `llm 1min models` to see descriptions
4. **Try different models**: Compare outputs to find what works best
5. **Use persistent options**: Set `llm 1min options set` for frequently used settings

## Common Mistakes

### Mistake 1: Using Friendly Names
```bash
# ❌ Wrong
llm -m "Claude 4 Sonnet" "Hello"
llm -m "GPT-4o Mini" "Hello"

# ✅ Correct
llm -m claude-sonnet-4-20250514 "Hello"
llm -m gpt-4o-mini "Hello"
```

### Mistake 2: Using Spaces in Model IDs
```bash
# ❌ Wrong - spaces break the command
llm -m claude sonnet 4 "Hello"

# ✅ Correct - use the full ID with dashes
llm -m claude-sonnet-4-20250514 "Hello"
```

### Mistake 3: Forgetting Quotes Around Prompt
```bash
# ❌ Wrong - multi-word prompts need quotes
llm -m gpt-4o-mini Hello world

# ✅ Correct
llm -m gpt-4o-mini "Hello world"
```

## Built-in Model Defaults

Some models have optimized default settings:

```bash
# View all built-in defaults
llm 1min options defaults
```

**Code models** (auto-use `CODE_GENERATOR`):
- `1min/claude-4-sonnet`
- `1min/claude-3-7-sonnet`
- `1min/grok-code-fast-1`
- `1min/deepseek-r1`

**Web-aware models** (auto-enable `web_search=true`):
- `1min/sonar`
- `1min/sonar-reasoning`
- `1min/sonar-reasoning-pro`

**Override any default:**
```bash
llm 1min options set --model <api-model-id> <key> <value>
```

## Quick Reference

```bash
# See model IDs
llm models list | grep "1min.ai"

# See model IDs with descriptions
llm 1min models

# View built-in defaults
llm 1min options defaults

# Use a model
llm -m 1min/<model-name> "your prompt"

# Continue conversation
llm -m 1min/gpt-4o "first message"
llm -c "follow up"  # model remembered

# Examples
llm -m 1min/gpt-4o-mini "test"
llm -m 1min/claude-4-sonnet "write code"  # auto CODE_GENERATOR
llm -m 1min/sonar "latest AI news"  # auto web_search
```

## Need Help?

```bash
# Show help
llm --help

# Show 1min.ai commands
llm 1min --help

# Show models with descriptions
llm 1min models

# Show built-in defaults
llm 1min options defaults

# Show all your settings
llm 1min options list
```
