# Model Router - Multi-Model AI Communication System

## Overview
Model Router is a Flask-based API server that enables Claude Code to communicate with multiple AI models (GPT-5, Claude variants) through a unified interface. It includes conversation management, live monitoring, and XML-based prompt configuration.

## Features

### Core Capabilities
- **Multi-Model Support**: Communicate with GPT-5, Claude Sonnet, and Claude Opus
- **Conversation Management**: Start new conversations or continue existing ones with full history tracking
- **Live Web Monitor**: Real-time browser interface to watch all conversations as they happen
- **XML Prompt Configuration**: Customizable prompts that can be added to requests automatically
- **Clarification System**: Models can request clarification when prompts are ambiguous
- **Session Persistence**: Conversations are maintained for up to 20 days

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python model_router.py
```

The server will start on `http://localhost:5000`

### 3. Open the Web Monitor
Navigate to `http://localhost:5000` in your browser to see the live conversation monitor.

## API Usage

### Send a Message to a Model

```python
import requests

response = requests.post('http://localhost:5000/api/chat', json={
    'model': 'gpt-5',  # or 'claude', 'claude-opus'
    'prompt': 'Your question here',
    'new_conversation': True,  # Start fresh conversation
    'include_clarification': True,  # Add clarification prompt
    'reasoning_effort': 'high'  # For GPT-5: 'minimal', 'low', 'medium', 'high'
})

result = response.json()
print(f"Response: {result['response']}")
print(f"Conversation ID: {result['conversation_id']}")
```

### Continue a Conversation

```python
response = requests.post('http://localhost:5000/api/chat', json={
    'model': 'gpt-5',
    'prompt': 'Follow-up question',
    'conversation_id': 'previous-conversation-id'
})
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Send a message to a model |
| `/api/models` | GET | List available models |
| `/api/conversations` | GET | List all active conversations |
| `/api/conversations/<id>` | GET | Get full conversation history |
| `/api/conversations/<id>` | DELETE | Delete a conversation |

## Files Structure

```
Model_Router/
├── model_router.py           # Main Flask server
├── prompts.xml              # XML prompt configuration
├── claude_code_example.py   # Example usage script
├── test_client.py          # Test client with examples
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Configuration

### Environment Variables
The system uses API keys from your `.env` files:
- `OPENAI_API_KEY` - For GPT models
- `ANTHROPIC_API_KEY` - For Claude models

### XML Prompts
Edit `prompts.xml` to customize system prompts. Available prompts:
- `clarification` - Asks models to request clarification when needed
- `system` - General system behavior
- `thinking` - Encourages step-by-step reasoning
- `code_review` - For code analysis tasks
- `problem_solving` - For complex problems
- `documentation` - For writing documentation
- `debug` - For debugging assistance
- `creative` - For creative tasks

## Example Usage from Claude Code

```python
from claude_code_example import ask_model

# Ask GPT-5
result = ask_model(
    prompt="Explain quantum computing",
    model="gpt-5",
    new_conversation=True
)
print(result['response'])

# Ask Claude for comparison
result = ask_model(
    prompt="Explain quantum computing",
    model="claude",
    new_conversation=True
)
print(result['response'])

# Continue conversation
result = ask_model(
    prompt="Can you give an example?",
    model="claude",
    conversation_id=result['conversation_id']
)
print(result['response'])
```

## Testing

Run the test suite:
```bash
python test_client.py
```

This will test:
- Model availability
- GPT-5 communication
- Claude communication
- Conversation continuity
- Conversation listing

## Web Monitor Features

The live web interface at `http://localhost:5000` provides:
- Real-time conversation list
- Live message streaming
- Conversation history viewer
- Test panel for sending messages
- Model selection
- Active connection status

## Advanced Features

### Reasoning Effort (GPT-5)
Control the thinking depth:
- `minimal` - Fast, simple responses
- `low` - Quick reasoning
- `medium` - Balanced approach
- `high` - Maximum thinking power

### Conversation Metadata
Attach custom metadata to conversations:
```python
response = requests.post('http://localhost:5000/api/chat', json={
    'model': 'gpt-5',
    'prompt': 'Your question',
    'new_conversation': True,
    'metadata': {
        'project': 'my-project',
        'user': 'claude-code',
        'task': 'debugging'
    }
})
```

## Troubleshooting

### Server Won't Start
- Check that ports 5000 is not in use
- Verify API keys are set in `.env` files
- Ensure all dependencies are installed

### Models Not Responding
- Verify API keys are valid
- Check internet connection
- Ensure you have access to the specified models

### Web Interface Issues
- Clear browser cache
- Check browser console for errors
- Ensure JavaScript is enabled

## Notes

- Conversations are automatically cleaned up after 20 days
- The server runs in debug mode by default (auto-reload on code changes)
- All API responses include timestamps
- WebSocket support enables real-time updates

## Support

For issues or questions, check the server logs or modify the code as needed. The system is designed to be easily extensible for adding new models or features.