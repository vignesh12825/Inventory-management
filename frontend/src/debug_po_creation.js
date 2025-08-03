// Debug script to help identify 422 errors in purchase order creation
// Add this to browser console when creating a PO

function debugPOCreation() {
  console.log('🔍 Debugging Purchase Order Creation...');
  
  // Get form data
  const supplierSelect = document.querySelector('select[value]');
  const orderDateInput = document.querySelector('input[type="date"]');
  const items = document.querySelectorAll('[data-item]');
  
  console.log('📋 Form Data:');
  console.log('Supplier ID:', supplierSelect?.value, 'Type:', typeof supplierSelect?.value);
  console.log('Order Date:', orderDateInput?.value, 'Type:', typeof orderDateInput?.value);
  
  // Check items
  items.forEach((item, index) => {
    const productSelect = item.querySelector('select');
    const quantityInput = item.querySelector('input[type="number"]');
    const priceInput = item.querySelector('input[step="0.01"]');
    
    console.log(`Item ${index + 1}:`);
    console.log('  Product ID:', productSelect?.value, 'Type:', typeof productSelect?.value);
    console.log('  Quantity:', quantityInput?.value, 'Type:', typeof quantityInput?.value);
    console.log('  Unit Price:', priceInput?.value, 'Type:', typeof priceInput?.value);
  });
  
  // Simulate the request
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.log('❌ No auth token found');
    return;
  }
  
  // Build request data
  const requestData = {
    supplier_id: parseInt(supplierSelect?.value) || 0,
    order_date: orderDateInput?.value || new Date().toISOString().split('T')[0],
    items: []
  };
  
  items.forEach((item) => {
    const productSelect = item.querySelector('select');
    const quantityInput = item.querySelector('input[type="number"]');
    const priceInput = item.querySelector('input[step="0.01"]');
    
    if (productSelect?.value && quantityInput?.value && priceInput?.value) {
      requestData.items.push({
        product_id: parseInt(productSelect.value),
        quantity: parseInt(quantityInput.value),
        unit_price: parseFloat(priceInput.value),
        supplier_sku: '',
        notes: ''
      });
    }
  });
  
  console.log('📤 Request Data:', JSON.stringify(requestData, null, 2));
  
  // Test the request
  fetch('http://localhost:8000/api/v1/purchase-orders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(requestData)
  })
  .then(response => {
    console.log('📥 Response Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('📥 Response Data:', data);
  })
  .catch(error => {
    console.log('❌ Request Error:', error);
  });
}

// Run the debug function
debugPOCreation(); 