import { Message } from '@/types';

type WebSocketCallback = (data: any) => void;
type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

class WebSocketService {
  private ws: WebSocket | null = null;
  private callbacks: Map<string, WebSocketCallback[]> = new Map();
  private connectionStatus: ConnectionStatus = 'disconnected';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000; // 3 seconds
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private heartbeatTimeout: NodeJS.Timeout | null = null;
  private url: string;

  constructor() {
    // Use WebSocket URL from environment or default to localhost
    this.url = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.connectionStatus === 'connected') {
        resolve();
        return;
      }

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.connectionStatus = 'connected';
          this.reconnectAttempts = 0;
          this.setupHeartbeat();
          console.log('WebSocket connected');

          // Notify all listeners of connection
          this.callCallbacks('connect', {});
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            this.callCallbacks('error', { error: 'Invalid message format' });
          }
        };

        this.ws.onclose = (event) => {
          this.connectionStatus = 'disconnected';
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.callCallbacks('disconnect', { code: event.code, reason: event.reason });

          // Attempt to reconnect if not closed intentionally
          if (!event.wasClean) {
            this.attemptReconnect();
          }
        };

        this.ws.onerror = (error) => {
          this.connectionStatus = 'error';
          console.error('WebSocket error:', error);
          this.callCallbacks('error', { error });
        };
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
    this.connectionStatus = 'disconnected';
  }

  /**
   * Send a message to the WebSocket server
   */
  send(data: any): void {
    if (this.connectionStatus !== 'connected' || !this.ws) {
      console.error('WebSocket not connected, cannot send message');
      return;
    }

    try {
      this.ws.send(JSON.stringify(data));
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  /**
   * Subscribe to WebSocket events
   */
  subscribe(event: string, callback: WebSocketCallback): void {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)?.push(callback);
  }

  /**
   * Unsubscribe from WebSocket events
   */
  unsubscribe(event: string, callback: WebSocketCallback): void {
    if (this.callbacks.has(event)) {
      const callbacks = this.callbacks.get(event) || [];
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): ConnectionStatus {
    return this.connectionStatus;
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(data: any): void {
    // Reset heartbeat timeout on any message
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
    }

    // Call specific event handlers
    if (data.type) {
      this.callCallbacks(data.type, data);
    }

    // Call general message handler
    this.callCallbacks('message', data);
  }

  /**
   * Call all callbacks for a specific event
   */
  private callCallbacks(event: string, data: any): void {
    const callbacks = this.callbacks.get(event) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in ${event} callback:`, error);
      }
    });
  }

  /**
   * Attempt to reconnect to WebSocket server
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
          this.attemptReconnect(); // Try again
        });
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      this.callCallbacks('reconnect_failed', {});
    }
  }

  /**
   * Set up heartbeat mechanism to detect broken connections
   */
  private setupHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    // Send ping every 30 seconds
    this.heartbeatInterval = setInterval(() => {
      if (this.connectionStatus === 'connected') {
        this.send({ type: 'ping' });

        // Set timeout to expect pong back
        this.heartbeatTimeout = setTimeout(() => {
          console.log('Heartbeat timeout, closing connection');
          if (this.ws) {
            this.ws.close(1006, 'Heartbeat timeout');
          }
        }, 5000); // 5 seconds timeout
      }
    }, 30000); // 30 seconds
  }
}

export default new WebSocketService();