import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { PlusIcon, EyeIcon, PencilIcon, TrashIcon, CheckIcon, XMarkIcon, TruckIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { PurchaseOrder, PurchaseOrderCreate, PurchaseOrderItemCreate, PurchaseOrderStatus, Supplier, Product, UserWithPermissions } from '../types';

const PurchaseOrders: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentUser, setCurrentUser] = useState<UserWithPermissions | null>(null);
  const queryClient = useQueryClient();

  // Get current user for role-based permissions
  const { data: userData } = useQuery(
    ['current-user'],
    () => apiService.users.getCurrentUser(),
    {
      onSuccess: (data) => setCurrentUser(data),
    }
  );

  const { data: purchaseOrdersData, isLoading, error } = useQuery(
    ['purchase-orders', searchTerm, statusFilter],
    () => apiService.purchaseOrders.getPurchaseOrders({ 
      status: statusFilter || undefined
    })
  );

  const { data: suppliersData } = useQuery(
    ['suppliers'],
    () => apiService.suppliers.getSuppliers()
  );

  const { data: productsData } = useQuery(
    ['products'],
    () => apiService.products.getProducts()
  );

  const createMutation = useMutation(
    (data: PurchaseOrderCreate) => apiService.purchaseOrders.createPurchaseOrder(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        setIsModalOpen(false);
        toast.success('Purchase order created successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create purchase order');
      }
    }
  );

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => apiService.purchaseOrders.updatePurchaseOrderWithItems(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        setIsModalOpen(false);
        setSelectedPO(null);
        toast.success('Purchase order updated successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update purchase order');
      }
    }
  );

  const cancelMutation = useMutation(
    (id: number) => apiService.purchaseOrders.cancelPurchaseOrder(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        toast.success('Purchase order cancelled successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to cancel purchase order');
      }
    }
  );

  const statusChangeMutation = useMutation(
    ({ id, status }: { id: number; status: PurchaseOrderStatus }) => 
      apiService.purchaseOrders.changePurchaseOrderStatus(id, status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        toast.success('Purchase order status updated successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update purchase order status');
      }
    }
  );

  const handleSubmit = (formData: PurchaseOrderCreate) => {
    if (selectedPO) {
      // Update existing purchase order
      updateMutation.mutate({ id: selectedPO.id, data: formData });
    } else {
      // Create new purchase order
      createMutation.mutate(formData);
    }
  };

  const handleCancel = (id: number) => {
    if (window.confirm('Are you sure you want to cancel this purchase order?')) {
      cancelMutation.mutate(id);
    }
  };

  const handleStatusChange = (id: number, newStatus: PurchaseOrderStatus) => {
    statusChangeMutation.mutate({ id, status: newStatus });
  };

  const canApprovePO = currentUser?.can_approve_po || false;
  const canCancelPO = currentUser?.can_cancel_po || false;
  const canReceivePO = currentUser?.can_receive_po || false;
  const canEditPO = currentUser?.can_edit_po || false;

  const getStatusColor = (status: PurchaseOrderStatus) => {
    switch (status) {
      case PurchaseOrderStatus.DRAFT:
        return 'bg-gray-100 text-gray-800';
      case PurchaseOrderStatus.PENDING_APPROVAL:
        return 'bg-yellow-100 text-yellow-800';
      case PurchaseOrderStatus.APPROVED:
        return 'bg-blue-100 text-blue-800';
      case PurchaseOrderStatus.ORDERED:
        return 'bg-purple-100 text-purple-800';
      case PurchaseOrderStatus.PARTIALLY_RECEIVED:
        return 'bg-orange-100 text-orange-800';
      case PurchaseOrderStatus.RECEIVED:
        return 'bg-green-100 text-green-800';
      case PurchaseOrderStatus.CANCELLED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">Error loading purchase orders</div>;

  const purchaseOrders = purchaseOrdersData?.data || [];
  const suppliers = suppliersData?.data || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Purchase Orders</h1>
          {currentUser && (
            <div className="mt-1 flex items-center space-x-4 text-sm text-gray-600">
              <span className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Logged in as: <span className="font-medium">{currentUser.full_name}</span>
                <span className="ml-2 px-2 py-1 bg-gray-100 rounded text-xs capitalize">
                  {currentUser.role}
                </span>
              </span>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500">Permissions:</span>
                {canEditPO && <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Create/Edit</span>}
                {canApprovePO && <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Approve</span>}
                {canCancelPO && <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">Cancel</span>}
                {canReceivePO && <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">Receive</span>}
              </div>
            </div>
          )}
        </div>
        {canEditPO && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create PO
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Search PO number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            {Object.values(PurchaseOrderStatus).map((status) => (
              <option key={status} value={status}>
                {status.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Purchase Orders Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                PO Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Supplier
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Expected Delivery
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {purchaseOrders.map((po) => (
              <tr key={po.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{po.po_number}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{po.supplier?.name || 'N/A'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {new Date(po.order_date).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {po.expected_delivery_date 
                      ? new Date(po.expected_delivery_date).toLocaleDateString()
                      : '-'
                    }
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    ${po.total_amount.toFixed(2)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(po.status)}`}>
                    {po.status.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => setSelectedPO(po)}
                      className="text-blue-600 hover:text-blue-900"
                      title="View Details"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    
                    {/* Edit button - only for users who can edit */}
                    {canEditPO && po.status !== PurchaseOrderStatus.RECEIVED && po.status !== PurchaseOrderStatus.CANCELLED && (
                      <button
                        onClick={() => {
                          setSelectedPO(po);
                          setIsModalOpen(true);
                        }}
                        className="text-green-600 hover:text-green-900"
                        title="Edit PO"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {/* Status change buttons based on current status and permissions */}
                    {po.status === PurchaseOrderStatus.DRAFT && canEditPO && (
                      <button
                        onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.PENDING_APPROVAL)}
                        className="text-yellow-600 hover:text-yellow-900"
                        title="Submit for Approval"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {po.status === PurchaseOrderStatus.PENDING_APPROVAL && canApprovePO && (
                      <button
                        onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.APPROVED)}
                        className="text-green-600 hover:text-green-900"
                        title="Approve PO"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {po.status === PurchaseOrderStatus.APPROVED && canEditPO && (
                      <button
                        onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.ORDERED)}
                        className="text-purple-600 hover:text-purple-900"
                        title="Mark as Ordered"
                      >
                        <TruckIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {po.status === PurchaseOrderStatus.ORDERED && canReceivePO && (
                      <div className="flex space-x-1">
                        <button
                          onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.PARTIALLY_RECEIVED)}
                          className="text-orange-600 hover:text-orange-900"
                          title="Mark as Partially Received"
                        >
                          <TruckIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.RECEIVED)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Mark as Fully Received"
                        >
                          <TruckIcon className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                    
                    {po.status === PurchaseOrderStatus.PARTIALLY_RECEIVED && canReceivePO && (
                      <button
                        onClick={() => handleStatusChange(po.id, PurchaseOrderStatus.RECEIVED)}
                        className="text-green-600 hover:text-green-900"
                        title="Mark as Fully Received"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {/* Cancel button - only for users who can cancel and for cancellable statuses */}
                    {canCancelPO && 
                     po.status !== PurchaseOrderStatus.RECEIVED && 
                     po.status !== PurchaseOrderStatus.CANCELLED && (
                      <button
                        onClick={() => handleCancel(po.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Cancel PO"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Purchase Order Modal */}
      {isModalOpen && (
        <PurchaseOrderModal
          purchaseOrder={selectedPO}
          suppliers={suppliers}
          products={productsData?.data || []}
          onSubmit={handleSubmit}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedPO(null);
          }}
          isLoading={createMutation.isLoading || updateMutation.isLoading}
        />
      )}

      {/* Purchase Order Details Modal */}
      {selectedPO && !isModalOpen && (
        <PurchaseOrderDetailsModal
          purchaseOrder={selectedPO}
          onClose={() => setSelectedPO(null)}
        />
      )}
    </div>
  );
};

// Purchase Order Modal Component
interface PurchaseOrderModalProps {
  purchaseOrder: PurchaseOrder | null;
  suppliers: Supplier[];
  products: Product[];
  onSubmit: (data: PurchaseOrderCreate) => void;
  onClose: () => void;
  isLoading: boolean;
}

const PurchaseOrderModal: React.FC<PurchaseOrderModalProps> = ({ 
  purchaseOrder, 
  suppliers, 
  products,
  onSubmit, 
  onClose, 
  isLoading 
}) => {
  const [formData, setFormData] = useState<PurchaseOrderCreate>({
    supplier_id: purchaseOrder?.supplier_id || 0,
    order_date: purchaseOrder?.order_date || new Date().toISOString().split('T')[0],
    expected_delivery_date: purchaseOrder?.expected_delivery_date || '',
    payment_terms: purchaseOrder?.payment_terms || '',
    shipping_address: purchaseOrder?.shipping_address || '',
    billing_address: purchaseOrder?.billing_address || '',
    notes: purchaseOrder?.notes || '',
    items: purchaseOrder?.items || [],
    tax_amount: purchaseOrder?.tax_amount || 0,
    shipping_amount: purchaseOrder?.shipping_amount || 0,
  });

  // Filter products based on selected supplier
  const filteredProducts = formData.supplier_id 
    ? products.filter(product => product.supplier_id === formData.supplier_id)
    : [];

  // Calculate totals
  const subtotal = formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  const total = subtotal + (formData.tax_amount || 0) + (formData.shipping_amount || 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, {
        product_id: 0,
        quantity: 1,
        unit_price: 0,
        supplier_sku: '',
        notes: ''
      }]
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index)
    });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  // Handle supplier change - clear product selections when supplier changes
  const handleSupplierChange = (supplierId: number) => {
    setFormData({
      ...formData,
      supplier_id: supplierId,
      items: [] // Clear items when supplier changes
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {purchaseOrder ? 'Edit Purchase Order' : 'Create Purchase Order'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Supplier</label>
                <select
                  required
                  value={formData.supplier_id}
                  onChange={(e) => handleSupplierChange(parseInt(e.target.value))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select supplier</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Order Date</label>
                <input
                  type="date"
                  required
                  value={formData.order_date}
                  onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Expected Delivery Date</label>
              <input
                type="date"
                value={formData.expected_delivery_date}
                onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Terms</label>
              <input
                type="text"
                value={formData.payment_terms}
                onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                placeholder="e.g., Net 30"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Items Section */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-medium text-gray-900">Items</h4>
                <button
                  type="button"
                  onClick={addItem}
                  disabled={!formData.supplier_id || filteredProducts.length === 0}
                  className={`px-3 py-1 rounded-md text-sm ${
                    !formData.supplier_id || filteredProducts.length === 0
                      ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  Add Item
                </button>
              </div>
              
              {formData.items.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  {!formData.supplier_id 
                    ? "Please select a supplier first to add items to this purchase order."
                    : filteredProducts.length === 0 
                      ? "No products are available for the selected supplier. Please choose a different supplier or add products to this supplier."
                      : "No items added yet. Click 'Add Item' to start."
                  }
                </p>
              ) : (
                <div className="space-y-3">
                  {formData.items.map((item, index) => (
                    <div key={index} className="border border-gray-200 rounded-md p-4">
                      <div className="grid grid-cols-4 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Product</label>
                          <select
                            required
                            value={item.product_id}
                            onChange={(e) => updateItem(index, 'product_id', parseInt(e.target.value))}
                            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">
                              {!formData.supplier_id 
                                ? "Please select a supplier first" 
                                : filteredProducts.length === 0 
                                  ? "No products available for this supplier" 
                                  : "Select product"
                              }
                            </option>
                            {filteredProducts.map((product) => (
                              <option key={product.id} value={product.id}>
                                {product.name} (${product.price})
                              </option>
                            ))}
                          </select>
                          {!formData.supplier_id && (
                            <p className="text-xs text-orange-600 mt-1">Please select a supplier to see available products</p>
                          )}
                          {formData.supplier_id && filteredProducts.length === 0 && (
                            <p className="text-xs text-orange-600 mt-1">No products are available for the selected supplier</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Quantity</label>
                          <input
                            type="number"
                            required
                            min="1"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value))}
                            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Unit Price</label>
                          <input
                            type="number"
                            required
                            step="0.01"
                            min="0"
                            value={item.unit_price}
                            onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value))}
                            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="flex items-end">
                          <button
                            type="button"
                            onClick={() => removeItem(index)}
                            className="bg-red-600 text-white px-3 py-2 rounded-md text-sm hover:bg-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                      <div className="mt-2">
                        <label className="block text-sm font-medium text-gray-700">Notes</label>
                        <input
                          type="text"
                          value={item.notes || ''}
                          onChange={(e) => updateItem(index, 'notes', e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Financial Summary */}
            <div className="bg-gray-50 rounded-md p-4">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Financial Summary</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tax Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.tax_amount || 0}
                    onChange={(e) => setFormData({ ...formData, tax_amount: parseFloat(e.target.value) || 0 })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Shipping Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.shipping_amount || 0}
                    onChange={(e) => setFormData({ ...formData, shipping_amount: parseFloat(e.target.value) || 0 })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Subtotal:</span>
                  <span className="text-sm font-medium">${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tax:</span>
                  <span className="text-sm font-medium">${(formData.tax_amount || 0).toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Shipping:</span>
                  <span className="text-sm font-medium">${(formData.shipping_amount || 0).toFixed(2)}</span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="text-sm font-medium text-gray-900">Total:</span>
                  <span className="text-sm font-bold text-gray-900">${total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : purchaseOrder ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Purchase Order Details Modal Component
interface PurchaseOrderDetailsModalProps {
  purchaseOrder: PurchaseOrder;
  onClose: () => void;
}

const PurchaseOrderDetailsModal: React.FC<PurchaseOrderDetailsModalProps> = ({ purchaseOrder, onClose }) => {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Purchase Order: {purchaseOrder.po_number}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Order Details</h4>
              <dl className="space-y-1">
                <div>
                  <dt className="text-sm text-gray-500">Supplier:</dt>
                  <dd className="text-sm text-gray-900">{purchaseOrder.supplier?.name}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Order Date:</dt>
                  <dd className="text-sm text-gray-900">
                    {new Date(purchaseOrder.order_date).toLocaleDateString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Expected Delivery:</dt>
                  <dd className="text-sm text-gray-900">
                    {purchaseOrder.expected_delivery_date 
                      ? new Date(purchaseOrder.expected_delivery_date).toLocaleDateString()
                      : 'Not specified'
                    }
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Status:</dt>
                  <dd className="text-sm text-gray-900">{purchaseOrder.status}</dd>
                </div>
              </dl>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Financial Details</h4>
              <dl className="space-y-1">
                <div>
                  <dt className="text-sm text-gray-500">Subtotal:</dt>
                  <dd className="text-sm text-gray-900">${purchaseOrder.subtotal.toFixed(2)}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Tax:</dt>
                  <dd className="text-sm text-gray-900">${purchaseOrder.tax_amount.toFixed(2)}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Shipping:</dt>
                  <dd className="text-sm text-gray-900">${purchaseOrder.shipping_amount.toFixed(2)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Total:</dt>
                  <dd className="text-sm font-medium text-gray-900">${purchaseOrder.total_amount.toFixed(2)}</dd>
                </div>
              </dl>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Items</h4>
            <div className="bg-gray-50 rounded-md p-4">
              {purchaseOrder.items.length > 0 ? (
                <div className="space-y-2">
                  {purchaseOrder.items.map((item) => (
                    <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {item.product?.name || `Product ID: ${item.product_id}`}
                        </div>
                        <div className="text-sm text-gray-500">
                          Qty: {item.quantity} × ${item.unit_price.toFixed(2)}
                        </div>
                      </div>
                      <div className="text-sm font-medium text-gray-900">
                        ${item.total_price.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No items in this purchase order.</p>
              )}
            </div>
          </div>

          <div className="flex justify-end mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrders; 