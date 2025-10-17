"""
Anthropic provider for Claude AI models.

Integrates with Anthropic API for content generation.
Requires: anthropic package and ANTHROPIC_API_KEY environment variable.
"""

import os
from typing import Any, Dict, List

from .base import AIProvider


class AnthropicProvider(AIProvider):
    """
    Anthropic API provider for Claude models.

    Usage:
    1. Install: pip install anthropic (or uv sync)
    2. Set environment variable: export ANTHROPIC_API_KEY=sk-ant-...
    3. Use in WorkshopForge: --provider anthropic
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider.

        Args:
            model: Model identifier (default: claude-3-5-sonnet-20241022)
                   Options: claude-3-5-sonnet-20241022, claude-3-opus-20240229, etc.

        Raises:
            RuntimeError: If ANTHROPIC_API_KEY not set
            ImportError: If anthropic package not installed
        """
        self.model = model

        # Validate API key exists
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable not set.\n"
                "Get your API key from: https://console.anthropic.com/settings/keys\n"
                "Then set: export ANTHROPIC_API_KEY=sk-ant-..."
            )

        # Initialize Anthropic client
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError as e:
            raise ImportError("anthropic package not installed. Install with: uv sync") from e

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generate completion using Anthropic API.

        Args:
            messages: Message list with 'role' and 'content' keys
                      Expects: [{"role": "system", "content": "..."},
                               {"role": "user", "content": "..."}]
            **kwargs: Anthropic-specific parameters
                     - temperature: float (default: 0.7)
                     - max_tokens: int (default: 4096)
                     - top_p: float (default: 1.0)

        Returns:
            Generated text content

        Raises:
            RuntimeError: If API call fails
        """
        # Extract system message (Anthropic requires it separate)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")

        # Extract user messages (Anthropic expects only user/assistant in messages array)
        user_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("user", "assistant")
        ]

        # Set default parameters for content generation
        params = {
            "temperature": 0.7,  # Balanced creativity/consistency
            "max_tokens": 4096,  # Sufficient for workshop content
            "top_p": 1.0,
        }
        params.update(kwargs)  # Allow overrides

        try:
            response = self.client.messages.create(
                model=self.model, system=system_msg, messages=user_messages, **params
            )

            # Extract text from response
            # Anthropic returns content as list of content blocks
            return response.content[0].text

        except Exception as e:
            raise RuntimeError(
                f"Anthropic API call failed: {e}\n"
                f"Model: {self.model}\n"
                f"Check your API key and credits at: https://console.anthropic.com"
            ) from e

    def get_name(self) -> str:
        """Get provider name."""
        return f"anthropic-{self.model}"
