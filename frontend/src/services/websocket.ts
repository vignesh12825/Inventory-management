import { toast } from 'react-toastify';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private userId: number | null = null;

  connect(userId?: number) {
    this.userId = userId || null;
    const wsUrl = userId 
      ? `ws://localhost:8000/api/v1/ws/alerts/${userId}`
      : 'ws://localhost:8000/api/v1/ws/alerts';
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.log('Heartbeat message:', event.data);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }

  private handleMessage(data: any) {
    if (data.type === 'stock_alert') {
      this.handleStockAlert(data.data);
    }
  }

  private handleStockAlert(alertData: any) {
    const isResolved = alertData.status === 'resolved';
    const alertType = alertData.alert_type === 'low_stock' ? 'Low Stock Alert' : 'Out of Stock Alert';
    const message = `${alertType}: ${alertData.message}`;
    
    if (isResolved) {
      // Show success toast for resolved alerts
      toast.success(message, {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });

      // Dispatch custom event for resolved alerts
      const event = new CustomEvent('alertResolved', { detail: alertData });
      window.dispatchEvent(event);
    } else {
      // Show warning toast for new/active alerts
      toast.warning(message, {
        position: "top-right",
        autoClose: 10000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });

      // Dispatch custom event for new alerts
      const event = new CustomEvent('stockAlert', { detail: alertData });
      window.dispatchEvent(event);
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      
      setTimeout(() => {
        this.connect(this.userId || undefined);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    }
  }
}

export const websocketService = new WebSocketService(); 