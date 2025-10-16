"""
Anthropic provider (stub).

Placeholder for Anthropic API integration. Implement when needed.
Requires: anthropic package and ANTHROPIC_API_KEY environment variable.
"""

import os
from typing import Any, Dict, List

from .base import AIProvider


class AnthropicProvider(AIProvider):
    """
    Anthropic API provider (stub implementation).

    To use:
    1. Install: pip install anthropic
    2. Set: export ANTHROPIC_API_KEY=sk-ant-...
    3. Implement complete() method below
    """

    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic provider.

        Args:
            model: Model identifier
        """
        self.model = model
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generate completion using Anthropic API.

        Args:
            messages: Message list (system + user messages)
            **kwargs: Anthropic-specific parameters

        Returns:
            Generated text

        Raises:
            NotImplementedError: Stub implementation
        """
        raise NotImplementedError(
            "Anthropic provider not yet implemented. "
            "To implement: install anthropic package and add completion logic here."
        )

        # Example implementation (uncomment when ready):
        # import anthropic
        # client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        #
        # # Anthropic API requires system message separate
        # system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        # user_messages = [m for m in messages if m["role"] == "user"]
        #
        # response = client.messages.create(
        #     model=self.model,
        #     system=system_msg,
        #     messages=user_messages,
        #     **kwargs
        # )
        # return response.content[0].text

    def get_name(self) -> str:
        """Get provider name."""
        return f"anthropic-{self.model}"
