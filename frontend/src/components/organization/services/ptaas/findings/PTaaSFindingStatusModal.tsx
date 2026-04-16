'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';

interface StatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  currentStatus: string;
  onSuccess: () => void;
}

const STATUS_OPTIONS = [
  { value: 'submitted', label: 'Submitted', color: 'bg-gray-100 text-gray-700' },
  { value: 'triaged', label: 'Triaged', color: 'bg-blue-100 text-blue-700' },
  { value: 'accepted', label: 'Accepted', color: 'bg-green-100 text-green-700' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'fixed', label: 'Fixed', color: 'bg-purple-100 text-purple-700' },
  { value: 'retest', label: 'Retest', color: 'bg-orange-100 text-orange-700' },
  { value: 'closed', label: 'Closed', color: 'bg-gray-100 text-gray-700' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-700' },
];

export default function PTaaSFindingStatusModal({
  isOpen,
  onClose,
  findingId,
  currentStatus,
  onSuccess,
}: StatusModalProps) {
  const [status, setStatus] = useState(currentStatus);
  const [notes, setNotes] = useState('');
  const { showToast } = useToast();

  const { mutate: updateStatus, isLoading } = useApiMutation(
    `/ptaas/findings/${findingId}`,
    'PATCH',
    {
      onSuccess: () => {
        showToast('Status updated successfully', 'success');
        onSuccess();
        onClose();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to update status', 'error');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateStatus({ status, status_notes: notes });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Change Finding Status">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Current Status
          </label>
          <div className="flex items-center gap-2 mb-4">
            {STATUS_OPTIONS.find((s) => s.value === currentStatus) && (
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
                  STATUS_OPTIONS.find((s) => s.value === currentStatus)?.color
                }`}
              >
                {STATUS_OPTIONS.find((s) => s.value === currentStatus)?.label}
              </span>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            New Status
          </label>
          <Select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            required
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Notes
          </label>
          <Textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Explain the reason for status change..."
            rows={4}
            required
          />
        </div>

        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
          <p className="text-sm text-blue-700">
            Status changes are tracked and will appear in the finding timeline.
          </p>
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading} className="flex-1">
            Update Status
          </Button>
        </div>
      </form>
    </Modal>
  );
}
