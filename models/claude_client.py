#!/usr/bin/env python3
"""
Claude API Client Module
=========================
Handles all interactions with Anthropic's Claude models including Sonnet 4.5.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
import anthropic


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model: Optional[str] = None
    metadata: Optional[dict] = None


class ClaudeClient:
    """Client for interacting with Anthropic's Claude models"""

    # Model mapping for convenience
    MODEL_MAP = {
        'claude': 'claude-sonnet-4-5-20250929',
        'claude-sonnet': 'claude-sonnet-4-5-20250929',
        'claude-sonnet-4.5': 'claude-sonnet-4-5-20250929',
        'claude-opus': 'claude-opus-4.1-20250514',
        'claude-haiku': 'claude-haiku-20250305',
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude client

        Args:
            api_key: Anthropic API key. If not provided, will use ANTHROPIC_API_KEY from environment
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def call(
        self,
        messages: List[Message],
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4000,
        temperature: Optional[float] = None,
        system: Optional[str] = None
    ) -> str:
        """
        Call Claude API

        Args:
            messages: List of conversation messages
            model: Model to use (can use friendly names like 'claude' or full model IDs)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0). If None, uses Claude's default
            system: Optional system prompt

        Returns:
            The model's response text

        Raises:
            Exception: If the API call fails
        """
        try:
            # Map friendly model names to full model IDs
            resolved_model = self.MODEL_MAP.get(model, model)

            # Convert messages to Anthropic format
            formatted_messages = self._format_messages(messages)

            # Build API call parameters
            api_params = {
                "model": resolved_model,
                "max_tokens": max_tokens,
                "messages": formatted_messages
            }

            # Add optional parameters if provided
            if temperature is not None:
                api_params["temperature"] = temperature

            if system:
                api_params["system"] = system

            # Call Claude API
            response = self.client.messages.create(**api_params)

            return response.content[0].text

        except Exception as e:
            return f"Error calling Claude: {str(e)}"

    def _format_messages(self, messages: List[Message]) -> List[dict]:
        """
        Convert Message objects to Anthropic API format

        Args:
            messages: List of Message objects

        Returns:
            List of message dictionaries in Anthropic format
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        return formatted

    def get_model_info(self, model: str = "claude") -> dict:
        """
        Get information about a Claude model

        Args:
            model: Model name or ID

        Returns:
            Dictionary with model information
        """
        resolved_model = self.MODEL_MAP.get(model, model)

        return {
            "friendly_name": model,
            "model_id": resolved_model,
            "provider": "Anthropic",
            "available": True
        }


# Convenience function for backward compatibility
def call_claude(messages: List[Message], model: str = "claude-sonnet-4-5-20250929") -> str:
    """
    Legacy function for calling Claude (backward compatibility)

    Args:
        messages: List of conversation messages
        model: Model to use

    Returns:
        The model's response text
    """
    client = ClaudeClient()
    return client.call(messages, model=model)
