import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { PlusIcon, PencilIcon, TrashIcon, MapPinIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { Inventory as InventoryType, InventoryCreate, InventoryUpdate, Product, Location } from '../types';

const InventoryPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAdjustmentModalOpen, setIsAdjustmentModalOpen] = useState(false);
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [editingInventory, setEditingInventory] = useState<InventoryType | null>(null);
  const [selectedInventory, setSelectedInventory] = useState<InventoryType | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [adjustmentQuantity, setAdjustmentQuantity] = useState<number>(0);
  const [adjustmentNotes, setAdjustmentNotes] = useState<string>('');
  const [movementData, setMovementData] = useState({
    quantity: 0,
    movementType: 'in',
    notes: '',
    fromLocationId: '',
    toLocationId: ''
  });
  const queryClient = useQueryClient();

  const { data: inventoryData, isLoading, error } = useQuery(
    ['inventory', selectedLocation],
    () => apiService.inventory.getInventory({ 
      location_id: selectedLocation ? parseInt(selectedLocation) : undefined
    })
  );

  const { data: productsData } = useQuery(
    ['products'],
    () => apiService.products.getProducts({ is_active: true })
  );

  const { data: locationsData } = useQuery(
    ['locations'],
    () => apiService.locations.getLocations({ is_active: true })
  );

  const createMutation = useMutation(
    (data: InventoryCreate) => apiService.inventory.createInventoryItem(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('inventory');
        setIsModalOpen(false);
        toast.success('Inventory item created successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create inventory item');
      }
    }
  );

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: InventoryUpdate }) =>
      apiService.inventory.updateInventoryItem(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('inventory');
        setIsModalOpen(false);
        setEditingInventory(null);
        toast.success('Inventory item updated successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update inventory item');
      }
    }
  );

  const deleteMutation = useMutation(
    (id: number) => apiService.inventory.deleteInventoryItem(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('inventory');
        toast.success('Inventory item deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete inventory item');
      }
    }
  );

  const adjustStockMutation = useMutation(
    ({ inventoryId, quantityChange, notes }: { inventoryId: number; quantityChange: number; notes?: string }) =>
      apiService.inventory.adjustStock(inventoryId, quantityChange, notes),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('inventory');
        setIsAdjustmentModalOpen(false);
        setSelectedInventory(null);
        setAdjustmentQuantity(0);
        setAdjustmentNotes('');
        toast.success('Stock adjusted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to adjust stock');
      }
    }
  );

  const createMovementMutation = useMutation(
    ({ inventoryId, movementData }: { inventoryId: number; movementData: any }) =>
      apiService.inventory.createStockMovement(inventoryId, movementData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('inventory');
        setIsMovementModalOpen(false);
        setSelectedInventory(null);
        setMovementData({
          quantity: 0,
          movementType: 'in',
          notes: '',
          fromLocationId: '',
          toLocationId: ''
        });
        toast.success('Stock movement recorded successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to record stock movement');
      }
    }
  );

  const handleSubmit = (formData: InventoryCreate) => {
    if (editingInventory) {
      updateMutation.mutate({ id: editingInventory.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (inventory: InventoryType) => {
    setEditingInventory(inventory);
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this inventory item?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleAdjustStock = (inventory: InventoryType) => {
    setSelectedInventory(inventory);
    setIsAdjustmentModalOpen(true);
  };

  const handleMovement = (inventory: InventoryType) => {
    setSelectedInventory(inventory);
    setIsMovementModalOpen(true);
  };

  const handleAdjustmentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInventory || adjustmentQuantity === 0) {
      toast.error('Please enter a valid quantity');
      return;
    }
    
    adjustStockMutation.mutate({
      inventoryId: selectedInventory.id,
      quantityChange: adjustmentQuantity,
      notes: adjustmentNotes
    });
  };

  const handleMovementSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInventory || movementData.quantity <= 0) {
      toast.error('Please enter a valid quantity');
      return;
    }

    const movementPayload = {
      movement_type: movementData.movementType,
      quantity: movementData.quantity,
      notes: movementData.notes,
      from_location_id: movementData.fromLocationId ? parseInt(movementData.fromLocationId) : undefined,
      to_location_id: movementData.toLocationId ? parseInt(movementData.toLocationId) : undefined
    };

    createMovementMutation.mutate({
      inventoryId: selectedInventory.id,
      movementData: movementPayload
    });
  };

  const getStockStatus = (availableQuantity: number, minLevel: number) => {
    if (availableQuantity <= 0) return { status: 'Out of Stock', color: 'text-red-600' };
    if (availableQuantity <= minLevel) return { status: 'Low Stock', color: 'text-yellow-600' };
    return { status: 'In Stock', color: 'text-green-600' };
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">Error loading inventory</div>;

  const inventory = inventoryData?.data || [];
  const products = productsData?.data || [];
  const locations = locationsData?.data || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Inventory Item
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Locations</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Available
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Unit Cost
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {inventory.map((item) => {
              const product = products.find(p => p.id === item.product_id);
              const location = locations.find(l => l.id === item.location_id);
              const stockStatus = getStockStatus(item.available_quantity, product?.min_stock_level || 0);
              
              return (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{product?.name || 'Unknown Product'}</div>
                    <div className="text-sm text-gray-500">{product?.sku || 'No SKU'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MapPinIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900">{location?.name || 'Unknown Location'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{item.quantity}</div>
                    {item.reserved_quantity > 0 && (
                      <div className="text-xs text-gray-500">Reserved: {item.reserved_quantity}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{item.available_quantity}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${stockStatus.color}`}>
                      {stockStatus.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {item.unit_cost ? `$${item.unit_cost.toFixed(2)}` : 'N/A'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => handleAdjustStock(item)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Adjust Stock"
                      >
                        <ArrowUpIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleMovement(item)}
                        className="text-green-600 hover:text-green-900"
                        title="Record Movement"
                      >
                        <ArrowDownIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleEdit(item)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Inventory Modal */}
      {isModalOpen && (
        <InventoryModal
          inventory={editingInventory}
          products={products}
          locations={locations}
          onSubmit={handleSubmit}
          onClose={() => {
            setIsModalOpen(false);
            setEditingInventory(null);
          }}
          isLoading={createMutation.isLoading || updateMutation.isLoading}
        />
      )}

      {/* Stock Adjustment Modal */}
      {isAdjustmentModalOpen && selectedInventory && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Adjust Stock</h3>
              <p className="text-sm text-gray-500 mb-4">
                Adjusting stock for: {products.find(p => p.id === selectedInventory.product_id)?.name}
              </p>
              <form onSubmit={handleAdjustmentSubmit}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity Change *
                  </label>
                  <input
                    type="number"
                    value={adjustmentQuantity}
                    onChange={(e) => setAdjustmentQuantity(parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter quantity (positive to add, negative to subtract)"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Current quantity: {selectedInventory.quantity}
                  </p>
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={adjustmentNotes}
                    onChange={(e) => setAdjustmentNotes(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Reason for adjustment"
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setIsAdjustmentModalOpen(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={adjustStockMutation.isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {adjustStockMutation.isLoading ? 'Adjusting...' : 'Adjust Stock'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Stock Movement Modal */}
      {isMovementModalOpen && selectedInventory && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Record Stock Movement</h3>
              <p className="text-sm text-gray-500 mb-4">
                Recording movement for: {products.find(p => p.id === selectedInventory.product_id)?.name}
              </p>
              <form onSubmit={handleMovementSubmit}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Movement Type *
                  </label>
                  <select
                    value={movementData.movementType}
                    onChange={(e) => setMovementData({ ...movementData, movementType: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="in">Stock In</option>
                    <option value="out">Stock Out</option>
                    <option value="transfer">Transfer</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity *
                  </label>
                  <input
                    type="number"
                    value={movementData.quantity}
                    onChange={(e) => setMovementData({ ...movementData, quantity: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter quantity"
                    required
                  />
                </div>
                {movementData.movementType === 'transfer' && (
                  <>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        From Location
                      </label>
                      <select
                        value={movementData.fromLocationId}
                        onChange={(e) => setMovementData({ ...movementData, fromLocationId: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select location</option>
                        {locations.map((location) => (
                          <option key={location.id} value={location.id}>
                            {location.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        To Location
                      </label>
                      <select
                        value={movementData.toLocationId}
                        onChange={(e) => setMovementData({ ...movementData, toLocationId: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select location</option>
                        {locations.map((location) => (
                          <option key={location.id} value={location.id}>
                            {location.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={movementData.notes}
                    onChange={(e) => setMovementData({ ...movementData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Movement details"
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setIsMovementModalOpen(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createMovementMutation.isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
                  >
                    {createMovementMutation.isLoading ? 'Recording...' : 'Record Movement'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Inventory Modal Component
interface InventoryModalProps {
  inventory: InventoryType | null;
  products: Product[];
  locations: Location[];
  onSubmit: (data: InventoryCreate) => void;
  onClose: () => void;
  isLoading: boolean;
}

const InventoryModal: React.FC<InventoryModalProps> = ({ 
  inventory, 
  products, 
  locations, 
  onSubmit, 
  onClose, 
  isLoading 
}) => {
  const [formData, setFormData] = useState<InventoryCreate>({
    product_id: inventory?.product_id || 0,
    location_id: inventory?.location_id || 0,
    quantity: inventory?.quantity || 0,
    reserved_quantity: inventory?.reserved_quantity || 0,
    unit_cost: inventory?.unit_cost || 0,
    notes: inventory?.notes || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {inventory ? 'Edit Inventory Item' : 'Add Inventory Item'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Product</label>
              <select
                required
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: parseInt(e.target.value) })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <select
                required
                value={formData.location_id}
                onChange={(e) => setFormData({ ...formData, location_id: parseInt(e.target.value) })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select location</option>
                {locations.map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                <input
                  type="number"
                  required
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Reserved Quantity</label>
                <input
                  type="number"
                  value={formData.reserved_quantity}
                  onChange={(e) => setFormData({ ...formData, reserved_quantity: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Unit Cost</label>
              <input
                type="number"
                step="0.01"
                value={formData.unit_cost}
                onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
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
                {isLoading ? 'Saving...' : inventory ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InventoryPage; 