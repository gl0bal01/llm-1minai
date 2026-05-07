import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import click
import llm
import requests
from pydantic import Field, field_validator

# Store mapping of LLM conversation IDs to 1min.ai conversation UUIDs
_conversation_mapping = {}
_conversation_file = None

# Model-specific defaults — code-focused models use CODE_GENERATOR by default,
# web-aware models default to web_search=True.
MODEL_DEFAULTS = {
    # CODE_GENERATOR-eligible (per /api/features Code Generator spec)
    "qwen3-coder-plus": {"conversation_type": "CODE_GENERATOR"},
    "qwen3-coder-flash": {"conversation_type": "CODE_GENERATOR"},
    "claude-sonnet-4-6": {"conversation_type": "CODE_GENERATOR"},
    "claude-opus-4-6": {"conversation_type": "CODE_GENERATOR"},
    "claude-haiku-4-5-20251001": {"conversation_type": "CODE_GENERATOR"},
    "deepseek-reasoner": {"conversation_type": "CODE_GENERATOR"},
    "gpt-5.1-codex": {"conversation_type": "CODE_GENERATOR"},
    "gpt-5.1-codex-mini": {"conversation_type": "CODE_GENERATOR"},
    "grok-code-fast-1": {"conversation_type": "CODE_GENERATOR"},
    # Web-aware: enable web_search by default
    "sonar": {"web_search": True, "num_of_site": 5},
    "sonar-pro": {"web_search": True, "num_of_site": 5},
    "sonar-reasoning-pro": {"web_search": True, "num_of_site": 5},
    "sonar-deep-research": {"web_search": True, "num_of_site": 10},
    "o3-deep-research": {"web_search": True, "num_of_site": 5},
    "o4-mini-deep-research": {"web_search": True, "num_of_site": 5},
}


def _warn(message: str) -> None:
    """Emit warning messages to stderr."""
    print(f"[llm-1min] Warning: {message}", file=sys.stderr)


def _get_conversation_file():
    """Get the path to the persistent conversation mapping file."""
    global _conversation_file
    if _conversation_file is None:
        config_dir = Path.home() / ".config" / "llm-1min"
        config_dir.mkdir(parents=True, exist_ok=True)
        _conversation_file = config_dir / "conversations.json"
    return _conversation_file


def _load_conversations():
    """Load conversation mappings from disk."""
    global _conversation_mapping
    conv_file = _get_conversation_file()
    if conv_file.exists():
        try:
            with open(conv_file, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                _conversation_mapping = {str(k): str(v) for k, v in loaded.items()}
            else:
                _warn(
                    f"Ignoring invalid conversation mapping format in {conv_file}: "
                    f"expected JSON object."
                )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as e:
            _warn(f"Could not load conversation mapping from {conv_file}: {e}")


def _save_conversations():
    """Save conversation mappings to disk."""
    conv_file = _get_conversation_file()
    tmp_file_path = None
    try:
        conv_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_file_path = tempfile.mkstemp(
            prefix="conversations.",
            suffix=".json.tmp",
            dir=str(conv_file.parent),
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(_conversation_mapping, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_file_path, 0o600)
        os.replace(tmp_file_path, conv_file)
        os.chmod(conv_file, 0o600)
    except (OSError, TypeError, ValueError) as e:
        _warn(f"Failed to persist conversation mapping to {conv_file}: {e}")
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except OSError:
                pass


# Load existing conversations on module import
_load_conversations()


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
            except OSError:
                # Fallback to home directory
                self.config_path = Path.home() / ".llm-1min.json"
        else:
            self.config_path = config_dir / "config.json"

    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return {"defaults": {}, "models": {}}

        try:
            with open(self.config_path) as f:
                config = json.load(f)
        except Exception:
            return {"defaults": {}, "models": {}}

        self._check_legacy_keys(config)
        return config

    @staticmethod
    def _check_legacy_keys(config: Dict[str, Any]) -> None:
        """Raise on saved config keys removed in v0.4.0."""
        legacy_renames = {"is_mixed": "history_mixed"}

        def scan(scope_name: str, options: Dict[str, Any]) -> None:
            for old, new in legacy_renames.items():
                if old in options:
                    raise ValueError(
                        f"Saved config option '{old}' (in {scope_name}) was renamed "
                        f"to '{new}' in v0.4.0. Run: "
                        f"`llm 1min options migrate` to auto-rename, or "
                        f"`llm 1min options unset {old}` and "
                        f"`llm 1min options set {new} <value>` manually."
                    )

        defaults = config.get("defaults") or {}
        if isinstance(defaults, dict):
            scan("defaults", defaults)

        models = config.get("models") or {}
        if isinstance(models, dict):
            for model_id, opts in models.items():
                if isinstance(opts, dict):
                    scan(f"models.{model_id}", opts)

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
        # Find exact mapping matches for this model only:
        # - model-only key: "1min/gpt-4o"
        # - conversation-scoped key: "{conversation_id}_1min/gpt-4o"
        for key, uuid in list(_conversation_mapping.items()):
            if key == model_id or key.endswith(f"_{model_id}"):
                conversation_uuid = uuid
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
        success = response.status_code in [200, 204, 404]
        if success:
            # Remove every local key pointing to this UUID.
            # A single UUID can be referenced by multiple keys when history_mixed is enabled.
            removed = False
            for key, uuid in list(_conversation_mapping.items()):
                if uuid == conversation_uuid:
                    del _conversation_mapping[key]
                    removed = True
            if removed:
                _save_conversations()
        return success
    except requests.RequestException:
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
    any_removed = False
    uuids = list(dict.fromkeys(_conversation_mapping.values()))
    for uuid in uuids:
        try:
            headers = {"API-KEY": api_key, "Content-Type": "application/json"}

            response = requests.delete(
                f"https://api.1min.ai/api/conversations/{uuid}", headers=headers, timeout=30
            )

            if response.status_code in [200, 204, 404]:
                for key, mapped_uuid in list(_conversation_mapping.items()):
                    if mapped_uuid == uuid:
                        del _conversation_mapping[key]
                        any_removed = True
                count += 1
        except requests.RequestException:
            continue

    if any_removed:
        _save_conversations()  # Persist the deletions

    return count


def get_active_conversations() -> dict:
    """
    Get all active conversation mappings.

    Returns:
        Dictionary of conversation mappings
    """
    _load_conversations()  # Reload from disk to get latest
    return _conversation_mapping.copy()


@llm.hookimpl
def register_models(register):
    """Register 1min.ai models with LLM (catalog refreshed for 1min.ai API v2)."""

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
    register(OneMinModel("1min/gpt-5.1", "gpt-5.1", "GPT-5.1"))
    register(OneMinModel("1min/gpt-5.1-codex", "gpt-5.1-codex", "GPT-5.1 Codex"))
    register(OneMinModel("1min/gpt-5.1-codex-mini", "gpt-5.1-codex-mini", "GPT-5.1 Codex Mini"))
    register(OneMinModel("1min/gpt-5.2", "gpt-5.2", "GPT-5.2"))
    register(OneMinModel("1min/gpt-5.2-pro", "gpt-5.2-pro", "GPT-5.2 Pro"))
    register(OneMinModel("1min/gpt-5.4", "gpt-5.4", "GPT-5.4"))
    register(OneMinModel("1min/gpt-5.4-mini", "gpt-5.4-mini", "GPT-5.4 Mini"))
    register(OneMinModel("1min/gpt-5.4-nano", "gpt-5.4-nano", "GPT-5.4 Nano"))
    register(OneMinModel("1min/gpt-5.4-pro", "gpt-5.4-pro", "GPT-5.4 Pro"))
    register(OneMinModel("1min/o3", "o3", "o3"))
    register(OneMinModel("1min/o3-mini", "o3-mini", "o3 Mini"))
    register(OneMinModel("1min/o3-pro", "o3-pro", "o3 Pro"))
    register(OneMinModel("1min/o3-deep-research", "o3-deep-research", "o3 Deep Research"))
    register(OneMinModel("1min/o4-mini", "o4-mini", "o4 Mini"))
    register(
        OneMinModel("1min/o4-mini-deep-research", "o4-mini-deep-research", "o4 Mini Deep Research")
    )

    # Anthropic Models
    register(OneMinModel("1min/claude-4-sonnet", "claude-sonnet-4-20250514", "Claude 4 Sonnet"))
    register(
        OneMinModel("1min/claude-4-5-sonnet", "claude-sonnet-4-5-20250929", "Claude 4.5 Sonnet")
    )
    register(OneMinModel("1min/claude-4-6-sonnet", "claude-sonnet-4-6", "Claude 4.6 Sonnet"))
    register(OneMinModel("1min/claude-4-opus", "claude-opus-4-20250514", "Claude 4 Opus"))
    register(OneMinModel("1min/claude-4-1-opus", "claude-opus-4-1-20250805", "Claude 4.1 Opus"))
    register(OneMinModel("1min/claude-4-5-opus", "claude-opus-4-5-20251101", "Claude 4.5 Opus"))
    register(OneMinModel("1min/claude-4-6-opus", "claude-opus-4-6", "Claude 4.6 Opus"))
    register(OneMinModel("1min/claude-4-5-haiku", "claude-haiku-4-5-20251001", "Claude 4.5 Haiku"))

    # Google Models
    register(OneMinModel("1min/gemini-2.5-flash", "gemini-2.5-flash", "Gemini 2.5 Flash"))
    register(OneMinModel("1min/gemini-2.5-pro", "gemini-2.5-pro", "Gemini 2.5 Pro"))
    register(
        OneMinModel("1min/gemini-3-flash", "gemini-3-flash-preview", "Gemini 3 Flash (Preview)")
    )
    register(
        OneMinModel(
            "1min/gemini-3.1-flash-lite",
            "gemini-3.1-flash-lite-preview",
            "Gemini 3.1 Flash Lite (Preview)",
        )
    )
    register(
        OneMinModel("1min/gemini-3.1-pro", "gemini-3.1-pro-preview", "Gemini 3.1 Pro (Preview)")
    )

    # Alibaba (Qwen) Models
    register(OneMinModel("1min/qwen-flash", "qwen-flash", "Qwen Flash"))
    register(OneMinModel("1min/qwen-plus", "qwen-plus", "Qwen Plus"))
    register(OneMinModel("1min/qwen-max", "qwen-max", "Qwen Max"))
    register(OneMinModel("1min/qwen-vl-plus", "qwen-vl-plus", "Qwen VL Plus"))
    register(OneMinModel("1min/qwen-vl-max", "qwen-vl-max", "Qwen VL Max"))
    register(OneMinModel("1min/qwen3-max", "qwen3-max", "Qwen3 Max"))
    register(OneMinModel("1min/qwen3-vl-flash", "qwen3-vl-flash", "Qwen3 VL Flash"))
    register(OneMinModel("1min/qwen3-vl-plus", "qwen3-vl-plus", "Qwen3 VL Plus"))
    register(OneMinModel("1min/qwen3-coder-plus", "qwen3-coder-plus", "Qwen3 Coder Plus"))
    register(OneMinModel("1min/qwen3-coder-flash", "qwen3-coder-flash", "Qwen3 Coder Flash"))

    # DeepSeek Models
    register(OneMinModel("1min/deepseek-chat", "deepseek-chat", "DeepSeek V3.2 Chat"))
    register(OneMinModel("1min/deepseek-reasoner", "deepseek-reasoner", "DeepSeek V3.2 Reasoner"))

    # xAI Models
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
    register(
        OneMinModel("1min/mistral-medium-latest", "mistral-medium-latest", "Mistral Medium 3.1")
    )
    register(OneMinModel("1min/mistral-large-latest", "mistral-large-latest", "Mistral Large 2"))
    register(
        OneMinModel("1min/magistral-small-latest", "magistral-small-latest", "Magistral Small 1.2")
    )
    register(
        OneMinModel(
            "1min/magistral-medium-latest", "magistral-medium-latest", "Magistral Medium 1.2"
        )
    )
    register(OneMinModel("1min/ministral-14b-latest", "ministral-14b-latest", "Ministral 14B"))

    # Cohere Models
    register(OneMinModel("1min/command-r", "command-r-08-2024", "Command R"))

    # Meta / open-source
    register(OneMinModel("1min/llama-2-70b", "meta/llama-2-70b-chat", "LLaMA 2 70b"))
    register(OneMinModel("1min/llama-3-70b", "meta/meta-llama-3-70b-instruct", "LLaMA 3 70b"))
    register(OneMinModel("1min/llama-4-scout", "meta/llama-4-scout-instruct", "LLaMA 4 Scout"))
    register(
        OneMinModel("1min/llama-4-maverick", "meta/llama-4-maverick-instruct", "LLaMA 4 Maverick")
    )
    register(OneMinModel("1min/gpt-oss-20b", "openai/gpt-oss-20b", "GPT OSS 20b"))
    register(OneMinModel("1min/gpt-oss-120b", "openai/gpt-oss-120b", "GPT OSS 120b"))

    # Perplexity Models
    register(OneMinModel("1min/sonar", "sonar", "Perplexity Sonar"))
    register(OneMinModel("1min/sonar-pro", "sonar-pro", "Perplexity Sonar Pro"))
    register(
        OneMinModel(
            "1min/sonar-reasoning-pro",
            "sonar-reasoning-pro",
            "Perplexity Sonar Reasoning Pro",
        )
    )
    register(
        OneMinModel(
            "1min/sonar-deep-research",
            "sonar-deep-research",
            "Perplexity Sonar Deep Research",
        )
    )


class OneMinModel(llm.Model):
    """
    LLM plugin for 1min.ai API

    This plugin integrates 1min.ai's conversational AI capabilities into LLM.
    Set your API key with: llm keys set 1min

    Available providers (run `llm 1min models` for full IDs):
    - OpenAI: GPT-3.5/4/4.1/4o/5/5.1/5.2/5.4 + Codex variants, o3, o4 (incl. deep-research)
    - Anthropic: Claude 4 / 4.5 / 4.6 Sonnet, Claude 4 / 4.1 / 4.5 / 4.6 Opus, Claude 4.5 Haiku
    - Google: Gemini 2.5 Flash/Pro, Gemini 3 / 3.1 (Preview)
    - Alibaba: Qwen3 Max / VL / Coder, Qwen Plus / Max / Flash / VL
    - DeepSeek: V3.2 Chat, V3.2 Reasoner
    - xAI: Grok 3 / 4 / Code Fast
    - Mistral: Mistral Small/Medium/Large, Magistral, Ministral, Open Mistral Nemo
    - Cohere: Command R
    - Meta / open-source: LLaMA 2/3/4, GPT OSS 20b/120b
    - Perplexity: Sonar, Sonar Pro, Sonar Reasoning Pro, Sonar Deep Research
    """

    needs_key = "1min"
    key_env_var = "ONEMIN_API_KEY"
    can_stream = True  # /api/chat-with-ai supports SSE streaming with isStreaming=true

    class Options(llm.Options):
        conversation_type: Optional[str] = Field(
            description="Type of conversation: UNIFY_CHAT_WITH_AI (default) or CODE_GENERATOR",
            default="UNIFY_CHAT_WITH_AI",
        )

        # webSearchSettings
        web_search: Optional[bool] = Field(
            description="Enable web search for grounding responses", default=False
        )
        num_of_site: Optional[int] = Field(
            description="Number of sites to search when web_search is enabled (1-10)", default=3
        )
        max_word: Optional[int] = Field(
            description="Maximum words to extract from web search results (100-10000)",
            default=1000,
        )

        # historySettings
        history_mixed: Optional[bool] = Field(
            description="Mix context from different AI models in conversation history",
            default=False,
        )
        history_limit: Optional[int] = Field(
            description="Maximum number of history messages to include as context (1-50)",
            default=10,
        )

        # Memory + brand voice
        with_memories: Optional[bool] = Field(
            description="Enable AI memory across conversations", default=False
        )
        brand_voice_id: Optional[str] = Field(
            description="Brand voice ID to apply a custom tone/style to the response",
            default=None,
        )

        # Attachments (comma-separated keys/IDs from Asset API)
        images: Optional[str] = Field(
            description="Comma-separated image asset keys (from Asset API)", default=None
        )
        files: Optional[str] = Field(
            description="Comma-separated file IDs (from Asset API)", default=None
        )

        # Debug mode
        debug: Optional[bool] = Field(
            description="Show debug information including API request details", default=False
        )

        @field_validator("conversation_type")
        @classmethod
        def validate_conversation_type(cls, conv_type):
            if conv_type not in ["UNIFY_CHAT_WITH_AI", "CODE_GENERATOR"]:
                raise ValueError("conversation_type must be UNIFY_CHAT_WITH_AI or CODE_GENERATOR")
            return conv_type

        @field_validator("num_of_site")
        @classmethod
        def validate_num_of_site(cls, value):
            if value is not None and (value < 1 or value > 10):
                raise ValueError("num_of_site must be between 1 and 10")
            return value

        @field_validator("max_word")
        @classmethod
        def validate_max_word(cls, value):
            if value is not None and (value < 100 or value > 10000):
                raise ValueError("max_word must be between 100 and 10000")
            return value

        @field_validator("history_limit")
        @classmethod
        def validate_history_limit(cls, value):
            if value is not None and (value < 1 or value > 50):
                raise ValueError("history_limit must be between 1 and 50")
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

    def get_or_create_conversation(self, key, conversation, prompt, conversation_type=None):
        """
        Get existing 1min.ai conversation UUID or create a new one.

        Args:
            key: API key
            conversation: LLM conversation object (may be None)
            prompt: LLM prompt object
            conversation_type: Override conversation type for new conversations.
                If None, falls back to prompt.options.conversation_type.

        Returns:
            1min.ai conversation UUID
        """
        # Reload conversation mappings from disk
        _load_conversations()

        # Debug logging
        debug_mode = prompt.options.debug or os.environ.get("LLM_1MIN_DEBUG", "").lower() in (
            "1",
            "true",
            "yes",
        )
        if debug_mode:
            print("\n[DEBUG] Conversation info:", file=sys.stderr)
            print(
                f"  conversation type: {type(conversation).__name__ if conversation else 'None'}",
                file=sys.stderr,
            )
            if conversation:
                print(f"  conversation.id: {getattr(conversation, 'id', 'N/A')}", file=sys.stderr)
                print(
                    f"  conversation.name: {getattr(conversation, 'name', 'N/A')}", file=sys.stderr
                )

        # Generate keys for this conversation
        # If history_mixed is enabled, use conversation ID only (shared across models)
        # Otherwise, use conversation ID + model ID (separate per model)
        history_mixed = prompt.options.history_mixed

        model_only_key = f"{self.model_id}"
        conv_specific_key = None
        if conversation and hasattr(conversation, "id"):
            if history_mixed:
                # Use conversation ID only - shared across all models
                conv_specific_key = f"{conversation.id}"
            else:
                # Use conversation ID + model ID - separate per model
                conv_specific_key = f"{conversation.id}_{self.model_id}"

        if debug_mode:
            print(f"  model_only_key: {model_only_key}", file=sys.stderr)
            print(f"  conv_specific_key: {conv_specific_key}", file=sys.stderr)
            print(f"  existing mappings: {list(_conversation_mapping.keys())}", file=sys.stderr)

        # Check if we have a conversation for this
        # Try conversation-specific key first, then model-only key
        conversation_uuid = None
        if conv_specific_key and conv_specific_key in _conversation_mapping:
            conversation_uuid = _conversation_mapping[conv_specific_key]
            if debug_mode:
                print(f"  ✓ Found via conv_specific_key: {conversation_uuid}", file=sys.stderr)
        elif model_only_key in _conversation_mapping:
            conversation_uuid = _conversation_mapping[model_only_key]
            # Migrate to conversation-specific key if we have a conversation ID
            if conv_specific_key:
                _conversation_mapping[conv_specific_key] = conversation_uuid
                del _conversation_mapping[model_only_key]
                _save_conversations()
                if debug_mode:
                    print(
                        f"  ✓ Migrated from model_only_key to conv_specific_key: {conversation_uuid}",
                        file=sys.stderr,
                    )
            else:
                if debug_mode:
                    print(f"  ✓ Found via model_only_key: {conversation_uuid}", file=sys.stderr)
        elif history_mixed and conversation and hasattr(conversation, "id"):
            # For history_mixed, check if there's a conversation from another model
            # with this same LLM conversation ID that we can reuse
            for key, uuid in list(_conversation_mapping.items()):
                if key.startswith(f"{conversation.id}_"):
                    conversation_uuid = uuid
                    # Migrate to conversation-only key (shared across models)
                    _conversation_mapping[conv_specific_key] = conversation_uuid
                    del _conversation_mapping[key]
                    _save_conversations()
                    if debug_mode:
                        print(
                            f"  ✓ Found conversation from other model, migrated to shared key: {conversation_uuid}",
                            file=sys.stderr,
                        )
                        print(
                            f"    Old key: {key} -> New key: {conv_specific_key}", file=sys.stderr
                        )
                    break

        if conversation_uuid:
            return conversation_uuid

        # No existing conversation found, create a new one
        conv_key = conv_specific_key if conv_specific_key else model_only_key

        # Create a new 1min.ai conversation
        conv_type = conversation_type or prompt.options.conversation_type or "UNIFY_CHAT_WITH_AI"

        headers = {"API-KEY": key, "Content-Type": "application/json"}

        payload = {
            "title": f"LLM Chat - {self.display_name}",
            "type": conv_type,
            "model": self.api_model_id,  # Use actual API model ID, not LLM ID
        }

        try:
            response = requests.post(
                "https://api.1min.ai/api/conversations", headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            conversation_uuid = response.json()["conversation"]["uuid"]
            _conversation_mapping[conv_key] = conversation_uuid
            _save_conversations()  # Persist to disk

            if debug_mode:
                print(f"  ✓ Created new conversation: {conversation_uuid}", file=sys.stderr)
                print(f"  ✓ Stored with key: {conv_key}", file=sys.stderr)

            return conversation_uuid

        except requests.exceptions.RequestException as e:
            raise llm.ModelError(f"Failed to create conversation: {str(e)}")

    def execute(self, prompt, stream, response, conversation):
        """Execute a prompt against the 1min.ai API"""
        key = self.get_key()

        # Load options from config (global + per-model)
        global_options = _options_config.get_defaults()
        model_options = _options_config.get_model_options(self.api_model_id)
        builtin_defaults = MODEL_DEFAULTS.get(self.api_model_id, {})

        # Merge: builtin < global < model-specific < CLI
        merged_options = {**builtin_defaults, **global_options, **model_options}

        cli_options = {}
        opts = prompt.options
        if opts.conversation_type != "UNIFY_CHAT_WITH_AI":
            cli_options["conversation_type"] = opts.conversation_type
        if opts.web_search is not False:
            cli_options["web_search"] = opts.web_search
        if opts.num_of_site != 3:
            cli_options["num_of_site"] = opts.num_of_site
        if opts.max_word != 1000:
            cli_options["max_word"] = opts.max_word
        if opts.history_mixed is not False:
            cli_options["history_mixed"] = opts.history_mixed
        if opts.history_limit != 10:
            cli_options["history_limit"] = opts.history_limit
        if opts.with_memories is not False:
            cli_options["with_memories"] = opts.with_memories
        if opts.brand_voice_id is not None:
            cli_options["brand_voice_id"] = opts.brand_voice_id
        if opts.images is not None:
            cli_options["images"] = opts.images
        if opts.files is not None:
            cli_options["files"] = opts.files

        merged_options.update(cli_options)

        debug_mode = opts.debug or os.environ.get("LLM_1MIN_DEBUG", "").lower() in (
            "1",
            "true",
            "yes",
        )
        if debug_mode:
            redacted_global_options = self._redact_options_for_debug(global_options)
            redacted_model_options = self._redact_options_for_debug(model_options)
            redacted_cli_options = self._redact_options_for_debug(cli_options)
            redacted_merged_options = self._redact_options_for_debug(merged_options)
            print(f"\n{'=' * 70}", file=sys.stderr)
            print("[DEBUG] 1min.ai API Request Details", file=sys.stderr)
            print(f"{'=' * 70}", file=sys.stderr)
            print(f"Model: {self.api_model_id}", file=sys.stderr)
            print("\nOptions (priority: CLI > user config > built-in defaults):", file=sys.stderr)
            print(f"  Built-in model defaults: {builtin_defaults}", file=sys.stderr)
            print(f"  User global options: {redacted_global_options}", file=sys.stderr)
            print(f"  User model-specific options: {redacted_model_options}", file=sys.stderr)
            print(f"  CLI options: {redacted_cli_options}", file=sys.stderr)
            print("\nFinal merged options:", file=sys.stderr)
            print(f"  {redacted_merged_options}", file=sys.stderr)
            print(f"{'=' * 70}", file=sys.stderr)

        conversation_type = merged_options.get("conversation_type", "UNIFY_CHAT_WITH_AI")
        conversation_uuid = self.get_or_create_conversation(
            key, conversation, prompt, conversation_type=conversation_type
        )

        if conversation_type == "CODE_GENERATOR":
            yield from self._execute_feature(
                key, prompt, conversation_uuid, merged_options, debug_mode, conversation
            )
        else:
            yield from self._execute_chat(
                key, prompt, conversation_uuid, merged_options, debug_mode, stream, conversation
            )

    def _build_mixed_prompt(self, prompt, conversation, limit):
        """Inline prior LLM-DB turns into the prompt for cross-model recall."""
        responses = getattr(conversation, "responses", None) or []
        if not responses:
            return prompt.prompt
        recent = responses[-limit:] if limit and limit > 0 else responses
        lines = []
        for r in recent:
            prior_prompt = getattr(getattr(r, "prompt", None), "prompt", "") or ""
            try:
                prior_text = r.text()
            except Exception:
                prior_text = ""
            if prior_prompt:
                lines.append(f"User: {prior_prompt}")
            if prior_text:
                lines.append(f"Assistant: {prior_text}")
        if not lines:
            return prompt.prompt
        return "\n".join(lines) + f"\n\nUser: {prompt.prompt}"

    def _execute_chat(
        self, key, prompt, conversation_uuid, merged, debug_mode, stream, conversation=None
    ):
        """POST /api/chat-with-ai with type=UNIFY_CHAT_WITH_AI."""
        prompt_text = prompt.prompt
        if merged.get("history_mixed", False) and conversation is not None:
            prompt_text = self._build_mixed_prompt(
                prompt, conversation, merged.get("history_limit", 10)
            )
        prompt_object = {"prompt": prompt_text}
        if conversation_uuid:
            prompt_object["conversationId"] = conversation_uuid

        settings = {}
        if merged.get("web_search", False):
            settings["webSearchSettings"] = {
                "webSearch": True,
                "numOfSite": merged.get("num_of_site", 3),
                "maxWord": merged.get("max_word", 1000),
            }
        if merged.get("history_mixed", False) or merged.get("history_limit", 10) != 10:
            settings["historySettings"] = {
                "isMixed": merged.get("history_mixed", False),
                "historyMessageLimit": merged.get("history_limit", 10),
            }
        if merged.get("with_memories", False):
            settings["withMemories"] = True
        if settings:
            prompt_object["settings"] = settings

        attachments = {}
        if merged.get("images"):
            attachments["images"] = [
                s.strip() for s in str(merged["images"]).split(",") if s.strip()
            ]
        if merged.get("files"):
            attachments["files"] = [s.strip() for s in str(merged["files"]).split(",") if s.strip()]
        if attachments:
            prompt_object["attachments"] = attachments

        payload = {
            "type": "UNIFY_CHAT_WITH_AI",
            "model": self.api_model_id,
            "promptObject": prompt_object,
        }
        if merged.get("brand_voice_id"):
            payload["brandVoiceId"] = merged["brand_voice_id"]

        url = "https://api.1min.ai/api/chat-with-ai"
        if stream:
            url = url + "?isStreaming=true"

        headers = {"API-KEY": key, "Content-Type": "application/json"}

        self._log_payload(url, payload, debug_mode)

        try:
            if stream:
                yield from self._stream_chat(url, headers, payload)
            else:
                api_response = requests.post(url, headers=headers, json=payload, timeout=120)
                api_response.raise_for_status()
                result_data = api_response.json()
                yield self._extract_result_text(result_data)
        except requests.exceptions.HTTPError as e:
            self._raise_http_error(e)
        except requests.exceptions.RequestException as e:
            raise llm.ModelError(f"API request failed: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise llm.ModelError(f"Failed to parse API response: {str(e)}")

    def _stream_chat(self, url, headers, payload):
        """Parse SSE stream from /api/chat-with-ai."""
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            event_name = None
            for raw_line in r.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue
                line = raw_line.strip()
                if not line:
                    event_name = None
                    continue
                if line.startswith("event:"):
                    event_name = line[len("event:") :].strip()
                    continue
                if line.startswith("data:"):
                    data_str = line[len("data:") :].strip()
                    if not data_str:
                        continue
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    if event_name == "content":
                        chunk = data.get("content", "")
                        if chunk:
                            yield chunk
                    elif event_name == "error":
                        msg = data.get("message") or data.get("error") or "Unknown stream error"
                        raise llm.ModelError(f"Stream error: {msg}")
                    elif event_name == "done":
                        return
                    # event_name == "result" -> ignore (final aiRecord; chunks already yielded)

    def _execute_feature(
        self, key, prompt, conversation_uuid, merged, debug_mode, conversation=None
    ):
        """POST /api/features with type=CODE_GENERATOR (legacy flat shape)."""
        prompt_text = prompt.prompt
        if merged.get("history_mixed", False) and conversation is not None:
            prompt_text = self._build_mixed_prompt(
                prompt, conversation, merged.get("history_limit", 10)
            )
        prompt_object = {"prompt": prompt_text}
        if merged.get("web_search", False):
            prompt_object["webSearch"] = True
            prompt_object["numOfSite"] = merged.get("num_of_site", 3)
            prompt_object["maxWord"] = merged.get("max_word", 1000)

        payload = {
            "type": "CODE_GENERATOR",
            "model": self.api_model_id,
            "conversationId": conversation_uuid,
            "promptObject": prompt_object,
        }

        url = "https://api.1min.ai/api/features"
        headers = {"API-KEY": key, "Content-Type": "application/json"}

        self._log_payload(url, payload, debug_mode)

        try:
            api_response = requests.post(url, headers=headers, json=payload, timeout=120)
            api_response.raise_for_status()
            yield self._extract_result_text(api_response.json())
        except requests.exceptions.HTTPError as e:
            self._raise_http_error(e)
        except requests.exceptions.RequestException as e:
            raise llm.ModelError(f"API request failed: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise llm.ModelError(f"Failed to parse API response: {str(e)}")

    @staticmethod
    def _extract_result_text(result_data):
        """Pull human-readable text out of an aiRecord response body.

        Spec: `aiRecord.aiRecordDetail.resultObject` is a list[str].
        """
        detail = result_data.get("aiRecord", {}).get("aiRecordDetail", {})
        result_object = detail.get("resultObject")
        if result_object is None:
            # Defensive: surface the raw body so failures aren't silent.
            return json.dumps(result_data, indent=2)
        if isinstance(result_object, list):
            return "\n".join(str(item) for item in result_object)
        if isinstance(result_object, dict):
            return json.dumps(result_object, indent=2)
        return str(result_object)

    @staticmethod
    def _raise_http_error(e):
        status = getattr(e.response, "status_code", None)
        if status == 401:
            raise llm.ModelError("Authentication failed. Please check your API key.")
        if status == 429:
            raise llm.ModelError("Rate limit exceeded. Please try again later.")
        raise llm.ModelError(f"API request failed: {str(e)}")

    @staticmethod
    def _log_payload(url, payload, debug_mode):
        """Print the API request payload to stderr when debug is on."""
        if not debug_mode:
            return
        redacted_payload = OneMinModel._redact_payload_for_debug(payload)
        print(f"\n{'=' * 70}", file=sys.stderr)
        print("[DEBUG] API Request Payload (sensitive fields redacted)", file=sys.stderr)
        print(f"{'=' * 70}", file=sys.stderr)
        print(f"Endpoint: {url}", file=sys.stderr)
        print("\nPayload:", file=sys.stderr)
        print(json.dumps(redacted_payload, indent=2), file=sys.stderr)
        print(f"{'=' * 70}\n", file=sys.stderr)

    @staticmethod
    def _redact_options_for_debug(options):
        """Redact sensitive option values before logging."""
        redacted = {}
        for key, value in options.items():
            if key in {"images", "files", "brand_voice_id"} and value is not None:
                redacted[key] = "<redacted>"
            else:
                redacted[key] = value
        return redacted

    @staticmethod
    def _redact_payload_for_debug(payload):
        """Redact prompt and attachment identifiers before logging payloads."""
        safe_payload = json.loads(json.dumps(payload))
        prompt_object = safe_payload.get("promptObject", {})
        prompt_text = prompt_object.get("prompt")
        if isinstance(prompt_text, str):
            prompt_object["prompt"] = f"<redacted:{len(prompt_text)} chars>"

        attachments = prompt_object.get("attachments")
        if isinstance(attachments, dict):
            for attachment_key in ("images", "files"):
                if attachment_key in attachments:
                    value = attachments.get(attachment_key)
                    count = len(value) if isinstance(value, list) else 1
                    attachments[attachment_key] = f"<redacted:{count} item(s)>"

        if safe_payload.get("brandVoiceId"):
            safe_payload["brandVoiceId"] = "<redacted>"

        return safe_payload


@llm.hookimpl
def register_commands(cli):
    """Register CLI commands for conversation management"""

    @cli.group(name="1min")
    def onemin_group():
        """Manage 1min.ai conversations and options.

        \b
        Examples:
          llm 1min models           # List models
          llm 1min options list     # View settings
          llm 1min conversations    # Active chats

        \b
        Debug (see API requests):
          llm -m 1min/gpt-4o -o debug true "test"
          LLM_1MIN_DEBUG=1 llm -m 1min/gpt-4o "test"
          llm models --options
        """
        pass

    @onemin_group.command(name="models")
    def list_models():
        """List all available 1min.ai models.

        Roster is derived from register_models(); registration order also
        controls grouping in the output.

        Example:
          llm 1min models | grep -i claude
        """
        captured = []
        register_models(lambda m: captured.append(m))

        click.echo(f"Available 1min.ai models ({len(captured)} total):\n")
        for m in captured:
            defaults = MODEL_DEFAULTS.get(m.api_model_id, {})
            tags = []
            if defaults.get("conversation_type") == "CODE_GENERATOR":
                tags.append("code")
            if defaults.get("web_search"):
                tags.append("web")
            tag_str = f"  [{', '.join(tags)}]" if tags else ""
            click.echo(f"  {click.style(m.model_id, fg='cyan', bold=True)}{tag_str}")
            click.echo(f"    Name: {m.display_name}")
            click.echo(f"    API: {m.api_model_id}")
            click.echo()

        click.echo("Tags: [code]=auto CODE_GENERATOR, [web]=auto web_search")
        click.echo("\nUsage:")
        click.echo('  llm -m <model-id> "your prompt"')
        click.echo("\nExample:")
        click.echo('  llm -m 1min/gpt-4o-mini "Explain Python decorators"')

    @onemin_group.command(name="conversations")
    def list_conversations():
        """List active 1min.ai conversations.

        Shows all tracked conversation UUIDs and their associated models.
        Each conversation maintains context across multiple messages.

        Example:
          llm 1min conversations
        """
        conversations = get_active_conversations()

        if not conversations:
            click.echo("No active conversations")
            return

        click.echo(f"Active conversations: {len(conversations)}\n")
        for key, uuid in conversations.items():
            click.echo(f"  {key}: {uuid}")

    @onemin_group.command(name="clear")
    @click.option("--model", "-m", help="Model ID to clear conversation for (e.g., 1min/gpt-4o)")
    @click.option("--all", "clear_all", is_flag=True, help="Clear all conversations")
    def clear_conversations_cmd(model, clear_all):
        """Clear conversation history.

        Use this to start fresh conversations or manage memory.

        Examples:
          llm 1min clear --model 1min/gpt-4o    # Clear specific model
          llm 1min clear --all                  # Clear all conversations
        """
        # Get API key from environment or LLM's key storage
        api_key = os.environ.get("ONEMIN_API_KEY")

        if not api_key:
            # Try to get from LLM's key storage
            try:
                # This is a bit hacky but works
                temp_model = OneMinModel("1min/gpt-4o-mini", "gpt-4o-mini", "GPT-4o Mini")
                api_key = temp_model.get_key()
            except Exception:
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

    @onemin_group.command(name="upload")
    @click.argument("file", type=click.Path(exists=True, dir_okay=False, readable=True))
    @click.option("--quiet", "-q", is_flag=True, help="Print only the asset key (no usage hint)")
    def upload_asset(file, quiet):
        """Upload an image or file to the 1min.ai Asset API.

        Prints the asset key returned by the server. Pass that key to
        the `images` or `files` option on a model invocation.

        Examples:
          llm 1min upload photo.png
          KEY=$(llm 1min upload -q photo.png)
          llm -m 1min/gpt-4o -o images "$KEY" "What is in this image?"
        """
        api_key = os.environ.get("ONEMIN_API_KEY")
        if not api_key:
            try:
                temp_model = OneMinModel("1min/gpt-4o-mini", "gpt-4o-mini", "GPT-4o Mini")
                api_key = temp_model.get_key()
            except Exception:
                click.echo(
                    "Error: No API key found. Set ONEMIN_API_KEY or use 'llm keys set 1min'",
                    err=True,
                )
                sys.exit(1)

        try:
            with open(file, "rb") as fh:
                response = requests.post(
                    "https://api.1min.ai/api/assets",
                    headers={"API-KEY": api_key},
                    files={"asset": (os.path.basename(file), fh)},
                    timeout=120,
                )
            response.raise_for_status()
            asset = response.json().get("asset") or {}
            key = asset.get("key")
            if not key:
                click.echo(f"Error: Upload succeeded but no key in response: {response.text}", err=True)
                sys.exit(1)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            body = e.response.text if e.response is not None else str(e)
            click.echo(f"Error: Upload failed (HTTP {status}): {body}", err=True)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            click.echo(f"Error: Upload failed: {e}", err=True)
            sys.exit(1)

        if quiet:
            click.echo(key)
            return

        opt = "images" if key.startswith("images/") else "files"
        click.echo(key)
        click.echo("", err=True)
        click.echo(f'Use: llm -m 1min/<model> -o {opt} "{key}" "your prompt"', err=True)

    @onemin_group.group(name="options")
    def options_group():
        """Manage persistent configuration options.

        Configure default behavior for web search, conversation types, and more.
        Settings can be global or per-model.

        Available options:
          - conversation_type (UNIFY_CHAT_WITH_AI / CODE_GENERATOR)
          - web_search (true/false): Enable web search
          - num_of_site (1-10): Sites to search when web_search is enabled
          - max_word (100-10000): Max words from web search results
          - history_mixed (true/false): Mix model contexts in conversation history
          - history_limit (1-50): Max history messages included as context
          - with_memories (true/false): Enable AI memory across conversations
          - brand_voice_id (string): Brand voice ID for response style
          - images (csv): Image asset keys (from Asset API), comma-separated
          - files (csv): File IDs (from Asset API), comma-separated
          - debug (true/false): Show API request details

        Examples:
          llm 1min options list              # View all settings
          llm 1min options set web_search true
          llm 1min options set --model sonar num_of_site 10
          llm 1min options migrate           # Rename legacy keys (e.g. is_mixed)
        """
        pass

    @options_group.command(name="set")
    @click.argument("key")
    @click.argument("value")
    @click.option(
        "--model",
        "-m",
        help="Set option for specific model (use API name: gpt-4o, not 1min/gpt-4o)",
    )
    def set_option(key, value, model):
        """Set a configuration option.

        Set options globally or for specific models. Use API model names
        (e.g., 'gpt-4o', 'sonar') not LLM IDs (not '1min/gpt-4o').

        Examples:
          llm 1min options set web_search true           # Global
          llm 1min options set --model gpt-4o web_search true
          llm 1min options set num_of_site 5
          llm 1min options set --model sonar num_of_site 10
        """
        legacy_renames = {"is_mixed": "history_mixed"}
        if key in legacy_renames:
            click.echo(
                f"Error: '{key}' was renamed to '{legacy_renames[key]}' in v0.4.0. "
                f"Use: llm 1min options set {legacy_renames[key]} {value}",
                err=True,
            )
            return

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
    @click.option("--model", "-m", help="Get option for specific model (API name)")
    def get_option(key, model):
        """Get a specific option value.

        Examples:
          llm 1min options get web_search                # Global value
          llm 1min options get --model gpt-4o web_search # Model-specific
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
    @click.option("--model", "-m", help="Show options for specific model only")
    def list_options(model):
        """Display all configuration options.

        Shows global defaults and per-model overrides.

        Examples:
          llm 1min options list                 # All settings
          llm 1min options list --model gpt-4o  # Model-specific only
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

    @options_group.command(name="defaults")
    def show_defaults():
        """Show built-in model defaults.

        These are optimized settings for specific models:
        - Code models use CODE_GENERATOR by default
        - Web-aware models have web_search enabled

        You can override these with your own settings.

        Example:
          llm 1min options defaults
        """
        click.echo("Built-in model defaults:\n")
        if MODEL_DEFAULTS:
            for model_id, defaults in MODEL_DEFAULTS.items():
                click.echo(f"  {click.style(model_id, fg='cyan', bold=True)}:")
                for key, value in defaults.items():
                    click.echo(f"    {key} = {value}")
                click.echo()
        else:
            click.echo("  No built-in defaults defined")

        click.echo("Priority: CLI options > User config > Built-in defaults")
        click.echo("\nOverride with: llm 1min options set --model <api-model-id> <key> <value>")

    @options_group.command(name="unset")
    @click.argument("key")
    @click.option("--model", "-m", help="Remove option from specific model")
    def unset_option(key, model):
        """Remove a configuration option.

        Reverts to default behavior for that option.

        Examples:
          llm 1min options unset web_search                 # Global
          llm 1min options unset --model gpt-4o web_search  # Model-specific
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
        """Reset all options to defaults.

        ⚠️  WARNING: Removes ALL global and per-model configurations.
        You will be prompted for confirmation.

        Example:
          llm 1min options reset
        """
        try:
            _options_config.reset()
            click.echo("All options reset to defaults")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="export")
    @click.option("--output", "-o", help="Output file path (prints to stdout if omitted)")
    def export_options(output):
        """Export configuration to JSON file.

        Useful for backup, sharing configs, or version control.

        Examples:
          llm 1min options export                        # Print to screen
          llm 1min options export -o backup.json         # Save to file
          llm 1min options export > my-settings.json     # Redirect output
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
        """Import configuration from JSON file.

        ⚠️  WARNING: This will replace your current configuration.
        Use 'export' first to backup existing settings.

        Example:
          llm 1min options import my-config.json
        """
        try:
            with open(file) as f:
                config = json.load(f)

            # Validate structure
            if not isinstance(config, dict):
                raise ValueError("Config must be a JSON object")

            _options_config.save(config)
            click.echo(f"Imported options from {file}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @options_group.command(name="migrate")
    def migrate_options():
        """Rename legacy option keys in saved config.

        Renames removed in v0.4.0:
          is_mixed → history_mixed

        Example:
          llm 1min options migrate
        """
        legacy_renames = {"is_mixed": "history_mixed"}

        if not _options_config.config_path.exists():
            click.echo("No saved config to migrate.")
            return

        try:
            with open(_options_config.config_path) as f:
                config = json.load(f)
        except Exception as e:
            click.echo(f"Error reading config: {e}", err=True)
            return

        changes = []

        def rename_in(scope_name, options):
            for old, new in legacy_renames.items():
                if old in options:
                    options[new] = options.pop(old)
                    changes.append(f"{scope_name}: {old} → {new}")

        defaults = config.get("defaults") or {}
        if isinstance(defaults, dict):
            rename_in("defaults", defaults)
            config["defaults"] = defaults

        models = config.get("models") or {}
        if isinstance(models, dict):
            for model_id, opts in models.items():
                if isinstance(opts, dict):
                    rename_in(f"models.{model_id}", opts)
            config["models"] = models

        if not changes:
            click.echo("No legacy keys found. Config is up to date.")
            return

        try:
            _options_config.save(config)
        except Exception as e:
            click.echo(f"Error writing config: {e}", err=True)
            return

        click.echo(f"Migrated {len(changes)} key(s):")
        for change in changes:
            click.echo(f"  {change}")
