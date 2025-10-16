"""
Data Models
===========
Core data structures for representing messages and conversations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class Conversation:
    """Represents a conversation with history"""
    id: str
    model: str
    messages: List[Message]
    created_at: str
    updated_at: str
    metadata: Dict
