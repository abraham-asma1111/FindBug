'use client';

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiQuery';
import { useToast } from '@/components/ui/Toast';
import { RefreshCw } from 'lucide-react';

interface PTaaSRetestModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  findingTitle: string;
  onSuccess?: () => void;
}

export default function PTaaSRetestModal({
  isOpen,
  onClose,
  findingId,
  findingTitle,
  onSuccess,
}: PTaaSRetestModalProps) {
  const { showToast } = useToast();
  const [notes, setNotes] = useState('');
  const [selectedResearcher, setSelectedResearcher] = useState('');

  const retestMutation = useApiMutation(
    `/ptaas/findings/${findingId}/retest`,
    'POST',
    {
      onSuccess: () => {
        showToast('Retest requested successfully', 'success');
        onClose();
        setNotes('');
        setSelectedResearcher('');
        onSuccess?.();
      },
      onError: (error: any) => {
        showToast(error.message || 'Failed to request retest', 'error');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    retestMutation.mutate({
      retest_notes: notes,
      assigned_researcher_id: selectedResearcher || null,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Request Retest">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <p className="text-sm text-[#6b6662] dark:text-[#a39e9a] mb-4">
            Request a retest for: <span className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">{findingTitle}</span>
          </p>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1]">
            Assign to Researcher (Optional)
          </label>
          <select
            value={selectedResearcher}
            onChange={(e) => setSelectedResearcher(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-[#e6ddd4] dark:border-[#3d3a36] bg-white dark:bg-[#2d2a26] text-[#2d2a26] dark:text-[#faf6f1] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]"
          >
            <option value="">Select researcher...</option>
            <option value="researcher-1">Researcher 1</option>
            <option value="researcher-2">Researcher 2</option>
            <option value="researcher-3">Researcher 3</option>
          </select>
          <p className="text-xs text-[#6b6662] dark:text-[#a39e9a]">
            Leave empty to assign automatically
          </p>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1]">
            Retest Notes <span className="text-red-500">*</span>
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Describe what needs to be retested and any specific instructions..."
            rows={4}
            required
            className="w-full px-4 py-3 rounded-lg border border-[#e6ddd4] dark:border-[#3d3a36] bg-white dark:bg-[#2d2a26] text-[#2d2a26] dark:text-[#faf6f1] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]"
          />
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            Retest Policy
          </h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>• Critical findings: Unlimited retests</li>
            <li>• High findings: Up to 3 retests</li>
            <li>• Medium/Low findings: Up to 2 retests</li>
            <li>• Retest must be completed within 7 days</li>
          </ul>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4] dark:border-[#3d3a36]">
          <Button
            type="button"
            onClick={onClose}
            variant="outline"
            disabled={retestMutation.isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={!notes.trim() || retestMutation.isLoading}
            className="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
          >
            {retestMutation.isLoading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Requesting...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Request Retest
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
