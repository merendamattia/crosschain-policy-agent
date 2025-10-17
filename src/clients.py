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
def _register_builtin_providers():
    # Lazy imports inside factories to avoid raising ImportError on import time
    # if optional packages aren't installed.

    def google_factory(cfg: Dict[str, Any]):
        from datapizza.clients.google import GoogleClient

        return GoogleClient(
            api_key=cfg.get("api_key") or os.getenv("GOOGLE_API_KEY"),
            model=cfg.get("model") or os.getenv("GOOGLE_MODEL"),
        )

    def openai_factory(cfg: Dict[str, Any]):
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

    register("google", google_factory)
    register("openai", openai_factory)


_register_builtin_providers()
