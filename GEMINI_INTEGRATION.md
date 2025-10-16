# Gemini 2.0 Flash Thinking Integration

## Overview

The Gemini integration adds Google's Gemini 2.0 Flash Thinking experimental model to the Model Router, providing advanced reasoning capabilities with file attachment support.

## ✨ Key Features

- **🧠 Maximum Reasoning Power**: Uses Gemini 2.0 Flash Thinking experimental model for deep analytical tasks
- **📎 File Attachment Support**: Upload and analyze PDFs, code files, images, and more
- **💬 Multi-turn Conversations**: Full conversation history support
- **🔄 Automatic File Cleanup**: Uploaded files are automatically cleaned up after processing
- **⚡ Modern API**: Uses the latest `google-genai` 1.45.0 SDK

## 🚀 Quick Start

### 1. Installation

The required package is already added to `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Your `GEMINI_API_KEY` is already configured in the `.env` file:

```env
GEMINI_API_KEY=AIzaSy...
```

### 3. Start the Server

```bash
python model_router.py
```

The server will start on `http://localhost:5000`

### 4. Test the Integration

Run the example script:

```bash
python "code examples/gemini_example.py"
```

## 📝 API Usage

### Basic Request

```python
import requests

response = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "Analyze the following complex problem step by step...",
    "new_conversation": True
})

print(response.json()['response'])
```

### With File Attachments

```python
response = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "Please analyze this document and provide insights",
    "file_paths": [
        "C:/path/to/document.pdf",
        "C:/path/to/code.py"
    ],
    "new_conversation": True
})
```

### Multi-turn Conversation

```python
# First message
response1 = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "Explain quantum computing",
    "new_conversation": True
})

conversation_id = response1.json()['conversation_id']

# Follow-up message
response2 = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "How does it differ from classical computing?",
    "conversation_id": conversation_id,
    "new_conversation": False
})
```

## 🎯 Available Models

The integration supports multiple model aliases:

| Alias | Actual Model | Description |
|-------|-------------|-------------|
| `gemini` | `gemini-2.0-flash-thinking-exp` | Default (recommended) |
| `gemini-2.5` | `gemini-2.0-flash-thinking-exp` | Alias for compatibility |
| `gemini-2.5-pro` | `gemini-2.0-flash-thinking-exp` | Pro alias |
| `gemini-pro` | `gemini-2.0-flash-thinking-exp` | Generic pro alias |
| `gemini-thinking` | `gemini-2.0-flash-thinking-exp` | Explicit thinking mode |

## 📋 Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `"gemini"` | Model to use (see aliases above) |
| `prompt` | string | **required** | User's message/question |
| `file_paths` | array | `[]` | List of file paths to upload |
| `conversation_id` | string | `null` | ID for continuing conversation |
| `new_conversation` | boolean | `false` | Start a new conversation |
| `include_clarification` | boolean | `true` | Include clarification prompt |
| `metadata` | object | `{}` | Custom metadata |

## 📂 Supported File Types

Gemini supports a wide range of file formats:

- **Documents**: PDF, TXT, DOC, DOCX
- **Code**: PY, JS, TS, JAVA, CPP, etc.
- **Images**: JPG, PNG, GIF, WEBP
- **Data**: CSV, JSON, XML
- **And many more**

Files are automatically:
- Uploaded to Google's servers
- Analyzed with maximum reasoning
- Cleaned up after processing

## 🔧 Architecture

### File Structure

```
Model_Router/
├── models/
│   ├── gemini_client.py      # Gemini client implementation
│   └── __init__.py            # Exports GeminiClient
├── model_router.py            # Main server (includes Gemini routes)
├── code examples/
│   └── gemini_example.py      # Usage examples
├── requirements.txt           # Includes google-genai
└── .env                       # Contains GEMINI_API_KEY
```

### Integration Points

1. **models/gemini_client.py**: Core client using `google.genai` SDK
2. **model_router.py line 25**: Import statement
3. **model_router.py line 278-281**: Request handling
4. **model_router.py line 340**: Model listing
5. **model_router.py line 609**: Web UI dropdown

## 🎨 Web Interface

The Gemini model is available in the live monitoring interface at `http://localhost:5000`:

1. Select "Gemini 2.0 Flash Thinking (Max Reasoning)" from the dropdown
2. Enter your prompt
3. Click "Send"
4. Watch the conversation in real-time

## 🧪 Testing

### Manual Test

```bash
# Test API availability
curl http://localhost:5000/api/models | jq '.models[] | select(.provider=="Google")'

# Test basic call
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini",
    "prompt": "What is 2+2? Think step by step.",
    "new_conversation": true
  }'
```

### Run Example Script

```bash
python "code examples/gemini_example.py"
```

This will:
1. List available models
2. Test basic reasoning
3. Test multi-turn conversations
4. Show file upload example (optional)

## ⚙️ Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (handled by client)
GEMINI_DEFAULT_MODEL=gemini-2.0-flash-thinking-exp
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=1.0
```

### Client Initialization

```python
from models import GeminiClient

# With environment variable
client = GeminiClient()

# With explicit API key
client = GeminiClient(api_key="your_key")
```

## 🔍 Advanced Usage

### Direct Client Usage

```python
from models.gemini_client import GeminiClient, Message
from datetime import datetime

client = GeminiClient()

messages = [
    Message(
        role="user",
        content="Solve this complex problem...",
        timestamp=datetime.now().isoformat()
    )
]

response = client.call(
    messages=messages,
    model="gemini-thinking",
    file_paths=["path/to/file.pdf"],
    max_tokens=4096,
    temperature=0.7
)

print(response)
```

### Custom Configuration

```python
response = client.call(
    messages=messages,
    model="gemini-2.0-flash-thinking-exp",
    thinking_budget=-1,  # Dynamic thinking
    max_tokens=8192,
    temperature=1.0
)
```

## 📊 Model Capabilities

### What Gemini Excels At

- ✅ Complex reasoning and problem-solving
- ✅ Multi-step analysis and planning
- ✅ Document analysis and summarization
- ✅ Code review and optimization
- ✅ Mathematical and logical reasoning
- ✅ Multi-modal understanding (text + files)

### Thinking Mode

The experimental thinking model:
- Shows its reasoning process
- Breaks down complex problems
- Provides step-by-step analysis
- Self-corrects during reasoning

## 🐛 Troubleshooting

### Import Error

**Error**: `ModuleNotFoundError: No module named 'google.genai'`

**Solution**:
```bash
pip install google-genai --upgrade
```

### API Key Error

**Error**: `ValueError: Google API key not provided`

**Solution**: Check your `.env` file:
```bash
# Verify key is set
grep GEMINI_API_KEY .env

# Reload environment
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

### File Upload Error

**Error**: `Failed to upload file`

**Solutions**:
- Check file path is absolute
- Verify file exists
- Ensure file size < 50MB
- Check file type is supported

### Response Parsing Error

**Error**: `No response generated`

**Solution**: This usually means the API returned an unexpected format. Check:
- API key is valid
- Model name is correct
- No rate limiting issues

## 📚 Resources

- **Google AI Studio**: https://aistudio.google.com/
- **API Documentation**: https://ai.google.dev/docs
- **Python SDK**: https://pypi.org/project/google-genai/
- **Model Router Docs**: See README.md

## 🆕 What's New

### Version 1.0 (Current)

- ✅ Modern `google-genai` 1.45.0 SDK
- ✅ Gemini 2.0 Flash Thinking experimental model
- ✅ File attachment support
- ✅ Multi-turn conversations
- ✅ Automatic file cleanup
- ✅ Web UI integration
- ✅ Comprehensive error handling

## 🤝 Contributing

To enhance the Gemini integration:

1. Update `models/gemini_client.py` for client changes
2. Modify `model_router.py` for routing changes
3. Add examples to `code examples/`
4. Update this documentation

## 📄 License

Same as Model Router project license.

---

**Happy reasoning with Gemini! 🧠✨**

For support, check the main README.md or open an issue.
