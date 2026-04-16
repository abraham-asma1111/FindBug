'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';

interface AssignModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  onSuccess: () => void;
}

export default function PTaaSFindingAssignModal({
  isOpen,
  onClose,
  findingId,
  onSuccess,
}: AssignModalProps) {
  const [assignedTo, setAssignedTo] = useState('');
  const [notes, setNotes] = useState('');
  const { showToast } = useToast();

  const { mutate: assignFinding, isLoading } = useApiMutation(
    `/ptaas/findings/${findingId}/assign`,
    'POST',
    {
      onSuccess: () => {
        showToast('Finding assigned successfully', 'success');
        onSuccess();
        onClose();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to assign finding', 'error');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignedTo) {
      showToast('Please select a team member', 'error');
      return;
    }
    assignFinding({ assigned_to: assignedTo, notes });
  };

  // Mock team members - in real app, fetch from API
  const teamMembers = [
    { id: '1', name: 'John Doe', role: 'Security Engineer' },
    { id: '2', name: 'Jane Smith', role: 'Senior Developer' },
    { id: '3', name: 'Mike Johnson', role: 'DevOps Engineer' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Finding">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Assign To
          </label>
          <Select
            value={assignedTo}
            onChange={(e) => setAssignedTo(e.target.value)}
            required
          >
            <option value="">Select team member...</option>
            {teamMembers.map((member) => (
              <option key={member.id} value={member.id}>
                {member.name} - {member.role}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Notes (Optional)
          </label>
          <Textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any notes or instructions..."
            rows={3}
          />
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
            Assign Finding
          </Button>
        </div>
      </form>
    </Modal>
  );
}
