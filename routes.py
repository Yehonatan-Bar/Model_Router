"""
API Routes
==========
All Flask route handlers for the Model Router API.
"""

from datetime import datetime
from dataclasses import asdict
from flask import request, jsonify, render_template_string

# Import model client functions from the models package
from models import call_gpt5, call_o3_pro, call_claude, call_grok, call_gemini
from web_interface import get_index_template


def register_routes(app, conversation_manager, prompt_config):
    """
    Register all API routes with the Flask app.

    Args:
        app: Flask application instance
        conversation_manager: ConversationManager instance
        prompt_config: PromptConfig instance
    """

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
                    'claude-opus': 'claude-opus-4-1-20250805',
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
        if conversation_manager.delete_conversation(conv_id):
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

    @app.route('/')
    def index():
        """Serve the web interface for monitoring conversations"""
        return render_template_string(get_index_template())
