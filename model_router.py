#!/usr/bin/env python3
"""
Model Router API Server
=======================
Flask server that enables Claude Code to communicate with multiple AI models
with conversation management, live monitoring, and XML configuration.
"""

import os
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# Import modular API clients
from models import call_gpt5, call_o3_pro, call_claude, call_grok, call_gemini

# Load environment variables
load_dotenv()
load_dotenv('.env.gpt5')

app = Flask(__name__)
CORS(app, origins="*")  # Allow Claude Code to access from any origin
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# Data Models
# ============================================================

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

class ConversationManager:
    """Manages all active conversations"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.lock = threading.Lock()

    def create_conversation(self, model: str, metadata: Optional[Dict] = None) -> str:
        """Create a new conversation and return its ID"""
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
        """Add a message to a conversation"""
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
                socketio.emit('new_message', {
                    'conversation_id': conv_id,
                    'message': asdict(message)
                })

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        with self.lock:
            return self.conversations.get(conv_id)

    def list_conversations(self) -> List[Dict]:
        """List all active conversations"""
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

    def _cleanup_old_conversations(self):
        """Remove conversations older than 20 days"""
        cutoff = datetime.now() - timedelta(days=20)
        to_remove = []
        for conv_id, conv in self.conversations.items():
            if datetime.fromisoformat(conv.updated_at) < cutoff:
                to_remove.append(conv_id)
        for conv_id in to_remove:
            del self.conversations[conv_id]

# ============================================================
# XML Prompt Configuration
# ============================================================

class PromptConfig:
    """Manages XML-based prompt configuration"""

    def __init__(self, config_file: str = 'prompts.xml'):
        self.config_file = config_file
        self.prompts = {}
        self.load_config()

    def load_config(self):
        """Load prompts from XML file"""
        if not os.path.exists(self.config_file):
            self.create_default_config()

        tree = ET.parse(self.config_file)
        root = tree.getroot()

        for prompt_elem in root.findall('prompt'):
            name = prompt_elem.get('name')
            content = prompt_elem.text.strip()
            self.prompts[name] = content

    def create_default_config(self):
        """Create default XML configuration file"""
        root = ET.Element('prompts')

        # Add clarification prompt
        clarification = ET.SubElement(root, 'prompt', name='clarification')
        clarification.text = """
Before responding, please consider if you need any clarification about the request.
If the request is ambiguous or lacks important details, ask for clarification first.
Be specific about what information would help you provide a better response.
        """

        # Add system prompt
        system = ET.SubElement(root, 'prompt', name='system')
        system.text = """
You are a helpful AI assistant participating in a collaborative conversation.
Provide clear, accurate, and helpful responses.
        """

        # Add thinking prompt
        thinking = ET.SubElement(root, 'prompt', name='thinking')
        thinking.text = """
Think step by step about the problem before providing a solution.
Consider edge cases and potential issues.
        """

        tree = ET.ElementTree(root)
        tree.write(self.config_file, encoding='utf-8', xml_declaration=True)

    def get_prompt(self, name: str) -> Optional[str]:
        """Get a prompt by name"""
        return self.prompts.get(name)

# ============================================================
# Model Calling Functions
# ============================================================
# Note: Model calling functions have been moved to separate modules
# in the 'models' package for better organization and maintainability.
# See: models/gpt5_client.py, models/o3_client.py, models/claude_client.py

# ============================================================
# Initialize Components
# ============================================================

conversation_manager = ConversationManager()
prompt_config = PromptConfig()

# ============================================================
# API Routes
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for Claude Code to communicate with models

    Request body:
    {
        "model": "o3-pro" | "gpt-5" | "claude" | "claude-opus" | "grok" | "gemini",
        "prompt": "Your message here",
        "conversation_id": "optional-existing-conversation-id",
        "new_conversation": false,
        "include_clarification": true,
        "reasoning_effort": "high" | "medium" | "low" | "minimal",
        "file_paths": ["optional-file-paths-for-o3-pro-and-gemini"],
        "metadata": {}
    }

    Note: o3-pro and gemini always use maximum effort (high) for reasoning
    """
    try:
        data = request.json
        model = data.get('model', 'gpt-5')
        prompt = data.get('prompt', '')
        conv_id = data.get('conversation_id')
        new_conversation = data.get('new_conversation', False)
        include_clarification = data.get('include_clarification', True)
        reasoning_effort = data.get('reasoning_effort', 'high')
        metadata = data.get('metadata', {})

        # Add clarification prompt if requested
        if include_clarification:
            clarification_prompt = prompt_config.get_prompt('clarification')
            if clarification_prompt:
                prompt = f"{clarification_prompt}\n\n{prompt}"

        # Handle conversation management
        if new_conversation or not conv_id:
            conv_id = conversation_manager.create_conversation(model, metadata)
        elif not conversation_manager.get_conversation(conv_id):
            return jsonify({'error': 'Conversation not found'}), 404

        conversation = conversation_manager.get_conversation(conv_id)

        # Add user message
        conversation_manager.add_message(conv_id, 'user', prompt)

        # Get conversation history for context
        messages = conversation.messages

        # Call appropriate model
        if model == 'o3-pro':
            # O3-Pro uses maximum effort by default as requested
            file_paths = data.get('file_paths', [])  # Optional file paths for o3-pro
            response = call_o3_pro(messages, reasoning_effort='high', file_paths=file_paths)
        elif model.startswith('gpt'):
            response = call_gpt5(messages, reasoning_effort)
        elif model.startswith('claude'):
            # Map model names
            model_map = {
                'claude': 'claude-sonnet-4-5-20250929',
                'claude-opus': 'claude-opus-4.1-20250514',
            }
            claude_model = model_map.get(model, model)
            response = call_claude(messages, claude_model)
        elif model.startswith('grok'):
            # Route to Grok models
            response = call_grok(messages, model=model)
        elif model.startswith('gemini'):
            # Route to Gemini 2.5 Pro with MAXIMUM reasoning power and file support
            file_paths = data.get('file_paths', [])  # Optional file paths for gemini
            response = call_gemini(messages, file_paths=file_paths)
        else:
            return jsonify({'error': f'Unknown model: {model}'}), 400

        # Add assistant response
        conversation_manager.add_message(conv_id, 'assistant', response, model)

        return jsonify({
            'conversation_id': conv_id,
            'response': response,
            'model': model,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    """List all active conversations"""
    return jsonify(conversation_manager.list_conversations())

@app.route('/api/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    """Get a specific conversation with full history"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    return jsonify({
        'id': conversation.id,
        'model': conversation.model,
        'messages': [asdict(msg) for msg in conversation.messages],
        'created_at': conversation.created_at,
        'updated_at': conversation.updated_at,
        'metadata': conversation.metadata
    })

@app.route('/api/conversations/<conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    """Delete a conversation"""
    with conversation_manager.lock:
        if conv_id in conversation_manager.conversations:
            del conversation_manager.conversations[conv_id]
            return jsonify({'message': 'Conversation deleted'})
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        'models': [
            {'id': 'o3-pro', 'name': 'O3-Pro', 'provider': 'OpenAI', 'max_thinking': True, 'supports_files': True},
            {'id': 'gpt-5', 'name': 'GPT-5', 'provider': 'OpenAI', 'max_thinking': True},
            {'id': 'gpt-5-pro', 'name': 'GPT-5 Pro', 'provider': 'OpenAI', 'max_thinking': True},
            {'id': 'claude', 'name': 'Claude Sonnet 4.5', 'provider': 'Anthropic'},
            {'id': 'claude-opus', 'name': 'Claude Opus', 'provider': 'Anthropic'},
            {'id': 'claude-haiku', 'name': 'Claude Haiku', 'provider': 'Anthropic'},
            {'id': 'grok', 'name': 'Grok 4 Fast Reasoning', 'provider': 'xAI', 'max_thinking': True, 'context_window': 2000000},
            {'id': 'gemini', 'name': 'Gemini 2.5 Pro (Maximum Reasoning)', 'provider': 'Google', 'max_thinking': True, 'supports_files': True, 'thinking_budget': -1}
        ]
    })

# ============================================================
# Web Interface for Live Monitoring
# ============================================================

@app.route('/')
def index():
    """Serve the web interface for monitoring conversations"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Model Router - Live Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .status {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #666;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            height: calc(100vh - 200px);
        }
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow-y: auto;
        }
        .conversation-list {
            list-style: none;
        }
        .conversation-item {
            padding: 12px;
            margin-bottom: 8px;
            background: #f3f4f6;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .conversation-item:hover {
            background: #e5e7eb;
            transform: translateX(5px);
        }
        .conversation-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .conversation-item .model {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }
        .conversation-item .info {
            font-size: 12px;
            opacity: 0.7;
        }
        .chat-area {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f9fafb;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .message-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .message-role {
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            text-transform: uppercase;
        }
        .message-role.user {
            background: #dbeafe;
            color: #1e40af;
        }
        .message-role.assistant {
            background: #dcfce7;
            color: #166534;
        }
        .message-content {
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 3px solid;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .message.user .message-content {
            border-color: #3b82f6;
        }
        .message.assistant .message-content {
            border-color: #10b981;
        }
        .message-time {
            font-size: 12px;
            color: #9ca3af;
        }
        .test-area {
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
            margin-top: auto;
        }
        .test-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        select, input, button {
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }
        select {
            min-width: 120px;
        }
        input {
            flex: 1;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 20px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover {
            opacity: 0.9;
        }
        button:active {
            transform: scale(0.98);
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #9ca3af;
        }
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
    </style>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>[*] Model Router - Live Monitor</h1>
            <div class="status">
                <div class="status-item">
                    <div class="status-indicator"></div>
                    <span>Connected</span>
                </div>
                <div class="status-item">
                    <span id="conversation-count">0 conversations</span>
                </div>
                <div class="status-item">
                    <span id="message-count">0 messages</span>
                </div>
            </div>
        </div>

        <div class="main-grid">
            <div class="sidebar">
                <h3 style="margin-bottom: 15px; color: #667eea;">Conversations</h3>
                <ul class="conversation-list" id="conversation-list">
                    <li class="empty-state">No conversations yet</li>
                </ul>
            </div>

            <div class="chat-area">
                <div class="messages" id="messages">
                    <div class="empty-state">
                        <div class="empty-state-icon">💬</div>
                        <p>Select a conversation to view messages</p>
                    </div>
                </div>

                <div class="test-area">
                    <h4 style="margin-bottom: 10px; color: #667eea;">Test API</h4>
                    <div class="test-controls">
                        <select id="test-model">
                            <option value="o3-pro">O3-Pro (Max Effort)</option>
                            <option value="gpt-5">GPT-5</option>
                            <option value="gpt-5-pro">GPT-5 Pro</option>
                            <option value="claude">Claude Sonnet</option>
                            <option value="claude-opus">Claude Opus</option>
                            <option value="grok">Grok 4 Fast Reasoning</option>
                            <option value="gemini">Gemini 2.5 Pro (Maximum Reasoning)</option>
                        </select>
                        <input type="text" id="test-prompt" placeholder="Enter your test prompt..." />
                        <button onclick="sendTestMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let conversations = {};
        let activeConversationId = null;
        let totalMessages = 0;

        // Initialize
        loadConversations();

        // Socket listeners
        socket.on('new_message', (data) => {
            handleNewMessage(data);
        });

        async function loadConversations() {
            try {
                const response = await fetch('/api/conversations');
                const data = await response.json();
                updateConversationList(data);
            } catch (error) {
                console.error('Error loading conversations:', error);
            }
        }

        async function loadConversation(convId) {
            try {
                const response = await fetch(`/api/conversations/${convId}`);
                const data = await response.json();
                displayConversation(data);
                activeConversationId = convId;
                updateActiveConversation();
            } catch (error) {
                console.error('Error loading conversation:', error);
            }
        }

        function updateConversationList(convList) {
            const listEl = document.getElementById('conversation-list');

            if (convList.length === 0) {
                listEl.innerHTML = '<li class="empty-state">No conversations yet</li>';
                document.getElementById('conversation-count').textContent = '0 conversations';
                return;
            }

            listEl.innerHTML = '';
            convList.forEach(conv => {
                conversations[conv.id] = conv;
                const li = document.createElement('li');
                li.className = 'conversation-item';
                li.dataset.id = conv.id;
                li.onclick = () => loadConversation(conv.id);
                li.innerHTML = `
                    <div class="model">${conv.model.toUpperCase()}</div>
                    <div class="info">${conv.message_count} messages • ${formatTime(conv.updated_at)}</div>
                `;
                listEl.appendChild(li);
            });

            document.getElementById('conversation-count').textContent = `${convList.length} conversations`;
        }

        function displayConversation(conv) {
            const messagesEl = document.getElementById('messages');

            if (!conv.messages || conv.messages.length === 0) {
                messagesEl.innerHTML = '<div class="empty-state">No messages in this conversation</div>';
                return;
            }

            messagesEl.innerHTML = '';
            conv.messages.forEach(msg => {
                addMessageToDisplay(msg);
            });

            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function addMessageToDisplay(msg) {
            const messagesEl = document.getElementById('messages');
            const msgEl = document.createElement('div');
            msgEl.className = `message ${msg.role}`;
            msgEl.innerHTML = `
                <div class="message-header">
                    <span class="message-role ${msg.role}">${msg.role}</span>
                    ${msg.model ? `<span style="color: #9ca3af; font-size: 12px;">${msg.model}</span>` : ''}
                    <span class="message-time">${formatTime(msg.timestamp)}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
            `;
            messagesEl.appendChild(msgEl);
            totalMessages++;
            document.getElementById('message-count').textContent = `${totalMessages} messages`;
        }

        function handleNewMessage(data) {
            if (data.conversation_id === activeConversationId) {
                addMessageToDisplay(data.message);
                const messagesEl = document.getElementById('messages');
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            loadConversations(); // Refresh conversation list
        }

        function updateActiveConversation() {
            document.querySelectorAll('.conversation-item').forEach(el => {
                if (el.dataset.id === activeConversationId) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        }

        async function sendTestMessage() {
            const model = document.getElementById('test-model').value;
            const prompt = document.getElementById('test-prompt').value;

            if (!prompt) return;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: model,
                        prompt: prompt,
                        new_conversation: !activeConversationId
                    })
                });

                const data = await response.json();
                if (data.conversation_id) {
                    loadConversation(data.conversation_id);
                    loadConversations();
                }

                document.getElementById('test-prompt').value = '';
            } catch (error) {
                console.error('Error sending test message:', error);
                alert('Error sending message: ' + error.message);
            }
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = (now - date) / 1000;

            if (diff < 60) return 'just now';
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            return date.toLocaleDateString();
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Auto-refresh conversations every 5 seconds
        setInterval(loadConversations, 5000);
    </script>
</body>
</html>
    ''')

# ============================================================
# Main Entry Point
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[*] MODEL ROUTER API SERVER")
    print("="*60)
    print("\nEndpoints:")
    print("  - Web Interface: http://localhost:5000")
    print("  - API Base: http://localhost:5000/api")
    print("  - Chat: POST http://localhost:5000/api/chat")
    print("  - List Models: GET http://localhost:5000/api/models")
    print("  - Conversations: GET http://localhost:5000/api/conversations")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)