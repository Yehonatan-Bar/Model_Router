# Model Router

Flask API providing unified access to **O3-Pro**, **Gemini 2.5 Pro**, **Grok 4**, **GPT-5**, and **Claude** with intelligent routing, conversation management, and live monitoring.

## Features

- **7 AI Models**: O3-Pro, Gemini 2.5 Pro, Grok 4, GPT-5, Claude Sonnet/Opus/Haiku
- **File Analysis**: PDF/code analysis (O3-Pro & Gemini)
- **Massive Context**: 2M tokens with Grok
- **Maximum Reasoning**: O3-Pro (fixed) & Gemini (adaptive)
- **Live Web Monitor**: Real-time conversation tracking
- **Persistent Conversations**: 20-day history retention

## Model Capabilities

| Model | Capability | Context | Files | Use Case |
|-------|-----------|---------|-------|----------|
| **O3-Pro** | Max reasoning (fixed) | Standard | ✅ | Complex algorithms, deep analysis |
| **Gemini 2.5 Pro** | Max reasoning (adaptive) | Standard | ✅ | Multi-modal, dynamic complexity |
| **Grok 4** | 2M token context | 2M tokens | ❌ | Entire codebases, massive docs |
| **GPT-5** | Adjustable reasoning | Standard | ❌ | General-purpose, speed control |
| **Claude Sonnet/Opus** | Creative & nuanced | Standard | ❌ | Writing, creative tasks |

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=...

# Run
python model_router.py

# Monitor: http://localhost:5000
```

## API Usage

### Basic Request
```python
import requests

r = requests.post('http://localhost:5000/api/chat', json={
    'model': 'o3-pro',  # or 'gemini', 'grok', 'gpt-5', 'claude'
    'prompt': 'Your question',
    'new_conversation': True
}).json()

print(r['response'])
```

### File Analysis
```python
# O3-Pro (fixed max) or Gemini (adaptive max)
requests.post('http://localhost:5000/api/chat', json={
    'model': 'gemini',
    'prompt': 'Analyze these files',
    'file_paths': ['doc.pdf', 'code.py']
})
```

### Massive Context (Grok 2M)
```python
with open('codebase.txt', 'r') as f:
    code = f.read()

requests.post('http://localhost:5000/api/chat', json={
    'model': 'grok',
    'prompt': f'{code}\n\nFind vulnerabilities'
})
```

### Compare Models
```python
for model in ['o3-pro', 'gemini', 'grok']:
    r = requests.post('http://localhost:5000/api/chat', json={
        'model': model, 'prompt': 'Question', 'new_conversation': True
    }).json()
    print(f"{model}: {r['response']}")
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message to model |
| `/api/models` | GET | List models |
| `/api/conversations` | GET | List conversations |
| `/api/conversations/<id>` | GET/DELETE | Get or delete conversation |

## Structure

```
Model_Router/
├── model_router.py       # Flask server
├── models/               # Model clients
│   ├── gpt5_client.py
│   ├── o3_client.py
│   ├── claude_client.py
│   ├── grok_client.py
│   └── gemini_client.py
├── prompts.xml           # Prompt config
├── requirements.txt
└── README.md
```

## Model Selection

**Decision Flow:**
1. File analysis (PDF/code) → `o3-pro` or `gemini`
2. Large context (>100K tokens) → `grok`
3. Maximum reasoning → `o3-pro` (fixed) or `gemini` (adaptive)
4. Speed control → `gpt-5` with `reasoning_effort`
5. Creative tasks → `claude`

**Examples:**
```python
# Deep code review
requests.post('http://localhost:5000/api/chat', json={
    'model': 'o3-pro',
    'prompt': 'Security audit',
    'file_paths': ['app.py', 'auth.py']
})

# Massive context
requests.post('http://localhost:5000/api/chat', json={
    'model': 'grok',
    'prompt': f'{entire_docs}\nFind inconsistencies'
})

# Adaptive reasoning
requests.post('http://localhost:5000/api/chat', json={
    'model': 'gemini',
    'prompt': 'Architecture analysis',
    'file_paths': ['design.pdf']
})
```

## Configuration

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...        # O3-Pro, GPT-5
ANTHROPIC_API_KEY=sk-ant-... # Claude
XAI_API_KEY=xai-...          # Grok
GOOGLE_API_KEY=...           # Gemini
```

**Customize Prompts:** Edit `prompts.xml` for system behavior

## Key Features

**Reasoning Control:**
- O3-Pro: Fixed maximum (non-adjustable)
- Gemini: Adaptive (scales to complexity)
- GPT-5: Manual (`minimal`|`low`|`medium`|`high`)
- Grok: Fast with 2M context

**File Support:** O3-Pro & Gemini only (PDF, code, text)

**Persistence:** Conversations auto-saved 20 days

## Troubleshooting

```bash
# Verify setup
curl http://localhost:5000/api/models

# Check keys
echo $OPENAI_API_KEY $ANTHROPIC_API_KEY $XAI_API_KEY $GOOGLE_API_KEY
```

## Best Practices

- **Provide full context**: Include complete error traces, code structure, dependencies
- **Choose right model**: O3-Pro/Gemini for deep reasoning, Grok for massive context, GPT-5 for speed control
- **Use absolute paths** for file analysis
- **Leverage file_paths** for PDFs/code (O3-Pro, Gemini)

---

**Model Router** - Multi-model AI access for Claude Code 🚀