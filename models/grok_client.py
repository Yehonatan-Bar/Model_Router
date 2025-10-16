#!/usr/bin/env python3
"""
Grok API Client Module
======================
Handles all interactions with xAI's Grok models including Grok-4-Fast-Reasoning.
"""

import os
from typing import List, Optional
from dataclasses import dataclass

# Try importing xAI SDK, fallback to OpenAI for compatibility
try:
    from xai_sdk import Client as XAIClient
    from xai_sdk.chat import system as xai_system, user as xai_user, assistant as xai_assistant
    USE_XAI_SDK = True
except ImportError:
    # Fallback to OpenAI SDK with custom base URL (xAI is OpenAI-compatible)
    try:
        from openai import OpenAI
        USE_XAI_SDK = False
    except ImportError:
        raise ImportError("Neither xai-sdk nor openai package found. Please install with: pip install xai-sdk")


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: str
    model: Optional[str] = None
    metadata: Optional[dict] = None


class GrokClient:
    """Client for interacting with xAI's Grok models"""

    # Model mapping for convenience
    MODEL_MAP = {
        'grok': 'grok-4-fast-reasoning',
        'grok-4': 'grok-4-fast-reasoning',
        'grok-4-fast': 'grok-4-fast-reasoning',
        'grok-4-fast-reasoning': 'grok-4-fast-reasoning',
        'grok-3': 'grok-3',
        'grok-2': 'grok-2',
        'grok-2-1212': 'grok-2-1212',
        'grok-2-latest': 'grok-2-latest',
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Grok client

        Args:
            api_key: xAI API key. If not provided, will use XAI_API_KEY or GROK_API_KEY from environment
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("xAI API key not provided and XAI_API_KEY/GROK_API_KEY environment variable not set")

        if USE_XAI_SDK:
            # Use native xAI SDK
            self.client = XAIClient(api_key=self.api_key)
            self.use_native = True
        else:
            # Use OpenAI SDK with xAI base URL (OpenAI-compatible)
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"
            )
            self.use_native = False

    def call(
        self,
        messages: List[Message],
        model: str = "grok-4-fast-reasoning",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Call Grok API

        Args:
            messages: List of conversation messages
            model: Model to use (can use friendly names like 'grok' or full model IDs)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            system_prompt: Optional system prompt to prepend
            stream: Whether to stream the response (not implemented in this version)

        Returns:
            The model's response text

        Raises:
            Exception: If the API call fails
        """
        try:
            # Map friendly model names to full model IDs
            resolved_model = self.MODEL_MAP.get(model, model)

            if self.use_native and USE_XAI_SDK:
                # Use native xAI SDK with chat sessions
                return self._call_native_sdk(messages, resolved_model, max_tokens, temperature, system_prompt)
            else:
                # Use OpenAI-compatible API
                return self._call_openai_compatible(messages, resolved_model, max_tokens, temperature, system_prompt)

        except Exception as e:
            return f"Error calling Grok: {str(e)}"

    def _call_native_sdk(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Call using native xAI SDK"""
        # Create initial messages list
        initial_messages = []

        # Add system prompt if provided
        if system_prompt:
            initial_messages.append(xai_system(system_prompt))

        # Extract system messages from conversation
        system_messages = [msg for msg in messages if msg.role == 'system']
        for sys_msg in system_messages:
            initial_messages.append(xai_system(sys_msg.content))

        # Create chat session
        chat = self.client.chat.create(
            model=model,
            messages=initial_messages if initial_messages else []
        )

        # Add user and assistant messages
        for msg in messages:
            if msg.role == 'system':
                continue  # Already added
            elif msg.role == 'user':
                chat.append(xai_user(msg.content))
            elif msg.role == 'assistant':
                chat.append(xai_assistant(msg.content))

        # Sample response
        response = chat.sample()
        return response.content

    def _call_openai_compatible(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Call using OpenAI-compatible API"""
        # Convert messages to OpenAI format
        formatted_messages = self._format_messages(messages, system_prompt)

        # Call Grok API (OpenAI-compatible endpoint)
        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )

        return response.choices[0].message.content

    def _format_messages(self, messages: List[Message], system_prompt: Optional[str] = None) -> List[dict]:
        """
        Convert Message objects to API format

        Args:
            messages: List of Message objects
            system_prompt: Optional system prompt to prepend

        Returns:
            List of message dictionaries in API format
        """
        formatted = []

        # Add system prompt if provided
        if system_prompt:
            formatted.append({
                "role": "system",
                "content": system_prompt
            })

        # Add conversation messages
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })

        return formatted

    def get_model_info(self, model: str = "grok") -> dict:
        """
        Get information about a Grok model

        Args:
            model: Model name or ID

        Returns:
            Dictionary with model information
        """
        resolved_model = self.MODEL_MAP.get(model, model)

        # Model capabilities info
        model_info = {
            "friendly_name": model,
            "model_id": resolved_model,
            "provider": "xAI",
            "available": True,
            "context_window": 2000000 if 'grok-4' in resolved_model else 128000,
            "supports_function_calling": True,
            "supports_vision": False  # Update if vision models become available
        }

        return model_info


# Convenience function for backward compatibility
def call_grok(
    messages: List[Message],
    model: str = "grok-4-fast-reasoning",
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Legacy function for calling Grok (backward compatibility)

    Args:
        messages: List of conversation messages
        model: Model to use (default: grok-4-fast-reasoning)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response

    Returns:
        The model's response text
    """
    client = GrokClient()
    return client.call(messages, model=model, temperature=temperature, max_tokens=max_tokens)
