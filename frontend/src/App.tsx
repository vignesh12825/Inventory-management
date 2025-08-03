import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Categories from './pages/Categories';
import InventoryPage from './pages/Inventory';
import Suppliers from './pages/Suppliers';
import Locations from './pages/Locations';
import PurchaseOrders from './pages/PurchaseOrders';
import StockAlerts from './pages/StockAlerts';
import Users from './pages/Users';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="categories" element={<Categories />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="suppliers" element={<Suppliers />} />
          <Route path="locations" element={<Locations />} />
          <Route path="purchase-orders" element={<PurchaseOrders />} />
          <Route path="stock-alerts" element={<StockAlerts />} />
          <Route path="profile" element={<Profile />} />
          <Route 
            path="users" 
            element={
              <ProtectedRoute requiredPermissions={['can_manage_users']}>
                <Users />
              </ProtectedRoute>
            } 
          />
        </Route>
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}

export default App; 