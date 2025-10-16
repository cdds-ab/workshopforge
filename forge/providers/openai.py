"""
OpenAI provider (stub).

Placeholder for OpenAI API integration. Implement when needed.
Requires: openai package and OPENAI_API_KEY environment variable.
"""

import os
from typing import Any, Dict, List

from .base import AIProvider


class OpenAIProvider(AIProvider):
    """
    OpenAI API provider (stub implementation).

    To use:
    1. Install: pip install openai
    2. Set: export OPENAI_API_KEY=sk-...
    3. Implement complete() method below
    """

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.

        Args:
            model: Model identifier (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generate completion using OpenAI API.

        Args:
            messages: Message list for chat completion
            **kwargs: OpenAI-specific parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text

        Raises:
            NotImplementedError: Stub implementation
        """
        raise NotImplementedError(
            "OpenAI provider not yet implemented. "
            "To implement: install openai package and add completion logic here."
        )

        # Example implementation (uncomment when ready):
        # import openai
        # response = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=messages,
        #     **kwargs
        # )
        # return response.choices[0].message.content

    def get_name(self) -> str:
        """Get provider name."""
        return f"openai-{self.model}"
