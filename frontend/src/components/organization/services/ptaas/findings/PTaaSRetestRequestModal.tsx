'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';
import { RefreshCcw, AlertCircle } from 'lucide-react';

interface RetestRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  onSuccess: () => void;
}

export default function PTaaSRetestRequestModal({
  isOpen,
  onClose,
  findingId,
  onSuccess,
}: RetestRequestModalProps) {
  const [fixDescription, setFixDescription] = useState('');
  const { showToast } = useToast();

  const { mutate: requestRetest, isLoading } = useApiMutation(
    `/ptaas/findings/${findingId}/request-retest`,
    'POST',
    {
      onSuccess: () => {
        showToast('Retest requested successfully', 'success');
        onSuccess();
        onClose();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to request retest', 'error');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (fixDescription.length < 10) {
      showToast('Fix description must be at least 10 characters', 'error');
      return;
    }
    requestRetest({ fix_description: fixDescription });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Request Retest">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
          <div className="flex gap-3">
            <RefreshCcw className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Verify Fix</h4>
              <p className="text-sm text-blue-700">
                You are requesting the researcher to retest this finding to confirm your fix.
                Please provide detailed information on what was changed.
              </p>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Fix Description & Instructions
          </label>
          <Textarea
            value={fixDescription}
            onChange={(e) => setFixDescription(e.target.value)}
            placeholder="Describe what was fixed, changed endpoints, new deployment details, or testing instructions..."
            rows={5}
            required
            className="w-full bg-[#faf6f1] border-[#e6ddd4] focus:border-blue-500 rounded-lg"
          />
        </div>

        <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white">
            Request Retest
          </Button>
        </div>
      </form>
    </Modal>
  );
}
