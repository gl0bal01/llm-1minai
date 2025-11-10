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
- `1min.ai: gpt-4o-mini` → Model ID is **gpt-4o-mini**
- `1min.ai: claude-sonnet-4-20250514` → Model ID is **claude-sonnet-4-20250514**

### Step 2: Use with -m Flag

```bash
llm -m <model-id> "your prompt"
```

### Examples

```bash
# ✅ Correct - Using model ID
llm -m gpt-4o-mini "Hello"
llm -m claude-sonnet-4-20250514 "Write code"
llm -m deepseek-chat "Explain AI"
llm -m grok-4-fast-reasoning "Solve problem"
llm -m gemini-2.5-pro "Analyze document"
llm -m mistral-large-latest "Complex task"
llm -m llama-3.1-405b "Open source inference"

# ❌ Wrong - Using friendly name
llm -m "GPT-4o Mini" "Hello"         # Won't work
llm -m "Claude 4 Sonnet" "Write code" # Won't work
llm -m "Grok 4" "Solve problem"       # Won't work
```

## Complete Model Reference

### OpenAI Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: gpt-3.5-turbo` | `gpt-3.5-turbo` | GPT-3.5 Turbo |
| `1min.ai: gpt-4-turbo` | `gpt-4-turbo` | GPT-4 Turbo |
| `1min.ai: gpt-4.1` | `gpt-4.1` | GPT-4.1 |
| `1min.ai: gpt-4.1-mini` | `gpt-4.1-mini` | GPT-4.1 Mini |
| `1min.ai: gpt-4.1-nano` | `gpt-4.1-nano` | GPT-4.1 Nano |
| `1min.ai: gpt-4o-mini` | `gpt-4o-mini` | GPT-4o Mini |
| `1min.ai: gpt-4o` | `gpt-4o` | GPT-4o |
| `1min.ai: gpt-5` | `gpt-5` | GPT-5 |
| `1min.ai: gpt-5-mini` | `gpt-5-mini` | GPT-5 Mini |
| `1min.ai: gpt-5-nano` | `gpt-5-nano` | GPT-5 Nano |
| `1min.ai: gpt-5-chat-latest` | `gpt-5-chat-latest` | GPT-5 Chat Latest |
| `1min.ai: o1-mini` | `o1-mini` | O1 Mini |
| `1min.ai: o3-mini` | `o3-mini` | O3 Mini |
| `1min.ai: o4-mini` | `o4-mini` | O4 Mini |

### Anthropic Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: claude-3-haiku-20240307` | `claude-3-haiku-20240307` | Claude 3 Haiku |
| `1min.ai: claude-3-5-haiku-20241022` | `claude-3-5-haiku-20241022` | Claude 3.5 Haiku |
| `1min.ai: claude-3-7-sonnet-20250219` | `claude-3-7-sonnet-20250219` | Claude 3.7 Sonnet |
| `1min.ai: claude-sonnet-4-20250514` | `claude-sonnet-4-20250514` | Claude 4 Sonnet |
| `1min.ai: claude-opus-4-20250514` | `claude-opus-4-20250514` | Claude 4 Opus |

### Google Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: gemini-1.5-pro` | `gemini-1.5-pro` | Gemini 1.5 Pro |
| `1min.ai: gemini-2.0-flash` | `gemini-2.0-flash` | Gemini 2.0 Flash |
| `1min.ai: gemini-2.0-flash-lite` | `gemini-2.0-flash-lite` | Gemini 2.0 Flash Lite |
| `1min.ai: gemini-2.5-flash` | `gemini-2.5-flash` | Gemini 2.5 Flash |
| `1min.ai: gemini-2.5-pro` | `gemini-2.5-pro` | Gemini 2.5 Pro |

### DeepSeek Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: deepseek-chat` | `deepseek-chat` | DeepSeek Chat |
| `1min.ai: deepseek-reasoner` | `deepseek-reasoner` | DeepSeek R1 |

### xAI Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: grok-2` | `grok-2` | Grok 2 |
| `1min.ai: grok-3` | `grok-3` | Grok 3 |
| `1min.ai: grok-3-mini` | `grok-3-mini` | Grok 3 Mini |
| `1min.ai: grok-4-0709` | `grok-4-0709` | Grok 4 |
| `1min.ai: grok-4-fast-non-reasoning` | `grok-4-fast-non-reasoning` | Grok 4 Fast Non-Reasoning |
| `1min.ai: grok-4-fast-reasoning` | `grok-4-fast-reasoning` | Grok 4 Fast Reasoning |
| `1min.ai: grok-code-fast-1` | `grok-code-fast-1` | Grok Code Fast 1 |

### Mistral Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: open-mistral-nemo` | `open-mistral-nemo` | Mistral Open Nemo |
| `1min.ai: mistral-small-latest` | `mistral-small-latest` | Mistral Small |
| `1min.ai: mistral-large-latest` | `mistral-large-latest` | Mistral Large 2 |
| `1min.ai: pixtral-12b` | `pixtral-12b` | Mistral Pixtral 12B |

### Cohere Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: command-r-08-2024` | `command-r-08-2024` | Command R |

### Meta/LLaMA Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: meta/llama-2-70b-chat` | `meta/llama-2-70b-chat` | LLaMA 2 70b |
| `1min.ai: meta/meta-llama-3-70b-instruct` | `meta/meta-llama-3-70b-instruct` | LLaMA 3 70b |
| `1min.ai: meta/meta-llama-3.1-405b-instruct` | `meta/meta-llama-3.1-405b-instruct` | LLaMA 3.1 405b |
| `1min.ai: meta/llama-4-scout-instruct` | `meta/llama-4-scout-instruct` | LLaMA 4 Scout |
| `1min.ai: meta/llama-4-maverick-instruct` | `meta/llama-4-maverick-instruct` | LLaMA 4 Maverick |
| `1min.ai: openai/gpt-oss-20b` | `openai/gpt-oss-20b` | GPT OSS 20b |
| `1min.ai: openai/gpt-oss-120b` | `openai/gpt-oss-120b` | GPT OSS 120b |

### Perplexity Models
| What You See in List | Model ID to Use | Friendly Name |
|---------------------|----------------|---------------|
| `1min.ai: sonar` | `sonar` | Sonar |
| `1min.ai: sonar-reasoning` | `sonar-reasoning` | Sonar Reasoning |

## Model Selection Guide

### For General Tasks (Fast & Cheap)
```bash
llm -m gpt-3.5-turbo "Quick question"
llm -m gpt-4o-mini "Fast response"
llm -m deepseek-chat "General chat"
llm -m mistral-small-latest "Efficient processing"
```

### For Coding
```bash
llm -m claude-sonnet-4-20250514 "Write a function"
llm -m grok-code-fast-1 "Generate optimized code"
llm -m deepseek-chat "Debug this code"
llm -m gpt-4o "Complex code analysis"
```

### For Reasoning/Logic
```bash
llm -m o3-mini "Solve logic puzzle"
llm -m o4-mini "Advanced reasoning"
llm -m deepseek-reasoner "Complex math problem"
llm -m grok-4-fast-reasoning "Fast reasoning tasks"
llm -m sonar-reasoning "Research with reasoning"
```

### For Web-Aware Answers
```bash
llm -m sonar "Latest news on AI"
llm -m sonar "Current events"
llm -m sonar-reasoning "Research with citations"
```

### For Complex Tasks
```bash
llm -m gpt-5 "Advanced reasoning and analysis"
llm -m gpt-5-chat-latest "Latest GPT-5 capabilities"
llm -m claude-opus-4-20250514 "Most complex tasks"
llm -m claude-sonnet-4-20250514 "Detailed explanation"
llm -m gemini-2.5-pro "Long document analysis"
llm -m mistral-large-latest "Complex problem solving"
llm -m llama-3.1-405b "Open source large model"
```

### For Fast Responses
```bash
llm -m claude-3-haiku-20240307 "Quick question"
llm -m claude-3-5-haiku-20241022 "Fast Anthropic model"
llm -m gpt-4.1-nano "Ultra-fast responses"
llm -m gpt-5-nano "Fast GPT-5 variant"
llm -m gemini-2.0-flash-lite "Fast Google model"
llm -m grok-3-mini "Fast xAI model"
```

### For Vision Tasks
```bash
llm -m pixtral-12b "Analyze this image"
llm -m gpt-4o "Image and text analysis"
```

### For Open Source Models
```bash
llm -m llama-4-maverick "Latest Meta model"
llm -m llama-3.1-405b "Largest open model"
llm -m open-mistral-nemo "Open Mistral variant"
llm -m command-r "Cohere's retrieval model"
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

## Quick Reference

```bash
# See model IDs
llm models list | grep "1min.ai"

# See model IDs with descriptions
llm 1min models

# Use a model
llm -m <model-id> "your prompt"

# Examples
llm -m gpt-4o-mini "test"
llm -m claude-sonnet-4-20250514 "write code"
llm -m sonar "latest AI news"
```

## Need Help?

```bash
# Show help
llm --help

# Show 1min.ai commands
llm 1min --help

# Show models with descriptions
llm 1min models
```
