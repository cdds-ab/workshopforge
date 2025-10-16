"""
Base interface for AI providers.

Defines the contract that all AI providers must implement
for prompt completion.
"""

from typing import Any, Dict, List


class AIProvider:
    """
    Abstract base class for AI providers.

    Providers implement the complete() method to generate text
    from a list of messages (system + user prompts).
    """

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generate completion from messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                      Example: [{"role": "system", "content": "..."},
                               {"role": "user", "content": "..."}]
            **kwargs: Provider-specific parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response

        Raises:
            NotImplementedError: If subclass doesn't implement
            RuntimeError: If provider call fails
        """
        raise NotImplementedError("Subclasses must implement complete()")

    def get_name(self) -> str:
        """
        Get provider name/identifier.

        Returns:
            Provider name string
        """
        return self.__class__.__name__
