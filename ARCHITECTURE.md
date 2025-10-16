# Model Router - Modular Architecture

## 📁 Project Structure

```
Model_Router/
├── app.py                      # Main entry point - run this to start the server
├── data_models.py              # Core data structures (Message, Conversation)
├── conversation_manager.py     # Conversation state management
├── prompt_config.py            # XML-based prompt configuration
├── routes.py                   # All API route handlers
├── web_interface.py            # Live monitoring dashboard template
├── test_imports.py             # Import verification script
├── model_router.py             # ⚠️ LEGACY - can be archived/deleted
│
├── models/                     # AI model API clients (unchanged)
│   ├── __init__.py
│   ├── gpt5_client.py
│   ├── o3_client.py
│   ├── claude_client.py
│   ├── grok_client.py
│   └── gemini_client.py
│
├── .env                        # Environment variables
├── .env.gpt5                   # GPT-5 specific config
└── prompts.xml                 # Prompt templates (auto-created)
```

## 🚀 Running the Application

### Old Way (deprecated):
```bash
python model_router.py
```

### New Way:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## 📦 Module Breakdown

### **1. app.py** (Main Entry Point)
- **Purpose**: Application initialization and startup
- **Responsibilities**:
  - Create Flask app and SocketIO instances
  - Initialize CORS
  - Create ConversationManager and PromptConfig
  - Register all routes
  - Run the server
- **Lines**: ~55 lines

### **2. data_models.py** (Data Structures)
- **Purpose**: Core data models
- **Classes**:
  - `Message`: Single message in a conversation
  - `Conversation`: Full conversation with history
- **Dependencies**: Standard library only
- **Lines**: ~30 lines

### **3. conversation_manager.py** (State Management)
- **Purpose**: Thread-safe conversation management
- **Class**: `ConversationManager`
- **Key Features**:
  - Create/read/delete conversations
  - Add messages with real-time WebSocket emission
  - Auto-cleanup of conversations older than 20 days
  - Thread-safe operations with locks
- **Dependencies**:
  - `data_models.py` (Message, Conversation)
  - `flask_socketio` (for real-time updates)
- **Lines**: ~130 lines

### **4. prompt_config.py** (Configuration)
- **Purpose**: XML-based prompt template management
- **Class**: `PromptConfig`
- **Key Features**:
  - Load prompts from `prompts.xml`
  - Auto-create default config if missing
  - Runtime config reloading
- **Dependencies**: Standard library only
- **Lines**: ~75 lines

### **5. routes.py** (API Endpoints)
- **Purpose**: All Flask route handlers
- **Function**: `register_routes(app, conversation_manager, prompt_config)`
- **Routes**:
  - `GET /health` - Health check
  - `POST /api/chat` - Main chat endpoint
  - `GET /api/conversations` - List conversations
  - `GET /api/conversations/<id>` - Get conversation details
  - `DELETE /api/conversations/<id>` - Delete conversation
  - `GET /api/models` - List available models
  - `GET /` - Web monitoring interface
- **Dependencies**:
  - `models` package (for API clients)
  - `web_interface.py` (for HTML template)
  - Receives `conversation_manager` and `prompt_config` as parameters
- **Lines**: ~165 lines

### **6. web_interface.py** (Frontend)
- **Purpose**: Live monitoring dashboard
- **Function**: `get_index_template()` returns HTML string
- **Features**:
  - Real-time WebSocket updates
  - Conversation list sidebar
  - Message display
  - Test API interface
- **Dependencies**: None (pure HTML/JS/CSS)
- **Lines**: ~445 lines

### **7. Port Selection** (Smart Port Management)
- **Default Port**: 3791
- **Fallback Port**: 3003
- **Behavior**:
  - Tries port 3791 first
  - If 3791 is in use, falls back to 3003
  - If both are in use, exits with error message
  - Shows warning when using fallback port
- **Functions**:
  - `is_port_available(port)` - Checks if a port can be bound
  - `find_available_port(ports)` - Finds first available port from list

### **8. models/** (API Clients - Unchanged)
- **Purpose**: Individual AI model API clients
- **Modules**: GPT-5, O3-Pro, Claude, Grok, Gemini
- **Used by**: `routes.py`

## 🔄 Data Flow

```
User Request
    ↓
app.py (Flask app)
    ↓
routes.py (route handler)
    ↓
conversation_manager.py (manage state)
    ↓
models/xxx_client.py (call AI API)
    ↓
conversation_manager.py (save response)
    ↓
socketio (emit real-time update)
    ↓
web_interface.py (update dashboard)
```

## 🎯 Key Architecture Decisions

### 1. **Dependency Injection Pattern**
Instead of global state, we pass dependencies explicitly:
```python
# app.py creates instances
conversation_manager = ConversationManager(socketio)
prompt_config = PromptConfig()

# Routes receive them as parameters
register_routes(app, conversation_manager, prompt_config)
```

**Benefits**:
- ✅ Easy to test (can mock dependencies)
- ✅ Clear dependencies
- ✅ No circular imports
- ✅ Explicit over implicit

### 2. **SocketIO Integration**
The `ConversationManager` receives the `socketio` instance in its constructor:
```python
class ConversationManager:
    def __init__(self, socketio):
        self.socketio = socketio
```

**Benefits**:
- ✅ Real-time updates work seamlessly
- ✅ No global state needed
- ✅ Can mock socketio in tests

### 3. **Route Registration Function**
Instead of Flask Blueprints, we use a simple registration function:
```python
def register_routes(app, conversation_manager, prompt_config):
    @app.route('/api/chat', methods=['POST'])
    def chat():
        # Use conversation_manager and prompt_config here
        ...
```

**Benefits**:
- ✅ Simpler than Blueprints for this use case
- ✅ Direct access to dependencies via closure
- ✅ Easy to understand

### 4. **Separation of Concerns**
Each module has a single, clear responsibility:
- `app.py`: Initialization and wiring
- `data_models.py`: Data structures
- `conversation_manager.py`: State management
- `prompt_config.py`: Configuration
- `routes.py`: HTTP request handling
- `web_interface.py`: Frontend presentation
- `models/`: External API integration

## 🧪 Testing the New Structure

Run the import verification:
```bash
python test_imports.py
```

This will verify all modules import correctly without errors.

## 🔧 Migration Guide

### For Developers:

**Before** (monolithic):
```python
# Everything in model_router.py
python model_router.py
```

**After** (modular):
```python
# Run the new entry point
python app.py
```

### API Compatibility:
✅ **100% backward compatible** - all API endpoints remain the same:
- Same request/response formats
- Same URLs
- Same behavior
- Existing clients (like Claude Code) work without changes

### Environment Variables:
No changes needed - still uses `.env` and `.env.gpt5`

## 📊 Code Statistics

| Module | Lines | Responsibility |
|--------|-------|----------------|
| app.py | 55 | App initialization |
| data_models.py | 30 | Data structures |
| conversation_manager.py | 130 | State management |
| prompt_config.py | 75 | Configuration |
| routes.py | 165 | API handlers |
| web_interface.py | 445 | Frontend |
| **Total** | **900** | **(vs 804 original)** |

*Note: Slight increase due to better documentation, imports, and separation*

## 🎓 Benefits of This Architecture

1. **Maintainability**: Each file has a clear, single purpose
2. **Testability**: Can test each component independently
3. **Readability**: Easier to find and understand code
4. **Scalability**: Easy to add new models or features
5. **Collaboration**: Multiple developers can work on different modules
6. **Reusability**: Components can be reused in other projects
7. **Debugging**: Easier to trace issues to specific modules

## 🚨 Common Issues & Solutions

### Import Error: "No module named 'data_models'"
**Solution**: Make sure you're running from the project root:
```bash
cd c:\projects\Model_Router
python app.py
```

### Import Error: "No module named 'models'"
**Solution**: The `models/` package should exist with `__init__.py`

### SocketIO not emitting events
**Solution**: Make sure `ConversationManager` receives the socketio instance in app.py

## 🔮 Future Enhancements

Potential improvements with this architecture:

1. **Add unit tests**: Each module can be tested independently
2. **Add type hints**: Already partially done, can be expanded
3. **Add logging**: Easy to add module-specific loggers
4. **Configuration file**: Could add `config.py` for settings
5. **Database integration**: Replace in-memory storage in ConversationManager
6. **API versioning**: Easy to add v2 routes alongside v1
7. **Move HTML to template file**: Convert `web_interface.py` to use `templates/index.html`

## 📝 Notes

- The original `model_router.py` can be kept as a backup or deleted
- All existing functionality is preserved
- The `models/` package remains unchanged and works as before
- No changes needed to API client code or environment variables
