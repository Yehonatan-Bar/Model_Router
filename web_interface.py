"""
Web Interface Template
======================
HTML template for the live monitoring dashboard.
"""


def get_index_template() -> str:
    """
    Returns the HTML template for the web monitoring interface.

    Returns:
        HTML template string
    """
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Model Router - Live Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .status {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #666;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            height: calc(100vh - 200px);
        }
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow-y: auto;
        }
        .conversation-list {
            list-style: none;
        }
        .conversation-item {
            padding: 12px;
            margin-bottom: 8px;
            background: #f3f4f6;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .conversation-item:hover {
            background: #e5e7eb;
            transform: translateX(5px);
        }
        .conversation-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .conversation-item .model {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }
        .conversation-item .info {
            font-size: 12px;
            opacity: 0.7;
        }
        .chat-area {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f9fafb;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .message-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .message-role {
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            text-transform: uppercase;
        }
        .message-role.user {
            background: #dbeafe;
            color: #1e40af;
        }
        .message-role.assistant {
            background: #dcfce7;
            color: #166534;
        }
        .message-content {
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 3px solid;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .message.user .message-content {
            border-color: #3b82f6;
        }
        .message.assistant .message-content {
            border-color: #10b981;
        }
        .message-time {
            font-size: 12px;
            color: #9ca3af;
        }
        .test-area {
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
            margin-top: auto;
        }
        .test-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        select, input, button {
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }
        select {
            min-width: 120px;
        }
        input {
            flex: 1;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 20px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover {
            opacity: 0.9;
        }
        button:active {
            transform: scale(0.98);
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #9ca3af;
        }
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
    </style>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Model Router - Live Monitor</h1>
            <div class="status">
                <div class="status-item">
                    <div class="status-indicator"></div>
                    <span>Connected</span>
                </div>
                <div class="status-item">
                    <span id="conversation-count">0 conversations</span>
                </div>
                <div class="status-item">
                    <span id="message-count">0 messages</span>
                </div>
            </div>
        </div>

        <div class="main-grid">
            <div class="sidebar">
                <h3 style="margin-bottom: 15px; color: #667eea;">Conversations</h3>
                <ul class="conversation-list" id="conversation-list">
                    <li class="empty-state">No conversations yet</li>
                </ul>
            </div>

            <div class="chat-area">
                <div class="messages" id="messages">
                    <div class="empty-state">
                        <div class="empty-state-icon">💬</div>
                        <p>Select a conversation to view messages</p>
                    </div>
                </div>

                <div class="test-area">
                    <h4 style="margin-bottom: 10px; color: #667eea;">Test API</h4>
                    <div class="test-controls">
                        <select id="test-model">
                            <option value="o3-pro">O3-Pro (Max Effort)</option>
                            <option value="gpt-5">GPT-5</option>
                            <option value="gpt-5-pro">GPT-5 Pro</option>
                            <option value="claude">Claude Sonnet</option>
                            <option value="claude-opus">Claude Opus</option>
                            <option value="grok">Grok 4 Fast Reasoning</option>
                            <option value="gemini">Gemini 2.5 Pro (Maximum Reasoning)</option>
                        </select>
                        <input type="text" id="test-prompt" placeholder="Enter your test prompt..." />
                        <button onclick="sendTestMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let conversations = {};
        let activeConversationId = null;
        let totalMessages = 0;

        // Initialize
        loadConversations();

        // Socket listeners
        socket.on('new_message', (data) => {
            handleNewMessage(data);
        });

        async function loadConversations() {
            try {
                const response = await fetch('/api/conversations');
                const data = await response.json();
                updateConversationList(data);
            } catch (error) {
                console.error('Error loading conversations:', error);
            }
        }

        async function loadConversation(convId) {
            try {
                const response = await fetch(`/api/conversations/${convId}`);
                const data = await response.json();
                displayConversation(data);
                activeConversationId = convId;
                updateActiveConversation();
            } catch (error) {
                console.error('Error loading conversation:', error);
            }
        }

        function updateConversationList(convList) {
            const listEl = document.getElementById('conversation-list');

            if (convList.length === 0) {
                listEl.innerHTML = '<li class="empty-state">No conversations yet</li>';
                document.getElementById('conversation-count').textContent = '0 conversations';
                return;
            }

            listEl.innerHTML = '';
            convList.forEach(conv => {
                conversations[conv.id] = conv;
                const li = document.createElement('li');
                li.className = 'conversation-item';
                li.dataset.id = conv.id;
                li.onclick = () => loadConversation(conv.id);
                li.innerHTML = `
                    <div class="model">${conv.model.toUpperCase()}</div>
                    <div class="info">${conv.message_count} messages • ${formatTime(conv.updated_at)}</div>
                `;
                listEl.appendChild(li);
            });

            document.getElementById('conversation-count').textContent = `${convList.length} conversations`;
        }

        function displayConversation(conv) {
            const messagesEl = document.getElementById('messages');

            if (!conv.messages || conv.messages.length === 0) {
                messagesEl.innerHTML = '<div class="empty-state">No messages in this conversation</div>';
                return;
            }

            messagesEl.innerHTML = '';
            conv.messages.forEach(msg => {
                addMessageToDisplay(msg);
            });

            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function addMessageToDisplay(msg) {
            const messagesEl = document.getElementById('messages');
            const msgEl = document.createElement('div');
            msgEl.className = `message ${msg.role}`;
            msgEl.innerHTML = `
                <div class="message-header">
                    <span class="message-role ${msg.role}">${msg.role}</span>
                    ${msg.model ? `<span style="color: #9ca3af; font-size: 12px;">${msg.model}</span>` : ''}
                    <span class="message-time">${formatTime(msg.timestamp)}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
            `;
            messagesEl.appendChild(msgEl);
            totalMessages++;
            document.getElementById('message-count').textContent = `${totalMessages} messages`;
        }

        function handleNewMessage(data) {
            if (data.conversation_id === activeConversationId) {
                addMessageToDisplay(data.message);
                const messagesEl = document.getElementById('messages');
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            loadConversations(); // Refresh conversation list
        }

        function updateActiveConversation() {
            document.querySelectorAll('.conversation-item').forEach(el => {
                if (el.dataset.id === activeConversationId) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        }

        async function sendTestMessage() {
            const model = document.getElementById('test-model').value;
            const prompt = document.getElementById('test-prompt').value;

            if (!prompt) return;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: model,
                        prompt: prompt,
                        new_conversation: !activeConversationId
                    })
                });

                const data = await response.json();
                if (data.conversation_id) {
                    loadConversation(data.conversation_id);
                    loadConversations();
                }

                document.getElementById('test-prompt').value = '';
            } catch (error) {
                console.error('Error sending test message:', error);
                alert('Error sending message: ' + error.message);
            }
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = (now - date) / 1000;

            if (diff < 60) return 'just now';
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            return date.toLocaleDateString();
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Auto-refresh conversations every 5 seconds
        setInterval(loadConversations, 5000);
    </script>
</body>
</html>
    '''
