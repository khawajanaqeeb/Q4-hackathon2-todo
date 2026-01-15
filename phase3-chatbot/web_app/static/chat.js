/**
 * Chat Interface JavaScript
 * Handles real-time communication with the Todo AI Chatbot
 */

class ChatInterface {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.inputField = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-btn');
        this.suggestions = document.querySelectorAll('.suggestion');

        // WebSocket connection
        this.ws = null;
        this.connectWebSocket();

        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Add event listeners to suggestions
        this.suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const text = suggestion.getAttribute('data-suggestion');
                this.inputField.value = text;
                this.sendMessage();
            });
        });

        // Add welcome message
        this.addBotMessage("Hello! I'm your Todo AI Assistant. You can ask me to add, list, complete, or delete tasks.");
    }

    connectWebSocket() {
        // Attempt to connect to WebSocket
        try {
            // In a real implementation, this would be dynamic based on the server
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('Connected to chat server');
                this.updateConnectionStatus('Connected', 'connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                switch(data.type) {
                    case 'response':
                        this.addBotMessage(data.message);
                        break;
                    case 'error':
                        this.addBotMessage(`Error: ${data.message}`);
                        break;
                    default:
                        this.addBotMessage(data.message);
                }
            };

            this.ws.onclose = () => {
                console.log('Disconnected from chat server');
                this.updateConnectionStatus('Disconnected', 'disconnected');

                // Attempt to reconnect after a delay
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('Error', 'error');
            };
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.updateConnectionStatus('Connection Failed', 'error');
        }
    }

    sendMessage() {
        const message = this.inputField.value.trim();

        if (!message) {
            return;
        }

        // Add user message to chat
        this.addUserMessage(message);

        // Clear input field
        this.inputField.value = '';

        // Send message via WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const userData = {
                user_id: this.getUserId(),
                message: message
            };

            this.ws.send(JSON.stringify(userData));
        } else {
            // Fallback to REST API if WebSocket is not available
            this.sendViaRestApi(message);
        }
    }

    sendViaRestApi(message) {
        // Show typing indicator
        this.addBotMessage('Thinking...', 'typing');

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: this.getUserId(),
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            this.removeLastTypingIndicator();

            if (data.success) {
                this.addBotMessage(data.response);
            } else {
                this.addBotMessage(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            // Remove typing indicator
            this.removeLastTypingIndicator();

            console.error('Error sending message:', error);
            this.addBotMessage(`Error: Could not process your request.`);
        });
    }

    addMessage(text, sender, className = '') {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`, className);

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(text)}</div>
            <div class="timestamp">${timestamp}</div>
        `;

        this.messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    addUserMessage(text) {
        this.addMessage(text, 'user');
    }

    addBotMessage(text) {
        this.addMessage(text, 'bot');
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.classList.add('message', 'bot-message', 'typing');

        typingDiv.innerHTML = `
            <div class="message-content">
                <span class="typing-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                </span>
            </div>
        `;

        this.messagesContainer.appendChild(typingDiv);

        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    removeLastTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateConnectionStatus(status, type) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `connection-status ${type}`;
        }
    }

    getUserId() {
        // In a real implementation, this would come from session/auth
        // For now, we'll generate a simple ID
        if (!localStorage.getItem('userId')) {
            localStorage.setItem('userId', Math.random().toString(36).substr(2, 9));
        }
        return localStorage.getItem('userId');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chat = new ChatInterface();
});