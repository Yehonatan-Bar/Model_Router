# Port Selection Logic

The Model Router now features **intelligent port selection** with automatic fallback.

## 🎯 Port Priority

```
┌─────────────────────────────────────────────┐
│         Start app.py                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Try Port 3791  │ ◄─── First Choice
         └────────┬───────┘
                  │
         ┌────────▼────────┐
         │   Available?    │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
        YES               NO
         │                 │
         ▼                 ▼
    ┌────────┐      ┌────────────────┐
    │ Use it │      │  Try Port 3003  │ ◄─── Fallback
    └────────┘      └────────┬───────┘
                              │
                     ┌────────▼────────┐
                     │   Available?    │
                     └────────┬────────┘
                              │
                     ┌────────┴────────┐
                     │                 │
                    YES               NO
                     │                 │
                     ▼                 ▼
                ┌────────┐      ┌──────────┐
                │ Use it │      │  ERROR   │
                │ (show  │      │  Exit    │
                │warning)│      │          │
                └────────┘      └──────────┘
```

## 📋 Port Configuration

| Priority | Port | Description |
|----------|------|-------------|
| **1st** | **3791** | Primary port (preferred) |
| **2nd** | **3003** | Fallback port (if 3791 is in use) |
| **N/A** | - | Error if both are taken |

## 💡 Example Scenarios

### Scenario 1: Normal Startup (Port 3791 Available)
```bash
$ python app.py

============================================================
🚀 MODEL ROUTER API SERVER
============================================================

✨ Server running on port 3791

Endpoints:
  - Web Interface: http://localhost:3791
  - API Base: http://localhost:3791/api
  ...
```

### Scenario 2: Fallback (Port 3791 In Use)
```bash
$ python app.py

⚠️  Port 3791 is in use, using fallback port 3003

============================================================
🚀 MODEL ROUTER API SERVER
============================================================

✨ Server running on port 3003

Endpoints:
  - Web Interface: http://localhost:3003
  - API Base: http://localhost:3003/api
  ...
```

### Scenario 3: All Ports Taken (Error)
```bash
$ python app.py

============================================================
❌ ERROR: All preferred ports are in use!
============================================================

Tried ports: 3791, 3003
Please free up one of these ports and try again.
============================================================
```

## 🔧 How It Works

### Code Implementation

```python
# app.py

def is_port_available(port):
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False


def find_available_port(preferred_ports):
    """Find the first available port from a list."""
    for port in preferred_ports:
        if is_port_available(port):
            return port
    return None


def main():
    # Try ports in order: 3791, then 3003
    preferred_ports = [3791, 3003]
    port = find_available_port(preferred_ports)

    if port is None:
        print("❌ ERROR: All preferred ports are in use!")
        return

    # Show warning if using fallback
    if port != preferred_ports[0]:
        print(f"⚠️  Port {preferred_ports[0]} is in use, using fallback port {port}")

    # Start server on selected port
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
```

## 🧪 Testing Port Selection

You can test the port selection logic without starting the server:

```bash
python test_port_selection.py
```

This will show you:
- Which ports are currently available
- Which port the server would use
- Whether fallback would be needed

Example output:
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

## 🛠️ Customizing Port Preferences

To change the port preferences, edit `app.py`:

```python
def main():
    # Modify these ports as needed
    preferred_ports = [3791, 3003]  # ← Change here
    port = find_available_port(preferred_ports)
    ...
```

You can add as many fallback ports as you want:
```python
preferred_ports = [3791, 3003, 8080, 8000]
```

## ⚡ Quick Reference

| What | Command |
|------|---------|
| **Start server** | `python app.py` |
| **Test ports** | `python test_port_selection.py` |
| **Check if port is in use** | `netstat -ano \| findstr :3791` (Windows) |
| **Check if port is in use** | `lsof -i :3791` (Linux/Mac) |
| **Kill process on port** | Find PID with above, then `kill <PID>` |

## 🎓 Design Benefits

1. **Zero Configuration**: Works out of the box, no config files needed
2. **Graceful Fallback**: Automatically handles port conflicts
3. **Clear Feedback**: Shows which port is being used and why
4. **Fail Fast**: Exits immediately if no ports are available (doesn't bind to random port)
5. **Predictable**: Always tries the same ports in the same order

## 🔍 Troubleshooting

### Both ports are in use, what do I do?

**Option 1**: Free up one of the ports
```bash
# Windows: Find what's using the port
netstat -ano | findstr :3791

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Option 2**: Add more fallback ports
Edit `app.py` and add more ports to the list:
```python
preferred_ports = [3791, 3003, 8080, 5000, 3000]
```

**Option 3**: Modify the preferred ports
Change the ports in `app.py` to ones you know are free:
```python
preferred_ports = [8888, 9999]
```

### How do I force a specific port?

Edit `app.py`:
```python
def main():
    # Force a specific port (no fallback)
    port = 3791
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
```

### Can I use a random available port?

Yes, but not recommended. You could modify to:
```python
import random

def find_random_available_port():
    """Find any available port"""
    for port in random.sample(range(3000, 9000), 100):
        if is_port_available(port):
            return port
    return None
```

But this makes it hard to know where your server is running!

---

**Note**: The intelligent port selection ensures your Model Router starts reliably without manual port configuration while maintaining predictability. 🚀
