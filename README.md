# 📦 Inventory Management System

A comprehensive, real-time inventory management solution built with FastAPI (Backend) and React (Frontend) featuring WebSocket notifications, automated stock alerts, and advanced analytics.

## 🚀 Features

### Core Functionality
- **Real-time Stock Management**: Track inventory levels across multiple locations
- **Automated Alerts**: Instant WebSocket notifications for low stock and out-of-stock items
- **Purchase Order Management**: Complete PO lifecycle from draft to received
- **Multi-location Support**: Manage inventory across different warehouses/locations
- **Supplier Management**: Track suppliers and their performance
- **Product Catalog**: Comprehensive product management with categories

### Advanced Features
- **Real-time Notifications**: WebSocket-based instant alerts
- **Smart Alert System**: Auto-resolve alerts when stock levels improve
- **Interactive Dashboard**: Pie chart for stock status and bar chart for purchase orders
- **Stock Movement Tracking**: Complete audit trail of stock adjustments
- **User Authentication**: Secure login with role-based access
- **Responsive Design**: Mobile-friendly interface

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core functionality
│   │   ├── background_tasks.py  # Automated stock alerts
│   │   ├── websocket.py         # WebSocket management
│   │   └── database.py          # Database configuration
│   ├── models/               # SQLAlchemy models
│   └── schemas/              # Pydantic schemas
├── alembic/                  # Database migrations
└── tests/                    # Unit and integration tests
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   ├── pages/               # Page components
│   ├── contexts/            # React contexts (Auth, Notifications)
│   ├── services/            # API and WebSocket services
│   └── types/               # TypeScript type definitions
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **WebSockets**: Real-time communication
- **Background Tasks**: Automated stock monitoring
- **JWT Authentication**: Secure user authentication

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Recharts**: Interactive charts and graphs
- **React Router**: Client-side routing
- **React Toastify**: Toast notifications

## 📊 Dashboard Features

### Stock Status Pie Chart
- **In Stock**: Items above minimum stock level
- **Low Stock**: Items at or below minimum stock level
- **Out of Stock**: Items with zero or negative available quantity
- **Hover Details**: Shows specific products and quantities

### Purchase Order Bar Chart
- **Draft**: POs in initial state
- **Pending**: POs awaiting approval
- **Approved**: POs approved but not ordered
- **Ordered**: POs sent to suppliers
- **Received**: POs completed and received
- **Cancelled**: POs that were cancelled
- **Hover Details**: Shows specific PO numbers and suppliers

## 🔔 Alert System

### Real-time Notifications
- **WebSocket Connection**: Instant communication between backend and frontend
- **Background Monitoring**: Checks stock levels every 60 seconds
- **Smart Resolution**: Automatically resolves alerts when stock improves
- **No Re-triggering**: Prevents unnecessary alerts for acknowledged/resolved items

### Alert Types
- **Low Stock**: When available quantity ≤ minimum stock level
- **Out of Stock**: When available quantity ≤ 0
- **Auto-resolution**: When stock levels improve above thresholds

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd inventory-management
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### 4. Using Docker (Alternative)
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/inventory_db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
PROJECT_NAME=Inventory Management System

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/users/me` - Get current user

### Inventory Management
- `GET /api/v1/inventory/` - List inventory items
- `POST /api/v1/inventory/` - Create inventory item
- `PUT /api/v1/inventory/{id}` - Update inventory item
- `DELETE /api/v1/inventory/{id}` - Delete inventory item
- `POST /api/v1/inventory/{id}/adjust` - Adjust stock levels

### Stock Alerts
- `GET /api/v1/stock-alerts/alerts/active` - Get active alerts
- `POST /api/v1/stock-alerts/check-alerts` - Manual alert check
- `GET /api/v1/stock-alerts/background-task/status` - Background task status
- `POST /api/v1/stock-alerts/background-task/trigger` - Trigger immediate check

### WebSocket
- `WS /api/v1/ws/alerts` - General alerts
- `WS /api/v1/ws/alerts/{user_id}` - User-specific alerts

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

### Background Task Status
```bash
curl http://localhost:8000/api/v1/stock-alerts/background-task/status
```

### Active Alerts
```bash
curl http://localhost:8000/api/v1/stock-alerts/alerts/active
```

## 🔍 Troubleshooting

### Common Issues

#### WebSocket Notifications Not Working
1. Check if backend is running on port 8000
2. Verify WebSocket connection in browser dev tools
3. Check background task status
4. Ensure alerts are being created

#### Stock Status Not Updating
1. Verify `available_quantity` field is being used
2. Check minimum stock levels are set correctly
3. Ensure background task is running
4. Check database for alert rules

#### Dashboard Charts Not Loading
1. Verify API endpoints are accessible
2. Check browser console for errors
3. Ensure data is being fetched correctly
4. Verify chart data structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## 🔄 Version History

### v1.0.0
- Initial release
- Real-time stock management
- WebSocket notifications
- Interactive dashboard
- Automated alert system
- Multi-location support

---

**Built with ❤️ using FastAPI and React** 