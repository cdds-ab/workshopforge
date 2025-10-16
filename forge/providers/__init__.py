"""
AI provider interfaces for WorkshopForge.

Supports multiple AI backends (OpenAI, Anthropic, local echo)
with a common interface for prompt completion.
"""

from .base import AIProvider
from .echo import EchoProvider

__all__ = ["AIProvider", "EchoProvider", "get_provider"]


def get_provider(provider_name: str) -> AIProvider:
    """
    Get AI provider instance by name.

    Args:
        provider_name: Provider identifier (echo, openai, anthropic)

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider name unknown
    """
    if provider_name == "echo":
        return EchoProvider()
    elif provider_name == "openai":
        from .openai import OpenAIProvider

        return OpenAIProvider()
    elif provider_name == "anthropic":
        from .anthropic import AnthropicProvider

        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
