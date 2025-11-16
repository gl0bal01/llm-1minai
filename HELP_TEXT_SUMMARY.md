# Improved Help Text Summary

All `llm 1min` commands now have comprehensive help text with examples.

## Main Command

```bash
$ llm 1min --help
```

```
Usage: llm 1min [OPTIONS] COMMAND [ARGS]...

  Manage 1min.ai conversations and options.

  Use 'llm 1min <command> --help' for detailed information on each command.

  Examples:
    llm 1min models              # List all available models
    llm 1min options list        # View your settings
    llm 1min conversations       # See active conversations

Options:
  -h, --help  Show this message and exit.

Commands:
  clear          Clear conversation history.
  conversations  List active 1min.ai conversations.
  models         List all available 1min.ai models with descriptions.
  options        Manage persistent configuration options.
```

## Options Management

```bash
$ llm 1min options --help
```

```
Usage: llm 1min options [OPTIONS] COMMAND [ARGS]...

  Manage persistent configuration options.

  Configure default behavior for web search, conversation types, and more.
  Settings can be global or per-model.

  Available options:
    - web_search (true/false): Enable web search
    - num_of_site (1-10): Sites to search
    - max_word (number): Max words from search
    - conversation_type (CHAT_WITH_AI/CODE_GENERATOR)
    - is_mixed (true/false): Mix model contexts
    - debug (true/false): Show API request details

  Examples:
    llm 1min options list              # View all settings
    llm 1min options set web_search true
    llm 1min options set --model sonar num_of_site 10

Commands:
  export  Export configuration to JSON file.
  get     Get a specific option value.
  import  Import configuration from JSON file.
  list    Display all configuration options.
  reset   Reset all options to defaults.
  set     Set a configuration option.
  unset   Remove a configuration option.
```

## Individual Commands

### Set Option

```bash
$ llm 1min options set --help
```

Shows:
- Clear explanation of global vs per-model settings
- Important note about using API names (gpt-4o) not LLM IDs (1min/gpt-4o)
- 4 practical examples

### Get Option

```bash
$ llm 1min options get --help
```

Shows:
- How to get global values
- How to get model-specific values

### List Options

```bash
$ llm 1min options list --help
```

Shows:
- View all settings
- Filter by model

### Unset Option

```bash
$ llm 1min options unset --help
```

Shows:
- Remove global settings
- Remove model-specific settings

### Reset

```bash
$ llm 1min options reset --help
```

Shows:
- ⚠️ Warning about removing all configurations
- Confirmation prompt requirement

### Export

```bash
$ llm 1min options export --help
```

Shows:
- Print to screen
- Save to file
- Use shell redirection

### Import

```bash
$ llm 1min options import --help
```

Shows:
- ⚠️ Warning about replacing current config
- Recommendation to backup first

## Models Command

```bash
$ llm 1min models --help
```

Shows:
- Lists 66+ models from 9 providers
- Grep example for filtering

## Conversations Command

```bash
$ llm 1min conversations --help
```

Shows:
- Purpose of tracking conversations
- Context maintenance

## Clear Command

```bash
$ llm 1min clear --help
```

Shows:
- Clear specific model conversation
- Clear all conversations
- Model ID format examples

## Key Improvements

✅ **Every command** has detailed help text
✅ **Examples** for all commands
✅ **Available options** listed in main options help
✅ **Warnings** for destructive operations (reset, import)
✅ **Important notes** (e.g., API names vs LLM IDs)
✅ **Usage patterns** clearly explained
