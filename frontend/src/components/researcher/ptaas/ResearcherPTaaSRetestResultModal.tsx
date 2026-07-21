'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useToast } from '@/components/ui/Toast';
import { RefreshCcw, CheckCircle, AlertCircle } from 'lucide-react';

interface ResearcherPTaaSRetestResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  onSuccess: () => void;
}

export default function ResearcherPTaaSRetestResultModal({
  isOpen,
  onClose,
  findingId,
  onSuccess,
}: ResearcherPTaaSRetestResultModalProps) {
  const [retestStatus, setRetestStatus] = useState('FIXED');
  const [retestNotes, setRetestNotes] = useState('');
  const { showToast } = useToast();

  const { mutate: submitRetestResult, isLoading } = useApiMutation(
    `/ptaas/findings/${findingId}/submit-retest`,
    'POST',
    {
      onSuccess: () => {
        showToast('Retest result submitted successfully', 'success');
        onSuccess();
        onClose();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to submit retest result', 'error');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (retestNotes.length < 10) {
      showToast('Retest notes must be at least 10 characters', 'error');
      return;
    }
    // Backend schema: PTaaSRetestResultSubmit expects is_fixed (bool) + retest_notes
    submitRetestResult({
      is_fixed: retestStatus === 'FIXED',
      retest_notes: retestNotes,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Submit Retest Result">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
          <div className="flex gap-3">
            <RefreshCcw className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Verify Fix Implementation</h4>
              <p className="text-sm text-blue-700">
                Submit your retest findings. Indicate if the vulnerability is fully resolved and describe your verification process in detail.
              </p>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Retest Outcome
          </label>
          <Select
            value={retestStatus}
            onChange={(e) => setRetestStatus(e.target.value)}
            required
            className="w-full"
          >
            <option value="FIXED">✅ Fixed — Vulnerability is fully remediated</option>
            <option value="NOT_FIXED">❌ Not Fixed — Vulnerability is still exploitable</option>
            <option value="PARTIALLY_FIXED">⚠️ Partially Fixed — Incomplete or bypassable</option>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Verification Notes & Evidence
          </label>
          <Textarea
            value={retestNotes}
            onChange={(e) => setRetestNotes(e.target.value)}
            placeholder="Describe your testing process, tools used, payloads attempted, and confirmation of the fix status..."
            rows={5}
            required
            className="w-full"
          />
          <p className="mt-1 text-xs text-[#8b8177]">{retestNotes.length}/10 minimum characters</p>
        </div>

        <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button type="button" variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={isLoading}
            className={`flex-1 text-white ${
              retestStatus === 'FIXED'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-orange-600 hover:bg-orange-700'
            }`}
          >
            {retestStatus === 'FIXED' ? (
              <><CheckCircle className="h-4 w-4 mr-2 inline" /> Confirm Fixed</>
            ) : (
              <><AlertCircle className="h-4 w-4 mr-2 inline" /> Report Not Fixed</>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
