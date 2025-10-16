#!/usr/bin/env python3
"""
Gemini 2.5 Pro API Client Module
=================================
Handles interactions with Google's most powerful Gemini 2.5 Pro model
with MAXIMUM reasoning effort using thinking_budget configuration.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
import google.generativeai as genai


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model: Optional[str] = None
    metadata: Optional[dict] = None


class GeminiClient:
    """Client for Google's Gemini 2.5 Pro with maximum reasoning power"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini 2.5 Pro client with maximum reasoning

        Args:
            api_key: Google API key. If not provided, will use GEMINI_API_KEY from environment
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided and GEMINI_API_KEY environment variable not set")

        # Configure the API key
        genai.configure(api_key=self.api_key)

    def call(
        self,
        messages: List[Message],
        file_paths: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Call Gemini 2.5 Pro with MAXIMUM reasoning effort

        Args:
            messages: List of conversation messages
            file_paths: Optional list of file paths to upload and analyze
            max_tokens: Maximum tokens in response (optional)
            temperature: Sampling temperature (optional)

        Returns:
            The model's response text

        Raises:
            Exception: If the API call fails
        """
        uploaded_files = []

        try:
            # Upload files if provided
            if file_paths:
                uploaded_files = self._upload_files(file_paths)

            # Configure generation with MAXIMUM reasoning effort
            # thinking_budget = -1 enables dynamic thinking for optimal reasoning
            generation_config_dict = {
                'extra_config': {
                    'thinking_config': {
                        'thinking_budget': -1  # Dynamic thinking - maximum reasoning
                    }
                }
            }

            # Add optional parameters
            if max_tokens:
                generation_config_dict['max_output_tokens'] = max_tokens
            if temperature is not None:
                generation_config_dict['temperature'] = temperature

            # Initialize Gemini 2.5 Pro with maximum reasoning configuration
            model = genai.GenerativeModel(
                'gemini-2.5-pro',
                generation_config=genai.types.GenerationConfig(**generation_config_dict)
            )

            # Prepare content parts
            content_parts = []

            # Add uploaded files first
            for uploaded_file in uploaded_files:
                content_parts.append(uploaded_file)

            # Format and add the conversation messages
            formatted_prompt = self._format_messages(messages)
            content_parts.append(formatted_prompt)

            # Generate content with maximum reasoning
            response = model.generate_content(content_parts)

            # Extract response text
            return response.text

        except Exception as e:
            return f"Error calling Gemini 2.5 Pro: {str(e)}"

        finally:
            # Clean up uploaded files
            self._cleanup_files(uploaded_files)

    def _upload_files(self, file_paths: List[str]) -> List:
        """
        Upload files to Gemini for analysis

        Args:
            file_paths: List of file paths to upload

        Returns:
            List of uploaded file objects
        """
        uploaded_files = []

        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    uploaded_file = genai.upload_file(file_path)
                    uploaded_files.append(uploaded_file)
                    print(f"Uploaded file: {file_path} -> {uploaded_file.name}")
                except Exception as e:
                    print(f"Warning: Failed to upload file {file_path}: {str(e)}")
            else:
                print(f"Warning: File not found: {file_path}")

        return uploaded_files

    def _format_messages(self, messages: List[Message]) -> str:
        """
        Format conversation messages for Gemini

        Args:
            messages: List of Message objects

        Returns:
            Formatted prompt string
        """
        formatted_prompt = ""

        for msg in messages:
            if msg.role == "user":
                formatted_prompt += f"User: {msg.content}\n\n"
            elif msg.role == "assistant":
                formatted_prompt += f"Assistant: {msg.content}\n\n"

        return formatted_prompt.strip()

    def _cleanup_files(self, uploaded_files: List):
        """
        Delete uploaded files from Gemini

        Args:
            uploaded_files: List of uploaded file objects to delete
        """
        for uploaded_file in uploaded_files:
            try:
                genai.delete_file(uploaded_file.name)
                print(f"Cleaned up file: {uploaded_file.name}")
            except Exception as e:
                # Ignore cleanup errors - files auto-expire after 48 hours
                print(f"Warning: Failed to delete file {uploaded_file.name}: {str(e)}")


# Convenience function for backward compatibility
def call_gemini(
    messages: List[Message],
    file_paths: Optional[List[str]] = None
) -> str:
    """
    Call Gemini 2.5 Pro with maximum reasoning effort

    Args:
        messages: List of conversation messages
        file_paths: Optional list of file paths to upload and analyze

    Returns:
        The model's response text
    """
    client = GeminiClient()
    return client.call(messages, file_paths=file_paths)
