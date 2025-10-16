"""
Conversation Manager
====================
Manages all active conversations with thread-safe operations.
"""

import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import asdict

from data_models import Message, Conversation


class ConversationManager:
    """Manages all active conversations with WebSocket integration"""

    def __init__(self, socketio):
        """
        Initialize the conversation manager.

        Args:
            socketio: Flask-SocketIO instance for real-time updates
        """
        self.conversations: Dict[str, Conversation] = {}
        self.lock = threading.Lock()
        self.socketio = socketio

    def create_conversation(self, model: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new conversation and return its ID.

        Args:
            model: The AI model to use for this conversation
            metadata: Optional metadata dictionary

        Returns:
            Unique conversation ID (UUID)
        """
        with self.lock:
            conv_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            self.conversations[conv_id] = Conversation(
                id=conv_id,
                model=model,
                messages=[],
                created_at=now,
                updated_at=now,
                metadata=metadata or {}
            )
            self._cleanup_old_conversations()
            return conv_id

    def add_message(self, conv_id: str, role: str, content: str, model: Optional[str] = None):
        """
        Add a message to a conversation and emit WebSocket event.

        Args:
            conv_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            model: Optional model identifier
        """
        with self.lock:
            if conv_id in self.conversations:
                message = Message(
                    role=role,
                    content=content,
                    timestamp=datetime.now().isoformat(),
                    model=model
                )
                self.conversations[conv_id].messages.append(message)
                self.conversations[conv_id].updated_at = datetime.now().isoformat()

                # Emit to WebSocket for live monitoring
                self.socketio.emit('new_message', {
                    'conversation_id': conv_id,
                    'message': asdict(message)
                })

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conv_id: Conversation ID

        Returns:
            Conversation object or None if not found
        """
        with self.lock:
            return self.conversations.get(conv_id)

    def list_conversations(self) -> List[Dict]:
        """
        List all active conversations with summary information.

        Returns:
            List of conversation summary dictionaries
        """
        with self.lock:
            return [
                {
                    'id': conv.id,
                    'model': conv.model,
                    'message_count': len(conv.messages),
                    'created_at': conv.created_at,
                    'updated_at': conv.updated_at,
                    'metadata': conv.metadata
                }
                for conv in self.conversations.values()
            ]

    def delete_conversation(self, conv_id: str) -> bool:
        """
        Delete a conversation by ID.

        Args:
            conv_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if conv_id in self.conversations:
                del self.conversations[conv_id]
                return True
            return False

    def _cleanup_old_conversations(self):
        """Remove conversations older than 20 days"""
        cutoff = datetime.now() - timedelta(days=20)
        to_remove = []
        for conv_id, conv in self.conversations.items():
            if datetime.fromisoformat(conv.updated_at) < cutoff:
                to_remove.append(conv_id)
        for conv_id in to_remove:
            del self.conversations[conv_id]
