#!/usr/bin/env python3
"""
Import Verification Script
===========================
Tests that all modules import correctly without errors.
"""

def test_imports():
    """Test all module imports"""
    print("Testing imports...")

    try:
        print("  ✓ Importing data_models...")
        from data_models import Message, Conversation

        print("  ✓ Importing prompt_config...")
        from prompt_config import PromptConfig

        print("  ✓ Importing web_interface...")
        from web_interface import get_index_template

        print("  ✓ Importing models package...")
        from models import call_gpt5, call_o3_pro, call_claude, call_grok, call_gemini

        print("  ✓ Importing Flask components...")
        from flask import Flask
        from flask_socketio import SocketIO

        print("  ✓ Importing conversation_manager...")
        # We'll create a mock socketio for testing
        app = Flask(__name__)
        socketio = SocketIO(app)
        from conversation_manager import ConversationManager
        cm = ConversationManager(socketio)

        print("  ✓ Importing routes...")
        from routes import register_routes

        print("\n✅ All imports successful!")
        print("\nModule structure:")
        print("  - data_models.py: Message, Conversation dataclasses")
        print("  - conversation_manager.py: ConversationManager class")
        print("  - prompt_config.py: PromptConfig class")
        print("  - web_interface.py: HTML template")
        print("  - routes.py: API route handlers")
        print("  - app.py: Main entry point")
        print("  - models/: API client package (gpt5, o3, claude, grok, gemini)")

        return True

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_imports()
    exit(0 if success else 1)
