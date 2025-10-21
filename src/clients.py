"""Client registry and factory for LLM clients.

This module exposes a simple registry where client factory callables can be
registered under a provider key (e.g. 'google', 'openai'). The `get_client`
function returns a ready-to-use client instance given the provider name and
configuration. This keeps provider selection extensible and avoids chained
if/else blocks in the CLI.

The registry holds callables with signature: Callable[[dict], Any]
which should accept a dict of keyword configuration values and return an
instance implementing the expected datapizza client interface.
"""
import logging
import os
from typing import Any, Callable, Dict

logger = logging.getLogger("policy_agent.clients")

# Registry mapping provider key -> factory callable
_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register(provider: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    """Register a factory for a provider key.

    If a provider is registered more than once, the latest registration wins.
    """
    _REGISTRY[provider] = factory
    logger.debug("Registered client provider '%s'", provider)


def get_client(provider: str, config: Dict[str, Any] | None = None) -> Any:
    """Return a client instance for the given provider.

    Args:
        provider: The provider key (e.g. 'google', 'openai').
        config: Optional dict of configuration (api_key, model, etc.).

    Raises:
        KeyError: if the provider is unknown.
        RuntimeError: if the selected provider's factory raises an import or
            instantiation error (wrapped to provide a helpful message).
    """
    cfg = dict(config or {})
    try:
        factory = _REGISTRY[provider]
    except KeyError:
        raise KeyError(
            f"Unknown client provider: '{provider}'. Available: {list(_REGISTRY.keys())}"
        )

    try:
        return factory(cfg)
    except Exception as exc:
        # surface a clearer error message for optional dependencies
        raise RuntimeError(
            f"Failed to instantiate client for provider '{provider}': {exc}"
        ) from exc


# Register built-in providers at import time.
def _register_builtin_providers() -> None:
    """Register all built-in client providers at import time.

    This function defines and registers factory functions for supported providers:
    - google: GoogleClient for Google Generative AI
    - openai: OpenAIClient for OpenAI API
    - ollama: OpenAILikeClient for local Ollama models

    Lazy imports are used inside factories to avoid raising ImportError at import
    time if optional packages aren't installed.
    """

    def google_factory(cfg: Dict[str, Any]) -> Any:
        """Create and return a GoogleClient instance.

        Args:
            cfg: Configuration dict with optional 'api_key' and 'model' keys.
                 Falls back to GOOGLE_API_KEY and GOOGLE_MODEL environment variables.

        Returns:
            A configured GoogleClient instance.

        Raises:
            RuntimeError: If the datapizza.clients.google module cannot be imported.
        """
        from datapizza.clients.google import GoogleClient

        return GoogleClient(
            api_key=cfg.get("api_key") or os.getenv("GOOGLE_API_KEY"),
            model=cfg.get("model") or os.getenv("GOOGLE_MODEL"),
        )

    def openai_factory(cfg: Dict[str, Any]) -> Any:
        """Create and return an OpenAIClient instance.

        Args:
            cfg: Configuration dict with optional 'api_key' and 'model' keys.
                 Falls back to OPENAI_API_KEY and OPENAI_MODEL environment variables.

        Returns:
            A configured OpenAIClient instance.

        Raises:
            RuntimeError: If the datapizza.clients.openai module is not installed.
        """
        try:
            from datapizza.clients.openai import OpenAIClient
        except Exception as exc:
            raise RuntimeError(
                "OpenAI client support not installed. Please install the optional 'datapizza-ai-clients-openai' package."
            ) from exc
        return OpenAIClient(
            api_key=cfg.get("api_key") or os.getenv("OPENAI_API_KEY"),
            model=cfg.get("model") or os.getenv("OPENAI_MODEL"),
        )

    def ollama_factory(cfg: Dict[str, Any]) -> Any:
        """Create and return an OpenAILikeClient instance configured for Ollama.

        Args:
            cfg: Configuration dict with optional 'model' and 'base_url' keys.
                 Falls back to OLLAMA_MODEL and OLLAMA_URL environment variables.
                 api_key is always empty as Ollama doesn't require authentication.

        Returns:
            A configured OpenAILikeClient instance for Ollama.

        Raises:
            RuntimeError: If the datapizza.clients.openai_like module is not installed.
        """
        try:
            from datapizza.clients.openai_like import OpenAILikeClient
        except Exception as exc:
            raise RuntimeError(
                "Ollama client support not installed. Please install the optional 'datapizza-ai-clients-openai-like' package."
            ) from exc
        return OpenAILikeClient(
            api_key="",
            model=cfg.get("model") or os.getenv("OLLAMA_MODEL"),
            base_url=cfg.get("base_url") or os.getenv("OLLAMA_URL"),
        )

    register("google", google_factory)
    register("openai", openai_factory)
    register("ollama", ollama_factory)


_register_builtin_providers()
