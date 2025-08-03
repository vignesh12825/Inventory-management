-- Initialize the inventory management database
-- This script creates the initial database structure

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (these will be created by SQLAlchemy, but we can add any initial data here)

-- Insert some sample categories
INSERT INTO categories (name, description) VALUES 
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Books and publications'),
('Home & Garden', 'Home improvement and garden supplies')
ON CONFLICT (name) DO NOTHING;

-- Insert some sample products
INSERT INTO products (name, description, sku, price, cost, category_id) VALUES 
('Laptop Computer', 'High-performance laptop for business use', 'LAPTOP-001', 999.99, 750.00, 1),
('Smartphone', 'Latest smartphone model', 'PHONE-001', 699.99, 550.00, 1),
('T-Shirt', 'Cotton t-shirt in various sizes', 'TSHIRT-001', 19.99, 12.00, 2),
('Programming Book', 'Learn Python programming', 'BOOK-001', 49.99, 30.00, 3)
ON CONFLICT (sku) DO NOTHING;

-- Insert some sample inventory items
INSERT INTO inventory (product_id, quantity, location, notes) VALUES 
(1, 10, 'Warehouse A', 'Main storage area'),
(2, 25, 'Warehouse B', 'Mobile devices section'),
(3, 100, 'Warehouse C', 'Clothing section'),
(4, 50, 'Warehouse A', 'Books section')
ON CONFLICT DO NOTHING; 