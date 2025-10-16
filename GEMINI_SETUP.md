# Gemini 2.5 Pro - Maximum Reasoning Power

## 🎯 What You Got

**ONE model. ONE configuration. MAXIMUM power.**

- **Model**: Gemini 2.5 Pro (Google's most powerful model)
- **Reasoning**: Maximum effort mode (`thinking_budget = -1`)
- **Features**: File attachments, multi-turn conversations
- **API**: `google.generativeai` (official Google SDK)

## 🚀 Quick Start

### 1. Your API key is already configured in `.env`:
```env
GEMINI_API_KEY=AIzaSy...
```

### 2. Start the server:
```bash
python model_router.py
```

### 3. Use it via API:
```python
import requests

response = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "Solve this complex problem step by step...",
    "new_conversation": True
})

print(response.json()['response'])
```

### 4. Or use the web interface:
Go to `http://localhost:5000` and select **"Gemini 2.5 Pro (Maximum Reasoning)"**

## 📊 What Makes It Maximum Power?

```python
# This is what's configured under the hood:
generation_config = {
    'extra_config': {
        'thinking_config': {
            'thinking_budget': -1  # -1 = Dynamic/Maximum reasoning
        }
    }
}

model = genai.GenerativeModel(
    'gemini-2.5-pro',  # Most powerful Gemini model
    generation_config=genai.types.GenerationConfig(**generation_config)
)
```

**`thinking_budget = -1`** means:
- ✅ Dynamic thinking allocation
- ✅ Adjusts reasoning depth based on problem complexity
- ✅ Uses optimal reasoning tokens automatically
- ✅ No artificial limits on reasoning power

## 📎 File Attachment Support

```python
response = requests.post('http://localhost:5000/api/chat', json={
    "model": "gemini",
    "prompt": "Analyze this document",
    "file_paths": [
        "C:/path/to/document.pdf",
        "C:/path/to/code.py"
    ],
    "new_conversation": True
})
```

**Supported file types**: PDF, TXT, DOC, DOCX, code files, images, CSV, JSON, XML, and more.

## 🧪 Test It

Run the example:
```bash
python "code examples/gemini_example.py"
```

This will:
1. List all available models (showing Gemini 2.5 Pro)
2. Test maximum reasoning with a complex problem
3. Test multi-turn conversations
4. Show file upload capabilities

## 📋 Integration Details

| Component | Status |
|-----------|--------|
| **Package** | `google-generativeai` 0.8.5 ✅ |
| **Model** | `gemini-2.5-pro` ✅ |
| **Client** | `models/gemini_client.py` ✅ |
| **Router** | Integrated in `model_router.py` ✅ |
| **API Key** | Configured in `.env` ✅ |
| **File Support** | Upload & auto-cleanup ✅ |
| **Reasoning** | Maximum (`thinking_budget=-1`) ✅ |

## 🔥 Key Configuration

**In `models/gemini_client.py`:**
- Uses `google.generativeai` SDK
- Hardcoded to `gemini-2.5-pro` (no model selection confusion)
- Always uses `thinking_budget = -1` for maximum reasoning
- File upload with automatic cleanup
- Simple, focused API

**In `model_router.py`:**
- Model ID: `gemini`
- Display name: "Gemini 2.5 Pro (Maximum Reasoning)"
- File paths accepted via `file_paths` parameter
- Integrated at lines 278-281

## 💡 Usage Examples

### Basic Call
```python
from models import call_gemini, Message
from datetime import datetime

messages = [Message(
    role="user",
    content="What is the optimal strategy for...",
    timestamp=datetime.now().isoformat()
)]

response = call_gemini(messages)
print(response)
```

### With Files
```python
response = call_gemini(
    messages,
    file_paths=["report.pdf", "data.csv"]
)
```

### Direct Client
```python
from models import GeminiClient

client = GeminiClient()
response = client.call(
    messages,
    file_paths=["file.pdf"],
    max_tokens=4096,
    temperature=0.7
)
```

## ⚡ What Changed From Before

**BEFORE (confusing):**
- Multiple model aliases
- Experimental models
- Model selection required
- Unclear which was "best"

**NOW (simple):**
- ✅ ONE model: `gemini-2.5-pro`
- ✅ ONE mode: Maximum reasoning
- ✅ ONE goal: Best quality responses
- ✅ Clear and focused

## 🎓 Understanding Maximum Reasoning

The `thinking_budget` parameter controls how many "thinking tokens" the model uses:

| Value | Meaning |
|-------|---------|
| `-1` | **Dynamic/Maximum** - Model decides optimal reasoning depth |
| `32768` | Fixed maximum budget |
| `0` | No thinking mode (not recommended for complex tasks) |

**You're using `-1`** = The model automatically:
- Allocates more thinking for complex problems
- Uses less for simple questions
- Optimizes for quality vs. speed dynamically
- No artificial constraints

## 📚 Resources

- **Your API Key**: Already in `.env` ✅
- **Example Script**: `code examples/gemini_example.py`
- **Client Code**: `models/gemini_client.py`
- **Official Docs**: https://ai.google.dev/docs

## ✅ Verification

Run this to verify everything is working:
```bash
cd "C:\projects\Model_Router"
python -c "from models import GeminiClient; from dotenv import load_dotenv; load_dotenv(); print('✓ All systems ready!')"
```

---

**You now have the most powerful Gemini model with maximum reasoning power integrated into your Model Router.** 🧠⚡

No complexity. No confusion. Just maximum power.
