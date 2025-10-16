#!/usr/bin/env python3
"""
Model Router API Server
=======================
Flask server that enables Claude Code to communicate with multiple AI models
with conversation management, live monitoring, and XML configuration.

This is the main entry point that initializes and runs the application.
"""

import socket
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

from conversation_manager import ConversationManager
from prompt_config import PromptConfig
from routes import register_routes

# Load environment variables
load_dotenv()
load_dotenv('.env.gpt5')

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")  # Allow Claude Code to access from any origin

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize core components
conversation_manager = ConversationManager(socketio)
prompt_config = PromptConfig()

# Register all routes
register_routes(app, conversation_manager, prompt_config)


def is_port_available(port):
    """
    Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False


def find_available_port(preferred_ports):
    """
    Find the first available port from a list of preferred ports.

    Args:
        preferred_ports: List of port numbers to try in order

    Returns:
        First available port number, or None if all are taken
    """
    for port in preferred_ports:
        if is_port_available(port):
            return port
    return None


def main():
    """Main entry point for the application"""
    # Try ports in order: 3791, then 3003
    preferred_ports = [3791, 3003]
    port = find_available_port(preferred_ports)

    if port is None:
        print("\n" + "="*60)
        print("❌ ERROR: All preferred ports are in use!")
        print("="*60)
        print(f"\nTried ports: {', '.join(map(str, preferred_ports))}")
        print("Please free up one of these ports and try again.")
        print("="*60 + "\n")
        return

    # Show which port we're using
    if port != preferred_ports[0]:
        print(f"\n⚠️  Port {preferred_ports[0]} is in use, using fallback port {port}\n")

    print("\n" + "="*60)
    print("🚀 MODEL ROUTER API SERVER")
    print("="*60)
    print(f"\n✨ Server running on port {port}")
    print("\nEndpoints:")
    print(f"  - Web Interface: http://localhost:{port}")
    print(f"  - API Base: http://localhost:{port}/api")
    print(f"  - Chat: POST http://localhost:{port}/api/chat")
    print(f"  - List Models: GET http://localhost:{port}/api/models")
    print(f"  - Conversations: GET http://localhost:{port}/api/conversations")
    print("\nAvailable Models:")
    print("  - O3-Pro (OpenAI) - Maximum reasoning effort + file support")
    print("  - GPT-5 / GPT-5 Pro (OpenAI) - Advanced reasoning")
    print("  - Claude Sonnet 4.5 / Opus (Anthropic)")
    print("  - Grok 4 Fast Reasoning (xAI) - 2M context window")
    print("  - Gemini 2.5 Pro (Google) - Maximum reasoning + file support")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")

    socketio.run(app, host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
