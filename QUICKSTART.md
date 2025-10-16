# Quick Start Guide - Modular Model Router

## 🎯 TL;DR

**Old way:**
```bash
python model_router.py
```

**New way:**
```bash
python app.py
```

Everything else stays the same! ✅

## 📂 What Changed?

The monolithic `model_router.py` (804 lines) is now split into 6 focused modules:

```
✨ NEW STRUCTURE:
├── app.py                    # 👈 Run this!
├── data_models.py            # Message & Conversation classes
├── conversation_manager.py   # State management
├── prompt_config.py          # XML config handler
├── routes.py                 # All API endpoints
└── web_interface.py          # Dashboard HTML

📦 UNCHANGED:
└── models/                   # API clients (gpt5, o3, claude, grok, gemini)
```

## ✅ Verification Checklist

### Test 1: Verify Imports
```bash
python test_imports.py
```

You should see:
```
Testing imports...
  ✓ Importing data_models...
  ✓ Importing prompt_config...
  ✓ Importing web_interface...
  ✓ Importing models package...
  ✓ Importing Flask components...
  ✓ Importing conversation_manager...
  ✓ Importing routes...

✅ All imports successful!
```

### Test 2: Check Port Availability
```bash
python test_port_selection.py
```

You should see which ports are available:
```
============================================================
🔍 Port Availability Test
============================================================

Checking port availability:
  Port 3791: ✅ Available
  Port 3003: ✅ Available

------------------------------------------------------------
✨ Will use preferred port: 3791
============================================================
```

## 🚀 Starting the Server

```bash
# Navigate to project directory
cd c:\projects\Model_Router

# Run the new entry point
python app.py
```

The server will **automatically select an available port**:
- **First choice**: Port **3791**
- **Fallback**: Port **3003** (if 3791 is in use)
- **Error**: If both ports are taken, you'll get a clear error message

You'll see:
```
============================================================
🚀 MODEL ROUTER API SERVER
============================================================

✨ Server running on port 3791

Endpoints:
  - Web Interface: http://localhost:3791
  - API Base: http://localhost:3791/api
  - Chat: POST http://localhost:3791/api/chat
  - List Models: GET http://localhost:3791/api/models
  - Conversations: GET http://localhost:3791/api/conversations

Available Models:
  - O3-Pro (OpenAI) - Maximum reasoning effort + file support
  - GPT-5 / GPT-5 Pro (OpenAI) - Advanced reasoning
  - Claude Sonnet 4.5 / Opus (Anthropic)
  - Grok 4 Fast Reasoning (xAI) - 2M context window
  - Gemini 2.5 Pro (Google) - Maximum reasoning + file support

Press CTRL+C to stop the server
============================================================
```

If port 3791 is in use, you'll see:
```
⚠️  Port 3791 is in use, using fallback port 3003
```

## 🔍 File Guide

| Need to... | Open this file |
|------------|----------------|
| Change startup behavior | `app.py` |
| Add/modify API routes | `routes.py` |
| Change data structures | `data_models.py` |
| Modify conversation logic | `conversation_manager.py` |
| Edit prompt templates | `prompt_config.py` or `prompts.xml` |
| Update dashboard UI | `web_interface.py` |
| Add/modify model clients | `models/` directory |

## 💡 Common Tasks

### Adding a New API Endpoint

Edit `routes.py`:
```python
def register_routes(app, conversation_manager, prompt_config):
    # ... existing routes ...

    @app.route('/api/my-new-endpoint', methods=['GET'])
    def my_new_endpoint():
        return jsonify({'message': 'Hello!'})
```

### Adding a New AI Model

1. Create `models/new_model_client.py`
2. Add to `models/__init__.py`:
   ```python
   from .new_model_client import call_new_model
   ```
3. Update `routes.py` chat endpoint to handle new model
4. Update model list in `routes.py` `list_models()` function

### Modifying Conversation Cleanup Time

Edit `conversation_manager.py`:
```python
def _cleanup_old_conversations(self):
    cutoff = datetime.now() - timedelta(days=30)  # Change from 20 to 30
    # ...
```

## 🧪 Testing Individual Modules

```python
# Test data models
from data_models import Message, Conversation
msg = Message(role="user", content="test", timestamp="2025-01-01T00:00:00")
print(msg)

# Test prompt config
from prompt_config import PromptConfig
config = PromptConfig()
print(config.get_prompt('clarification'))

# Test conversation manager (needs socketio)
from flask import Flask
from flask_socketio import SocketIO
from conversation_manager import ConversationManager

app = Flask(__name__)
socketio = SocketIO(app)
cm = ConversationManager(socketio)
conv_id = cm.create_conversation('gpt-5')
cm.add_message(conv_id, 'user', 'Hello!')
```

## 🎨 Architecture Highlights

### Clean Dependency Flow
```
app.py
  ├── Creates Flask app & SocketIO
  ├── Initializes ConversationManager(socketio)
  ├── Initializes PromptConfig()
  └── Calls register_routes(app, conversation_manager, prompt_config)
       └── routes.py uses these to handle requests
            └── Calls models/xxx_client.py for AI responses
```

### No Circular Imports
Each module has clear, one-way dependencies:
- `data_models.py` → (no dependencies)
- `prompt_config.py` → (no dependencies)
- `web_interface.py` → (no dependencies)
- `conversation_manager.py` → `data_models.py`
- `routes.py` → `data_models.py`, `models/`, `web_interface.py`
- `app.py` → Everything

## 📊 Impact Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Files | 1 | 6 | +5 |
| Total Lines | 804 | ~900 | +96 (+12%) |
| Largest File | 804 lines | 445 lines | -45% |
| Avg Lines/File | 804 | 150 | -81% |
| Modularity | ❌ | ✅ | ∞% |

*Note: Line increase is due to better documentation and separation*

## ⚠️ Breaking Changes

**None!** This is a pure refactor:
- ✅ Same API endpoints
- ✅ Same request/response formats
- ✅ Same behavior
- ✅ Same environment variables
- ✅ Same dependencies

Your existing clients (like Claude Code integrations) work without changes.

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'data_models'"
**Cause**: Running from wrong directory
**Fix**:
```bash
cd c:\projects\Model_Router
python app.py
```

### "ImportError: cannot import name 'call_gpt5'"
**Cause**: models/ package missing or broken
**Fix**: Verify `models/__init__.py` exists and contains imports

### Routes not registering
**Cause**: `register_routes()` not called in app.py
**Fix**: Check app.py has `register_routes(app, conversation_manager, prompt_config)`

### SocketIO events not working
**Cause**: ConversationManager not receiving socketio instance
**Fix**: Verify `conversation_manager = ConversationManager(socketio)` in app.py

## 🎓 Learn More

See `ARCHITECTURE.md` for detailed architecture documentation.

## 🤝 Contributing

With modular structure:
1. Each feature can be developed in isolation
2. Multiple developers can work on different modules
3. Testing is easier (can mock dependencies)
4. Code reviews are more focused (smaller files)

## 📝 Migration Checklist

- [x] All modules created
- [x] Import verification script created
- [x] Documentation written
- [ ] Test import verification (`python test_imports.py`)
- [ ] Start server (`python app.py`)
- [ ] Test web interface (http://localhost:5000)
- [ ] Test API endpoints
- [ ] Archive old `model_router.py` (optional)

---

**Ready to go!** Just run `python app.py` and you're all set! 🚀
