# 🔧 Technical Documentation

## System Architecture

### Overview
The Inventory Management System is built using a modern microservices architecture with:
- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React with TypeScript
- **Real-time Communication**: WebSocket for instant notifications
- **Background Processing**: Automated stock monitoring

### Data Flow
```
User Action → Frontend → API → Backend → Database
                ↓
            WebSocket ← Background Task ← Stock Monitoring
```

## Backend Architecture

### Core Components

#### 1. Background Task Manager (`app/core/background_tasks.py`)
```python
class BackgroundTaskManager:
    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # 60 seconds
        self.task: Optional[asyncio.Task] = None
```

**Key Features:**
- Runs every 60 seconds to check stock levels
- Creates alerts for low stock conditions
- Auto-resolves alerts when stock improves
- Prevents re-triggering of resolved alerts

**Alert Logic:**
```python
# Low Stock Alert
if item.available_quantity <= rule.threshold_quantity:
    should_alert = True

# Out of Stock Alert  
if item.available_quantity <= 0:
    should_alert = True

# Auto-resolution
if existing_alert and stock_improved:
    existing_alert.status = AlertStatus.RESOLVED
```

#### 2. WebSocket Manager (`app/core/websocket.py`)
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}
```

**Features:**
- Manages active WebSocket connections
- Broadcasts alerts to all connected clients
- User-specific notifications
- Automatic connection cleanup

#### 3. Database Models

**Stock Alert Model:**
```python
class StockAlert(Base):
    __tablename__ = "stock_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    alert_type = Column(Enum(AlertType))
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    current_quantity = Column(Integer)
    threshold_quantity = Column(Integer)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
```

**Alert Status Flow:**
```
ACTIVE → ACKNOWLEDGED → RESOLVED
   ↓
DISMISSED
```

### API Endpoints

#### Stock Alerts
```python
@router.get("/alerts/active")
async def get_active_alerts():
    """Get all active stock alerts"""

@router.post("/check-alerts") 
async def check_alerts():
    """Manually trigger alert check"""

@router.get("/background-task/status")
async def get_background_task_status():
    """Get background task status"""

@router.post("/background-task/trigger")
async def trigger_immediate_check():
    """Trigger immediate stock check"""
```

#### WebSocket Endpoints
```python
@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """General alerts WebSocket"""

@router.websocket("/ws/alerts/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: int):
    """User-specific alerts WebSocket"""
```

## Frontend Architecture

### State Management

#### 1. Notification Context (`src/contexts/NotificationContext.tsx`)
```typescript
interface NotificationContextType {
  activeAlertsCount: number;
  unreadAlertsCount: number;
  refreshAlerts: () => void;
}
```

**Features:**
- Real-time alert count updates
- WebSocket event listeners
- Automatic data refresh
- Global state management

#### 2. WebSocket Service (`src/services/websocket.ts`)
```typescript
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
}
```

**Event Handling:**
```typescript
private handleStockAlert(alertData: any) {
  const isResolved = alertData.status === 'resolved';
  
  if (isResolved) {
    toast.success(message);
    window.dispatchEvent(new CustomEvent('alertResolved', { detail: alertData }));
  } else {
    toast.warning(message);
    window.dispatchEvent(new CustomEvent('stockAlert', { detail: alertData }));
  }
}
```

### Dashboard Components

#### 1. Stock Status Chart
```typescript
const stockStatusData = [
  { 
    name: 'In Stock', 
    value: inStockItems.length,
    details: inStockItems.map(item => 
      `${product.name} - ${item.available_quantity} units at ${location.name}`
    )
  },
  // ... Low Stock, Out of Stock
];
```

**Custom Tooltip:**
```typescript
const StockStatusTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-4 border rounded-lg shadow-lg">
        <p className="font-bold">{data.name}</p>
        <p>Count: {data.value}</p>
        <p>Percentage: {percentage}%</p>
        {data.details && (
          <div className="max-h-32 overflow-y-auto">
            {data.details.slice(0, 5).map(detail => (
              <p key={index}>• {detail}</p>
            ))}
          </div>
        )}
      </div>
    );
  }
  return null;
};
```

#### 2. Purchase Order Chart
```typescript
const poStatusData = [
  { 
    name: 'Draft', 
    value: draftPOs.length,
    details: draftPOs.map(po => 
      `PO-${po.id}: ${po.supplier?.name}`
    )
  },
  // ... other statuses
];
```

## Database Schema

### Core Tables

#### Products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    price DECIMAL(10,2),
    min_stock_level INTEGER DEFAULT 0,
    max_stock_level INTEGER,
    reorder_point INTEGER,
    category_id INTEGER REFERENCES categories(id),
    supplier_id INTEGER REFERENCES suppliers(id)
);
```

#### Inventory
```sql
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    location_id INTEGER REFERENCES locations(id),
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    available_quantity INTEGER DEFAULT 0,
    unit_cost DECIMAL(10,2)
);
```

#### Stock Alerts
```sql
CREATE TABLE stock_alerts (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    location_id INTEGER REFERENCES locations(id),
    alert_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    current_quantity INTEGER,
    threshold_quantity INTEGER,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/inventory_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Inventory Management System

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Background Task
CHECK_INTERVAL_SECONDS=60
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Testing

### Backend Tests

#### Unit Tests
```python
# tests/unit/test_stock_alerts.py
def test_low_stock_alert_creation():
    """Test creating low stock alert"""
    # Test implementation

def test_alert_auto_resolution():
    """Test automatic alert resolution"""
    # Test implementation
```

#### Integration Tests
```python
# tests/integration/test_api_integration.py
def test_stock_alert_workflow():
    """Test complete stock alert workflow"""
    # Test implementation
```

### Frontend Tests

#### Component Tests
```typescript
// src/__tests__/components/Dashboard.test.tsx
describe('Dashboard', () => {
  it('renders stock status chart', () => {
    // Test implementation
  });

  it('shows correct hover details', () => {
    // Test implementation
  });
});
```

## Performance Optimization

### Backend Optimizations

#### 1. Database Indexing
```sql
-- Index for stock alerts
CREATE INDEX idx_stock_alerts_status ON stock_alerts(status);
CREATE INDEX idx_stock_alerts_product_location ON stock_alerts(product_id, location_id);

-- Index for inventory queries
CREATE INDEX idx_inventory_product_location ON inventory(product_id, location_id);
CREATE INDEX idx_inventory_available_quantity ON inventory(available_quantity);
```

#### 2. Background Task Optimization
```python
# Batch processing for large datasets
async def _check_stock_alerts_batch(self, rules: List[AlertRule]):
    """Process alerts in batches"""
    batch_size = 100
    for i in range(0, len(rules), batch_size):
        batch = rules[i:i + batch_size]
        await self._process_alert_batch(batch)
```

### Frontend Optimizations

#### 1. React Query Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});
```

#### 2. WebSocket Reconnection Strategy
```typescript
private async reconnect() {
  if (this.reconnectAttempts < this.maxReconnectAttempts) {
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }
}
```

## Security Considerations

### Authentication & Authorization
- JWT tokens for API authentication
- Role-based access control
- Secure password hashing with bcrypt
- CORS configuration for frontend access

### Data Validation
- Pydantic models for request/response validation
- SQL injection prevention with SQLAlchemy ORM
- Input sanitization for all user inputs

### WebSocket Security
- User authentication for WebSocket connections
- Rate limiting for WebSocket messages
- Connection validation and cleanup

## Monitoring & Logging

### Backend Logging
```python
import logging

logger = logging.getLogger(__name__)

# Background task logging
logger.info(f"Stock alert check completed. {alerts_created} new alerts created")

# Error logging
logger.error(f"Error checking stock alerts: {e}")
```

### Frontend Error Tracking
```typescript
// Error boundary for React components
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error tracking service
  }
}
```

## Deployment

### Docker Configuration
```dockerfile
# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: inventory_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/inventory_db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Troubleshooting Guide

### Common Issues

#### 1. WebSocket Connection Issues
**Symptoms:** No real-time notifications
**Solutions:**
- Check backend is running on port 8000
- Verify WebSocket URL in frontend
- Check browser console for connection errors
- Ensure CORS is configured correctly

#### 2. Background Task Not Running
**Symptoms:** No automatic alerts
**Solutions:**
- Check background task status endpoint
- Verify database connection
- Check logs for errors
- Ensure alert rules are configured

#### 3. Dashboard Charts Not Loading
**Symptoms:** Empty or broken charts
**Solutions:**
- Verify API endpoints are accessible
- Check data structure matches chart expectations
- Ensure proper error handling in chart components
- Verify React Query cache configuration

### Debug Commands

```bash
# Check background task status
curl http://localhost:8000/api/v1/stock-alerts/background-task/status

# Trigger manual alert check
curl -X POST http://localhost:8000/api/v1/stock-alerts/background-task/trigger

# Get active alerts
curl http://localhost:8000/api/v1/stock-alerts/alerts/active

# Test WebSocket connection
python test_websocket.py
```

## API Documentation

### Swagger UI
Access the interactive API documentation at:
- Development: `http://localhost:8000/docs`
- Production: `https://your-domain.com/docs`

### ReDoc
Alternative documentation format:
- Development: `http://localhost:8000/redoc`
- Production: `https://your-domain.com/redoc`

---

This technical documentation provides comprehensive information for developers working with the Inventory Management System. For additional support, refer to the main README.md or create an issue in the repository. 