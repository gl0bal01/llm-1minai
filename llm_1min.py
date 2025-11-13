import llm
import requests
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
import os
import json
import click
from pathlib import Path


# Store mapping of LLM conversation IDs to 1min.ai conversation UUIDs
_conversation_mapping = {}


# Configuration management
class OptionsConfig:
    """Manage persistent options configuration"""

    def __init__(self):
        # Try XDG config dir first, fallback to home dir
        config_dir = Path.home() / ".config" / "llm-1min"
        if not config_dir.exists():
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                self.config_path = config_dir / "config.json"
            except:
                # Fallback to home directory
                self.config_path = Path.home() / ".llm-1min.json"
        else:
            self.config_path = config_dir / "config.json"

    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return {"defaults": {}, "models": {}}

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except:
            return {"defaults": {}, "models": {}}

    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save config: {e}")

    def get_defaults(self) -> Dict[str, Any]:
        """Get global default options"""
        config = self.load()
        return config.get("defaults", {})

    def get_model_options(self, model_id: str) -> Dict[str, Any]:
        """Get options for specific model"""
        config = self.load()
        return config.get("models", {}).get(model_id, {})

    def set_option(self, key: str, value: Any, model_id: Optional[str] = None) -> None:
        """Set an option (global or per-model)"""
        config = self.load()

        if model_id:
            if "models" not in config:
                config["models"] = {}
            if model_id not in config["models"]:
                config["models"][model_id] = {}
            config["models"][model_id][key] = value
        else:
            if "defaults" not in config:
                config["defaults"] = {}
            config["defaults"][key] = value

        self.save(config)

    def unset_option(self, key: str, model_id: Optional[str] = None) -> bool:
        """Unset an option. Returns True if something was removed."""
        config = self.load()
        removed = False

        if model_id:
            if model_id in config.get("models", {}):
                if key in config["models"][model_id]:
                    del config["models"][model_id][key]
                    removed = True
                    # Clean up empty model configs
                    if not config["models"][model_id]:
                        del config["models"][model_id]
        else:
            if key in config.get("defaults", {}):
                del config["defaults"][key]
                removed = True

        if removed:
            self.save(config)

        return removed

    def reset(self) -> None:
        """Reset all options to defaults"""
        self.save({"defaults": {}, "models": {}})


# Global config instance
_options_config = OptionsConfig()


# Utility functions for conversation management
def clear_conversation(model_id: str, api_key: str, conversation_uuid: str = None) -> bool:
    """
    Clear a conversation from 1min.ai server.

    Args:
        model_id: The model identifier
        api_key: 1min.ai API key
        conversation_uuid: Optional specific conversation UUID to delete

    Returns:
        True if successful, False otherwise
    """
    if conversation_uuid is None:
        # Find conversation in mapping
        for key, uuid in list(_conversation_mapping.items()):
            if model_id in key:
                conversation_uuid = uuid
                del _conversation_mapping[key]
                break

    if conversation_uuid is None:
        return False

    # Try to delete from API
    # Common patterns: DELETE /api/conversations/{uuid}
    try:
        headers = {"API-KEY": api_key, "Content-Type": "application/json"}

        response = requests.delete(
            f"https://api.1min.ai/api/conversations/{conversation_uuid}",
            headers=headers,
            timeout=30,
        )

        # Success codes: 200, 204, or 404 (already deleted)
        return response.status_code in [200, 204, 404]
    except:
        return False


def clear_all_conversations(api_key: str) -> int:
    """
    Clear all tracked conversations.

    Args:
        api_key: 1min.ai API key

    Returns:
        Number of conversations cleared
    """
    count = 0
    for key, uuid in list(_conversation_mapping.items()):
        try:
            headers = {"API-KEY": api_key, "Content-Type": "application/json"}

            response = requests.delete(
                f"https://api.1min.ai/api/conversations/{uuid}", headers=headers, timeout=30
            )

            if response.status_code in [200, 204, 404]:
                del _conversation_mapping[key]
                count += 1
        except:
            continue

    return count


def get_active_conversations() -> dict:
    """
    Get all active conversation mappings.

    Returns:
        Dictionary of conversation mappings
    """
    return _conversation_mapping.copy()


@llm.hookimpl
def register_models(register):
    """Register 1min.ai models with LLM"""
    # Register with '1min/' prefix to avoid conflicts with other providers
    # The prefix is only for the LLM tool ID, not the actual API model name

    # OpenAI Models
    register(OneMinModel("1min/gpt-3.5-turbo", "gpt-3.5-turbo", "GPT-3.5 Turbo"))
    register(OneMinModel("1min/gpt-4-turbo", "gpt-4-turbo", "GPT-4 Turbo"))
    register(OneMinModel("1min/gpt-4.1", "gpt-4.1", "GPT-4.1"))
    register(OneMinModel("1min/gpt-4.1-mini", "gpt-4.1-mini", "GPT-4.1 Mini"))
    register(OneMinModel("1min/gpt-4.1-nano", "gpt-4.1-nano", "GPT-4.1 Nano"))
    register(OneMinModel("1min/gpt-4o-mini", "gpt-4o-mini", "GPT-4o Mini"))
    register(OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o"))
    register(OneMinModel("1min/gpt-5", "gpt-5", "GPT-5"))
    register(OneMinModel("1min/gpt-5-mini", "gpt-5-mini", "GPT-5 Mini"))
    register(OneMinModel("1min/gpt-5-nano", "gpt-5-nano", "GPT-5 Nano"))
    register(OneMinModel("1min/gpt-5-chat-latest", "gpt-5-chat-latest", "GPT-5 Chat Latest"))
    register(OneMinModel("1min/o3-mini", "o3-mini", "O3 Mini"))
    register(OneMinModel("1min/o4-mini", "o4-mini", "O4 Mini"))
    register(OneMinModel("1min/o1-mini", "o1-mini", "O1 Mini"))

    # Anthropic Models
    register(OneMinModel("1min/claude-3-haiku", "claude-3-haiku-20240307", "Claude 3 Haiku"))
    register(OneMinModel("1min/claude-3-5-haiku", "claude-3-5-haiku-20241022", "Claude 3.5 Haiku"))
    register(
        OneMinModel("1min/claude-3-7-sonnet", "claude-3-7-sonnet-20250219", "Claude 3.7 Sonnet")
    )
    register(OneMinModel("1min/claude-4-sonnet", "claude-sonnet-4-20250514", "Claude 4 Sonnet"))
    register(OneMinModel("1min/claude-4-opus", "claude-opus-4-20250514", "Claude 4 Opus"))

    # Google Models
    register(OneMinModel("1min/gemini-1.5-pro", "gemini-1.5-pro", "Gemini 1.5 Pro"))
    register(OneMinModel("1min/gemini-2.0-flash", "gemini-2.0-flash", "Gemini 2.0 Flash"))
    register(
        OneMinModel("1min/gemini-2.0-flash-lite", "gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite")
    )
    register(OneMinModel("1min/gemini-2.5-flash", "gemini-2.5-flash", "Gemini 2.5 Flash"))
    register(OneMinModel("1min/gemini-2.5-pro", "gemini-2.5-pro", "Gemini 2.5 Pro"))

    # DeepSeek Models
    register(OneMinModel("1min/deepseek-chat", "deepseek-chat", "DeepSeek Chat"))
    register(OneMinModel("1min/deepseek-r1", "deepseek-reasoner", "DeepSeek R1"))

    # xAI Models
    register(OneMinModel("1min/grok-2", "grok-2", "Grok 2"))
    register(OneMinModel("1min/grok-3", "grok-3", "Grok 3"))
    register(OneMinModel("1min/grok-3-mini", "grok-3-mini", "Grok 3 Mini"))
    register(OneMinModel("1min/grok-4", "grok-4-0709", "Grok 4"))
    register(
        OneMinModel(
            "1min/grok-4-fast-non-reasoning",
            "grok-4-fast-non-reasoning",
            "Grok 4 Fast Non-Reasoning",
        )
    )
    register(
        OneMinModel("1min/grok-4-fast-reasoning", "grok-4-fast-reasoning", "Grok 4 Fast Reasoning")
    )
    register(OneMinModel("1min/grok-code-fast-1", "grok-code-fast-1", "Grok Code Fast 1"))

    # Mistral Models
    register(OneMinModel("1min/open-mistral-nemo", "open-mistral-nemo", "Mistral Open Nemo"))
    register(OneMinModel("1min/mistral-small-latest", "mistral-small-latest", "Mistral Small"))
    register(OneMinModel("1min/mistral-large-latest", "mistral-large-latest", "Mistral Large 2"))
    register(OneMinModel("1min/pixtral-12b", "pixtral-12b", "Mistral Pixtral 12B"))

    # Cohere Models
    register(OneMinModel("1min/command-r", "command-r-08-2024", "Command R"))

    # Replicate/Meta Models
    register(OneMinModel("1min/llama-2-70b", "meta/llama-2-70b-chat", "LLaMA 2 70b"))
    register(OneMinModel("1min/llama-3-70b", "meta/meta-llama-3-70b-instruct", "LLaMA 3 70b"))
    register(
        OneMinModel("1min/llama-3.1-405b", "meta/meta-llama-3.1-405b-instruct", "LLaMA 3.1 405b")
    )
    register(OneMinModel("1min/llama-4-scout", "meta/llama-4-scout-instruct", "LLaMA 4 Scout"))
    register(
        OneMinModel("1min/llama-4-maverick", "meta/llama-4-maverick-instruct", "LLaMA 4 Maverick")
    )
    register(OneMinModel("1min/gpt-oss-20b", "openai/gpt-oss-20b", "GPT OSS 20b"))
    register(OneMinModel("1min/gpt-oss-120b", "openai/gpt-oss-120b", "GPT OSS 120b"))

    # Perplexity Models
    register(OneMinModel("1min/sonar-reasoning", "sonar-reasoning", "Sonar Reasoning"))
    register(OneMinModel("1min/sonar", "sonar", "Sonar"))


class OneMinModel(llm.Model):
    """
    LLM plugin for 1min.ai API

    This plugin integrates 1min.ai's conversational AI capabilities into LLM.
    Set your API key with: llm keys set 1min

    Available models:
    - OpenAI: gpt-3.5-turbo, gpt-4-turbo, gpt-4.1, gpt-4o, gpt-5, o1-mini, o3-mini, o4-mini
    - Anthropic: claude-3-haiku, claude-3-5-haiku, claude-3-7-sonnet, claude-4-sonnet, claude-4-opus
    - Google: gemini-1.5-pro, gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro
    - DeepSeek: deepseek-chat, deepseek-reasoner
    - xAI: grok-2, grok-3, grok-4, grok-code-fast-1
    - Mistral: open-mistral-nemo, mistral-small-latest, mistral-large-latest, pixtral-12b
    - Cohere: command-r
    - Meta: llama-2-70b, llama-3-70b, llama-3.1-405b, llama-4-scout, llama-4-maverick
    - Perplexity: sonar, sonar-reasoning
    """

    needs_key = "1min"
    key_env_var = "ONEMIN_API_KEY"
    can_stream = False  # 1min.ai API doesn't appear to support streaming based on the code

    class Options(llm.Options):
        conversation_type: Optional[str] = Field(
            description="Type of conversation: CHAT_WITH_AI or CODE_GENERATOR",
            default="CHAT_WITH_AI",
        )

        # Web search options
        web_search: Optional[bool] = Field(
            description="Enable web search for real-time information", default=False
        )
        num_of_site: Optional[int] = Field(
            description="Number of sites to search when web_search is enabled (1-10)", default=3
        )
        max_word: Optional[int] = Field(
            description="Maximum words to extract from web search results", default=500
        )

        # Mixed model context
        is_mixed: Optional[bool] = Field(
            description="Mix context between different models in conversation", default=False
        )

        @field_validator("conversation_type")
        def validate_conversation_type(cls, conv_type):
            if conv_type not in ["CHAT_WITH_AI", "CODE_GENERATOR"]:
                raise ValueError("conversation_type must be CHAT_WITH_AI or CODE_GENERATOR")
            return conv_type

        @field_validator("num_of_site")
        def validate_num_of_site(cls, value):
            if value < 1 or value > 10:
                raise ValueError("num_of_site must be between 1 and 10")
            return value

    def __init__(self, llm_model_id, api_model_id, display_name=None):
        """
        Initialize the model.

        Args:
            llm_model_id: ID used in LLM tool (e.g., "1min/gpt-4o-mini")
            api_model_id: ID used in 1min.ai API (e.g., "gpt-4o-mini")
            display_name: Human-readable name (e.g., "GPT-4o Mini")
        """
        self.model_id = llm_model_id  # LLM tool uses this
        self.api_model_id = api_model_id  # 1min.ai API uses this
        self.display_name = display_name or api_model_id

    def __str__(self):
        # Show model_id (what users need to use with -m flag)
        return f"1min.ai: {self.model_id}"

    def get_or_create_conversation(self, key, conversation, prompt):
        """
        Get existing 1min.ai conversation UUID or create a new one.

        Args:
            key: API key
            conversation: LLM conversation object (may be None)
            prompt: LLM prompt object

        Returns:
            1min.ai conversation UUID
        """
        # Generate a unique key for this conversation
        conv_key = f"{self.model_id}"
        if conversation and hasattr(conversation, "id"):
            conv_key = f"{conversation.id}_{self.model_id}"

        # Check if we already have a 1min.ai conversation for this
        if conv_key in _conversation_mapping:
            return _conversation_mapping[conv_key]

        # Create a new 1min.ai conversation
        conversation_type = prompt.options.conversation_type or "CHAT_WITH_AI"

        headers = {"API-KEY": key, "Content-Type": "application/json"}

        payload = {
            "title": f"LLM Chat - {self.display_name}",
            "type": conversation_type,
            "model": self.api_model_id,  # Use actual API model ID, not LLM ID
        }

        try:
            response = requests.post(
                "https://api.1min.ai/api/conversations", headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            conversation_uuid = response.json()["conversation"]["uuid"]
            _conversation_mapping[conv_key] = conversation_uuid

            return conversation_uuid

        except requests.exceptions.RequestException as e:
            raise llm.ModelError(f"Failed to create conversation: {str(e)}")

    def execute(self, prompt, stream, response, conversation):
        """Execute a prompt against the 1min.ai API"""
        # Get API key
        key = self.get_key()

        # Load options from config (global + per-model)
        global_options = _options_config.get_defaults()
        model_options = _options_config.get_model_options(self.api_model_id)

        # Merge options: global < model-specific < CLI
        merged_options = {**global_options, **model_options}

        # CLI options override everything (only if explicitly set)
        cli_options = {}
        if prompt.options.conversation_type != "CHAT_WITH_AI":  # If not default
            cli_options["conversation_type"] = prompt.options.conversation_type
        if prompt.options.web_search is not False:  # If not default
            cli_options["web_search"] = prompt.options.web_search
        if prompt.options.num_of_site != 3:  # If not default
            cli_options["num_of_site"] = prompt.options.num_of_site
        if prompt.options.max_word != 500:  # If not default
            cli_options["max_word"] = prompt.options.max_word
        if prompt.options.is_mixed is not False:  # If not default
            cli_options["is_mixed"] = prompt.options.is_mixed

        # Apply CLI overrides
        merged_options.update(cli_options)

        # Get or create 1min.ai conversation
        conversation_uuid = self.get_or_create_conversation(key, conversation, prompt)

        # Determine conversation type
        conversation_type = merged_options.get(
            "conversation_type", prompt.options.conversation_type
        )

        # Build promptObject with all options
        prompt_object = {"prompt": prompt.prompt}

        # Add optional parameters if enabled
        if merged_options.get("web_search", False):
            prompt_object["webSearch"] = True
            prompt_object["numOfSite"] = merged_options.get("num_of_site", 3)
            prompt_object["maxWord"] = merged_options.get("max_word", 500)

        if merged_options.get("is_mixed", False):
            prompt_object["isMixed"] = True

        # Build request payload for 1min.ai /api/features endpoint
        headers = {"API-KEY": key, "Content-Type": "application/json"}

        payload = {
            "type": conversation_type,
            "model": self.api_model_id,  # Use actual API model ID, not LLM ID
            "conversationId": conversation_uuid,
            "promptObject": prompt_object,
        }

        # Make the API request
        try:
            api_response = requests.post(
                "https://api.1min.ai/api/features",
                headers=headers,
                json=payload,
                timeout=60,  # Longer timeout for AI responses
            )
            api_response.raise_for_status()

            # Parse response - based on actual Discord bot implementation
            result_data = api_response.json()

            # Try to extract the result from the response
            result_object = None

            if result_data.get("aiRecord", {}).get("aiRecordDetail", {}).get("resultObject"):
                result_object = result_data["aiRecord"]["aiRecordDetail"]["resultObject"]
            elif result_data.get("result", {}).get("response"):
                result_object = result_data["result"]["response"]
            elif "data" in result_data:
                result_object = result_data["data"]
            else:
                # Fallback: stringify the whole response
                result_object = result_data

            # Convert to readable string
            if isinstance(result_object, list):
                result_text = "\n".join(str(item) for item in result_object)
            elif isinstance(result_object, dict):
                result_text = json.dumps(result_object, indent=2)
            else:
                result_text = str(result_object)

            yield result_text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise llm.ModelError("Authentication failed. Please check your API key.")
            elif e.response.status_code == 429:
                raise llm.ModelError("Rate limit exceeded. Please try again later.")
            else:
                raise llm.ModelError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise llm.ModelError(f"API request failed: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise llm.ModelError(f"Failed to parse API response: {str(e)}")


@llm.hookimpl
def register_commands(cli):
    """Register CLI commands for conversation management"""

    @cli.group(name="1min")
    def onemin_group():
        """Manage 1min.ai conversations"""
        pass

    @onemin_group.command(name="models")
    def list_models():
        """List available 1min.ai models"""
        models = [
            # OpenAI Models
            ("1min/gpt-3.5-turbo", "GPT-3.5 Turbo", "Fast and economical OpenAI model"),
            ("1min/gpt-4-turbo", "GPT-4 Turbo", "Enhanced GPT-4 with speed improvements"),
            ("1min/gpt-4.1", "GPT-4.1", "Latest GPT-4 series model"),
            ("1min/gpt-4.1-mini", "GPT-4.1 Mini", "Compact GPT-4.1 variant"),
            ("1min/gpt-4.1-nano", "GPT-4.1 Nano", "Ultra-compact GPT-4.1 variant"),
            ("1min/gpt-4o-mini", "GPT-4o Mini", "Fast and cost-effective OpenAI model"),
            ("1min/gpt-4o", "GPT-4o", "Omni-modal GPT-4 model"),
            ("1min/gpt-5", "GPT-5", "Latest OpenAI flagship model"),
            ("1min/gpt-5-mini", "GPT-5 Mini", "Compact GPT-5 variant"),
            ("1min/gpt-5-nano", "GPT-5 Nano", "Ultra-compact GPT-5 variant"),
            ("1min/gpt-5-chat-latest", "GPT-5 Chat Latest", "Latest GPT-5 chat variant"),
            ("1min/o1-mini", "O1 Mini", "OpenAI reasoning model"),
            ("1min/o3-mini", "O3 Mini", "Reasoning-focused OpenAI model"),
            ("1min/o4-mini", "O4 Mini", "Latest reasoning-focused model"),
            # Anthropic Models
            ("1min/claude-3-haiku", "Claude 3 Haiku", "Fast and compact Anthropic model"),
            ("1min/claude-3-5-haiku", "Claude 3.5 Haiku", "Enhanced fast Anthropic model"),
            ("1min/claude-3-7-sonnet", "Claude 3.7 Sonnet", "Advanced Anthropic model"),
            ("1min/claude-4-sonnet", "Claude 4 Sonnet", "Latest Anthropic Sonnet model"),
            ("1min/claude-4-opus", "Claude 4 Opus", "Most powerful Anthropic model"),
            # Google Models
            ("1min/gemini-1.5-pro", "Gemini 1.5 Pro", "Google's advanced model"),
            ("1min/gemini-2.0-flash", "Gemini 2.0 Flash", "Fast Gemini 2.0 variant"),
            ("1min/gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite", "Compact Gemini 2.0 Flash"),
            ("1min/gemini-2.5-flash", "Gemini 2.5 Flash", "Latest fast Gemini model"),
            ("1min/gemini-2.5-pro", "Gemini 2.5 Pro", "Latest Gemini Pro model"),
            # DeepSeek Models
            ("1min/deepseek-chat", "DeepSeek Chat", "DeepSeek conversational model"),
            ("1min/deepseek-r1", "DeepSeek R1", "DeepSeek reasoning model"),
            # xAI Models
            ("1min/grok-2", "Grok 2", "xAI's Grok model"),
            ("1min/grok-3", "Grok 3", "Latest xAI Grok model"),
            ("1min/grok-3-mini", "Grok 3 Mini", "Compact Grok 3 variant"),
            ("1min/grok-4", "Grok 4", "Newest xAI Grok model"),
            (
                "1min/grok-4-fast-non-reasoning",
                "Grok 4 Fast Non-Reasoning",
                "Fast Grok 4 without reasoning",
            ),
            ("1min/grok-4-fast-reasoning", "Grok 4 Fast Reasoning", "Fast Grok 4 with reasoning"),
            ("1min/grok-code-fast-1", "Grok Code Fast 1", "xAI's fast code generation model"),
            # Mistral Models
            ("1min/open-mistral-nemo", "Mistral Open Nemo", "Open Mistral model"),
            ("1min/mistral-small-latest", "Mistral Small", "Compact Mistral model"),
            ("1min/mistral-large-latest", "Mistral Large 2", "Most capable Mistral model"),
            ("1min/pixtral-12b", "Mistral Pixtral 12B", "Mistral vision model"),
            # Cohere Models
            ("1min/command-r", "Command R", "Cohere's Command R model"),
            # Meta/LLaMA Models
            ("1min/llama-2-70b", "LLaMA 2 70b", "Meta's LLaMA 2 70B model"),
            ("1min/llama-3-70b", "LLaMA 3 70b", "Meta's LLaMA 3 70B model"),
            ("1min/llama-3.1-405b", "LLaMA 3.1 405b", "Meta's largest LLaMA model"),
            ("1min/llama-4-scout", "LLaMA 4 Scout", "LLaMA 4 Scout variant"),
            ("1min/llama-4-maverick", "LLaMA 4 Maverick", "LLaMA 4 Maverick variant"),
            ("1min/gpt-oss-20b", "GPT OSS 20b", "Open-source GPT 20B model"),
            ("1min/gpt-oss-120b", "GPT OSS 120b", "Open-source GPT 120B model"),
            # Perplexity Models
            ("1min/sonar", "Sonar", "Perplexity web-aware model"),
            ("1min/sonar-reasoning", "Sonar Reasoning", "Perplexity with reasoning capabilities"),
        ]

        click.echo("Available 1min.ai models:\n")
        for model_id, name, description in models:
            click.echo(f"  {click.style(model_id, fg='cyan', bold=True)}")
            click.echo(f"    Name: {name}")
            click.echo(f"    Description: {description}")
            click.echo()

        click.echo("Usage:")
        click.echo('  llm -m <model-id> "your prompt"')
        click.echo("\nExample:")
        click.echo('  llm -m 1min/gpt-4o-mini "Explain Python decorators"')

    @onemin_group.command(name="conversations")
    def list_conversations():
        """List active 1min.ai conversations"""
        conversations = get_active_conversations()

        if not conversations:
            click.echo("No active conversations")
            return

        click.echo(f"Active conversations: {len(conversations)}\n")
        for key, uuid in conversations.items():
            click.echo(f"  {key}: {uuid}")

    @onemin_group.command(name="clear")
    @click.option("--model", "-m", help="Model ID to clear conversation for")
    @click.option("--all", "clear_all", is_flag=True, help="Clear all conversations")
    def clear_conversations_cmd(model, clear_all):
        """Clear 1min.ai conversation(s)"""
        # Get API key from environment or LLM's key storage
        api_key = os.environ.get("ONEMIN_API_KEY")

        if not api_key:
            # Try to get from LLM's key storage
            try:
                # This is a bit hacky but works
                temp_model = OneMinModel("1min/gpt-4o-mini", "gpt-4o-mini", "GPT-4o Mini")
                api_key = temp_model.get_key()
            except:
                click.echo(
                    "Error: No API key found. Set ONEMIN_API_KEY or use 'llm keys set 1min'",
                    err=True,
                )
                return

        if clear_all:
            count = clear_all_conversations(api_key)
            click.echo(f"Cleared {count} conversation(s)")
        elif model:
            success = clear_conversation(model, api_key)
            if success:
                click.echo(f"Cleared conversation for {model}")
            else:
                click.echo(f"No conversation found for {model}", err=True)
        else:
            click.echo("Error: Specify --model or --all", err=True)

    @onemin_group.group(name="options")
    def options_group():
        """Manage persistent options for 1min.ai models"""
        pass

    @options_group.command(name="set")
    @click.argument("key")
    @click.argument("value")
    @click.option(
        "--model", "-m", help="Set option for specific model (e.g., gpt-4o, claude-4-sonnet)"
    )
    def set_option(key, value, model):
        """Set an option (global or per-model)

        Examples:
          llm 1min options set web_search true
          llm 1min options set --model gpt-4o web_search true
          llm 1min options set num_of_site 5
        """
        # Convert string value to appropriate type
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)

        try:
            _options_config.set_option(key, value, model)
            if model:
                click.echo(f"Set {key}={value} for model '{model}'")
            else:
                click.echo(f"Set {key}={value} globally")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="get")
    @click.argument("key")
    @click.option("--model", "-m", help="Get option for specific model")
    def get_option(key, model):
        """Get an option value

        Examples:
          llm 1min options get web_search
          llm 1min options get --model gpt-4o web_search
        """
        try:
            if model:
                options = _options_config.get_model_options(model)
                if key in options:
                    click.echo(f"{key}={options[key]}")
                else:
                    click.echo(f"{key} not set for model '{model}'")
            else:
                options = _options_config.get_defaults()
                if key in options:
                    click.echo(f"{key}={options[key]}")
                else:
                    click.echo(f"{key} not set globally")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="list")
    @click.option("--model", "-m", help="List options for specific model")
    def list_options(model):
        """List all options

        Examples:
          llm 1min options list
          llm 1min options list --model gpt-4o
        """
        try:
            if model:
                options = _options_config.get_model_options(model)
                if options:
                    click.echo(f"Options for model '{model}':\n")
                    for key, value in options.items():
                        click.echo(f"  {key} = {value}")
                else:
                    click.echo(f"No options set for model '{model}'")
            else:
                config = _options_config.load()

                # Show global defaults
                defaults = config.get("defaults", {})
                if defaults:
                    click.echo("Global defaults:\n")
                    for key, value in defaults.items():
                        click.echo(f"  {key} = {value}")
                else:
                    click.echo("No global defaults set")

                # Show per-model options
                models = config.get("models", {})
                if models:
                    click.echo("\nPer-model options:\n")
                    for model_id, opts in models.items():
                        click.echo(f"  {model_id}:")
                        for key, value in opts.items():
                            click.echo(f"    {key} = {value}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="unset")
    @click.argument("key")
    @click.option("--model", "-m", help="Unset option for specific model")
    def unset_option(key, model):
        """Remove an option

        Examples:
          llm 1min options unset web_search
          llm 1min options unset --model gpt-4o web_search
        """
        try:
            removed = _options_config.unset_option(key, model)
            if removed:
                if model:
                    click.echo(f"Removed {key} for model '{model}'")
                else:
                    click.echo(f"Removed {key} globally")
            else:
                if model:
                    click.echo(f"{key} was not set for model '{model}'")
                else:
                    click.echo(f"{key} was not set globally")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="reset")
    @click.confirmation_option(prompt="Are you sure you want to reset all options?")
    def reset_options():
        """Reset all options to defaults

        This will remove all global and per-model options.
        """
        try:
            _options_config.reset()
            click.echo("All options reset to defaults")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="export")
    @click.option("--output", "-o", help="Output file (default: stdout)")
    def export_options(output):
        """Export options configuration to JSON

        Examples:
          llm 1min options export
          llm 1min options export --output my-config.json
        """
        try:
            config = _options_config.load()
            json_str = json.dumps(config, indent=2)

            if output:
                with open(output, "w") as f:
                    f.write(json_str)
                click.echo(f"Exported options to {output}")
            else:
                click.echo(json_str)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="import")
    @click.argument("file", type=click.Path(exists=True))
    def import_options(file):
        """Import options configuration from JSON file

        Example:
          llm 1min options import my-config.json
        """
        try:
            with open(file, "r") as f:
                config = json.load(f)

            # Validate structure
            if not isinstance(config, dict):
                raise ValueError("Config must be a JSON object")

            _options_config.save(config)
            click.echo(f"Imported options from {file}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
