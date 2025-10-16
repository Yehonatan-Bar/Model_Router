#!/usr/bin/env python3
"""
O3 Pro API Client Module
=========================
Handles all interactions with OpenAI's O3-Pro model using the Responses API.
Supports file uploads and configurable reasoning effort levels.
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


class O3Client:
    """Client for interacting with OpenAI's O3-Pro model"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the O3-Pro client

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
        reasoning_effort: str = "high",
        file_paths: Optional[List[str]] = None
    ) -> str:
        """
        Call OpenAI O3-Pro model using the Responses API

        Args:
            messages: List of conversation messages
            reasoning_effort: Effort level for reasoning ("high", "medium", "low", "minimal")
            file_paths: Optional list of file paths to upload and analyze

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

            # Build the input content array
            content = []

            # Add any uploaded files to the content
            for uploaded in uploaded_files:
                content.append({"type": "input_file", "file_id": uploaded.id})

            # Combine all messages into a single prompt for o3-pro
            # o3-pro works best with a single comprehensive prompt rather than conversation history
            combined_prompt = self._combine_messages(messages)

            # Add the combined prompt as input text
            content.append({"type": "input_text", "text": combined_prompt})

            # Call o3-pro with the specified effort level
            response = self.client.responses.create(
                model="o3-pro",
                reasoning={"effort": reasoning_effort},
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            # Extract text from the response
            result = self._extract_response_text(response)

            return result

        except Exception as e:
            return f"Error calling o3-pro: {str(e)}"

        finally:
            # Clean up uploaded files
            self._cleanup_files(uploaded_files)

    def _upload_files(self, file_paths: List[str]) -> List:
        """
        Upload files to OpenAI for analysis

        Args:
            file_paths: List of file paths to upload

        Returns:
            List of uploaded file objects
        """
        uploaded_files = []

        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        uploaded = self.client.files.create(
                            file=f,
                            purpose="user_data"
                        )
                        uploaded_files.append(uploaded)
                except Exception as e:
                    print(f"Warning: Failed to upload file {file_path}: {str(e)}")
            else:
                print(f"Warning: File not found: {file_path}")

        return uploaded_files

    def _combine_messages(self, messages: List[Message]) -> str:
        """
        Combine conversation messages into a single prompt

        Args:
            messages: List of Message objects

        Returns:
            Combined prompt string
        """
        combined_prompt = ""
        for msg in messages:
            if msg.role == "user":
                combined_prompt += f"User: {msg.content}\n\n"
            elif msg.role == "assistant":
                combined_prompt += f"Assistant: {msg.content}\n\n"

        return combined_prompt.strip()

    def _extract_response_text(self, response) -> str:
        """
        Extract text from O3-Pro response object

        Args:
            response: Response object from O3-Pro API

        Returns:
            Extracted text content
        """
        output_text = []
        for item in response.output:
            if getattr(item, "content", None):
                for c in item.content:
                    if getattr(c, "text", None):
                        output_text.append(c.text)

        return "".join(output_text)

    def _cleanup_files(self, uploaded_files: List):
        """
        Delete uploaded files from OpenAI

        Args:
            uploaded_files: List of uploaded file objects to delete
        """
        for uploaded in uploaded_files:
            try:
                self.client.files.delete(uploaded.id)
            except Exception as e:
                # Ignore cleanup errors - files will auto-expire
                print(f"Warning: Failed to delete file {uploaded.id}: {str(e)}")


# Convenience function for backward compatibility
def call_o3_pro(
    messages: List[Message],
    reasoning_effort: str = "high",
    file_paths: Optional[List[str]] = None
) -> str:
    """
    Legacy function for calling O3-Pro (backward compatibility)

    Args:
        messages: List of conversation messages
        reasoning_effort: Effort level for reasoning
        file_paths: Optional list of file paths to upload and analyze

    Returns:
        The model's response text
    """
    client = O3Client()
    return client.call(messages, reasoning_effort=reasoning_effort, file_paths=file_paths)
