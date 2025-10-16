#!/usr/bin/env python3
"""
GPT-5 Pro API Client Module
============================
Handles all interactions with OpenAI's GPT-5 and GPT-5 Pro models.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model: Optional[str] = None
    metadata: Optional[dict] = None


class GPT5Client:
    """Client for interacting with GPT-5 and GPT-5 Pro models"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GPT-5 client

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from environment
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=self.api_key)

    def call(
        self,
        messages: List[Message],
        model: str = "gpt-5-pro",
        max_output_tokens: int = 4000,
        temperature: float = 0.7,
        reasoning_effort: str = "high"
    ) -> str:
        """
        Call GPT-5 or GPT-5 Pro using OpenAI Responses API (supports reasoning)

        Args:
            messages: List of conversation messages
            model: Model to use (gpt-5, gpt-5-pro, etc.)
            max_output_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            reasoning_effort: Effort level for reasoning (high, medium, low, minimal)

        Returns:
            The model's response text

        Raises:
            Exception: If the API call fails
        """
        try:
            # Convert messages to OpenAI format
            formatted_messages = self._format_messages(messages)

            # Use Responses API which supports reasoning parameter
            response = self.client.responses.create(
                model=model,
                reasoning={"effort": reasoning_effort},
                input=formatted_messages,
                max_output_tokens=max_output_tokens,
                temperature=temperature
            )

            return response.output_text

        except Exception as e:
            return f"Error calling GPT model: {str(e)}"

    def _format_messages(self, messages: List[Message]) -> List[dict]:
        """
        Convert Message objects to OpenAI API format

        Args:
            messages: List of Message objects

        Returns:
            List of message dictionaries in OpenAI format
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        return formatted


# Convenience function for backward compatibility
def call_gpt5(messages: List[Message], reasoning_effort: str = "high") -> str:
    """
    Legacy function for calling GPT-5 (backward compatibility)

    Args:
        messages: List of conversation messages
        reasoning_effort: Effort level for reasoning

    Returns:
        The model's response text
    """
    client = GPT5Client()
    return client.call(messages, reasoning_effort=reasoning_effort)
