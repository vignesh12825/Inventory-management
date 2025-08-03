import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import apiService from '../services/api';
import { Location, LocationCreate, LocationUpdate } from '../types';

const Locations: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  const { data: locationsData, isLoading, error } = useQuery(
    ['locations', searchTerm],
    () => apiService.locations.getLocations({ search: searchTerm || undefined })
  );

  const createMutation = useMutation(
    (data: LocationCreate) => apiService.locations.createLocation(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('locations');
        setIsModalOpen(false);
      },
    }
  );

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: LocationUpdate }) =>
      apiService.locations.updateLocation(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('locations');
        setIsModalOpen(false);
        setEditingLocation(null);
      },
    }
  );

  const deleteMutation = useMutation(
    (id: number) => apiService.locations.deleteLocation(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('locations');
      },
    }
  );

  const toggleActiveMutation = useMutation(
    ({ id, isActive }: { id: number; isActive: boolean }) =>
      apiService.locations.updateLocation(id, { is_active: isActive }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('locations');
      },
    }
  );

  const handleSubmit = (formData: LocationCreate) => {
    if (editingLocation) {
      updateMutation.mutate({ id: editingLocation.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (location: Location) => {
    setEditingLocation(location);
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this location?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleToggleActive = (location: Location) => {
    toggleActiveMutation.mutate({ 
      id: location.id, 
      isActive: !location.is_active 
    });
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">Error loading locations</div>;

  const locations = locationsData?.data || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Locations</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Location
        </button>
      </div>

      {/* Search */}
      <div className="max-w-md">
        <input
          type="text"
          placeholder="Search locations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Locations Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {locations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No locations found. {searchTerm && `No results for "${searchTerm}"`}
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Code
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
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
              {locations.map((location) => (
                <tr key={location.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{location.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{location.code}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{location.address || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{location.warehouse_type || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleToggleActive(location)}
                      disabled={toggleActiveMutation.isLoading}
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full cursor-pointer transition-colors ${
                        location.is_active
                          ? 'bg-green-100 text-green-800 hover:bg-green-200'
                          : 'bg-red-100 text-red-800 hover:bg-red-200'
                      } ${toggleActiveMutation.isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      {location.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(location)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(location.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Location Modal */}
      {isModalOpen && (
        <LocationModal
          location={editingLocation}
          onSubmit={handleSubmit}
          onClose={() => {
            setIsModalOpen(false);
            setEditingLocation(null);
          }}
          isLoading={createMutation.isLoading || updateMutation.isLoading}
        />
      )}
    </div>
  );
};

// Location Modal Component
interface LocationModalProps {
  location: Location | null;
  onSubmit: (data: LocationCreate) => void;
  onClose: () => void;
  isLoading: boolean;
}

const LocationModal: React.FC<LocationModalProps> = ({ location, onSubmit, onClose, isLoading }) => {
  const [formData, setFormData] = useState<LocationCreate>({
    name: location?.name || '',
    code: location?.code || '',
    address: location?.address || '',
    warehouse_type: location?.warehouse_type || '',
  });

  const [isActive, setIsActive] = useState(location?.is_active ?? true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (location) {
      // For editing, include the is_active field
      onSubmit({ ...formData, is_active: isActive } as any);
    } else {
      // For creating, don't include is_active (it will default to true)
      onSubmit(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {location ? 'Edit Location' : 'Add Location'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Code</label>
              <input
                type="text"
                required
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Address</label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                rows={3}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Warehouse Type</label>
              <select
                value={formData.warehouse_type}
                onChange={(e) => setFormData({ ...formData, warehouse_type: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select type</option>
                <option value="main">Main Warehouse</option>
                <option value="secondary">Secondary Warehouse</option>
                <option value="retail">Retail Store</option>
                <option value="distribution">Distribution Center</option>
              </select>
            </div>
            {location && (
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Active</span>
                </label>
              </div>
            )}
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
                {isLoading ? 'Saving...' : location ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Locations; 