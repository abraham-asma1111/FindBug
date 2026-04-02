'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { useApiMutation } from '@/hooks/useApiMutation';

interface ScopeAddModalProps {
  programId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ScopeAddModal({ programId, onClose, onSuccess }: ScopeAddModalProps) {
  const [assetType, setAssetType] = useState('web_app');
  const [assetIdentifier, setAssetIdentifier] = useState('');
  const [isInScope, setIsInScope] = useState(true);
  const [description, setDescription] = useState('');

  const { mutate: addScope, isLoading, error } = useApiMutation(
    `/programs/${programId}/scopes`,
    'POST',
    {
      onSuccess: () => {
        alert('Scope added successfully!');
        onSuccess();
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!assetIdentifier.trim()) {
      alert('Please enter an asset identifier');
      return;
    }

    addScope({
      asset_type: assetType,
      asset_identifier: assetIdentifier.trim(),
      is_in_scope: isInScope,
      description: description.trim() || undefined,
    });
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Add Scope" size="md">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
            <p className="text-sm text-[#b42318]">{error.message}</p>
          </div>
        )}

        <div>
          <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
            Asset Type
          </label>
          <Select
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
            required
          >
            <option value="web_app">Web Application</option>
            <option value="api">API</option>
            <option value="mobile_app">Mobile App</option>
            <option value="domain">Domain</option>
            <option value="other">Other</option>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
            Asset Identifier *
          </label>
          <Input
            type="text"
            value={assetIdentifier}
            onChange={(e) => setAssetIdentifier(e.target.value)}
            placeholder="e.g., example.com, 192.168.1.1, com.example.app"
            required
          />
          <p className="text-xs text-[#8b8177] mt-1">
            Domain, IP address, app identifier, or other unique identifier
          </p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
            Scope Status
          </label>
          <Select
            value={isInScope ? 'in' : 'out'}
            onChange={(e) => setIsInScope(e.target.value === 'in')}
          >
            <option value="in">In Scope</option>
            <option value="out">Out of Scope</option>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
            Description (Optional)
          </label>
          <Input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Additional notes about this asset"
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Adding...' : 'Add Scope'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
