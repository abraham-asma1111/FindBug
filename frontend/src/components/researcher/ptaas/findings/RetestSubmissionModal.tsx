'use client';

import { useState } from 'react';
import api from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { AlertCircle, CheckCircle, XCircle, Upload } from 'lucide-react';

interface RetestSubmissionModalProps {
  isOpen: boolean;
  onClose: () => void;
  findingId: string;
  findingTitle: string;
  retestNotes?: string;
  onSuccess: () => void;
}

export default function RetestSubmissionModal({
  isOpen,
  onClose,
  findingId,
  findingTitle,
  retestNotes,
  onSuccess
}: RetestSubmissionModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    retest_status: 'FIXED', // FIXED, NOT_FIXED, PARTIALLY_FIXED
    retest_notes: '',
    retest_evidence: '',
    retest_screenshots: [] as string[]
  });

  const handleSubmit = async () => {
    if (!formData.retest_notes || formData.retest_notes.length < 20) {
      alert('Please provide detailed retest notes (minimum 20 characters)');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.post(`/ptaas/findings/${findingId}/retest`, {
        ...formData
      });
      
      alert('Retest results submitted successfully!');
      onSuccess();
      onClose();
      
      // Reset form
      setFormData({
        retest_status: 'FIXED',
        retest_notes: '',
        retest_evidence: '',
        retest_screenshots: []
      });
    } catch (error: any) {
      alert(error.message || 'Failed to submit retest results');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Submit Retest Results"
      size="lg"
    >
      <div className="space-y-6">
        {/* Finding Info */}
        <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
          <h4 className="text-sm font-semibold text-[#2d2a26] mb-2">Finding</h4>
          <p className="text-sm text-[#2d2a26]">{findingTitle}</p>
        </div>

        {/* Original Retest Notes */}
        {retestNotes && (
          <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-orange-900 mb-1">Retest Request</h4>
                <p className="text-sm text-orange-700 whitespace-pre-wrap">{retestNotes}</p>
              </div>
            </div>
          </div>
        )}

        {/* Retest Status */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Retest Status <span className="text-red-500">*</span>
          </label>
          <Select
            value={formData.retest_status}
            onChange={(e) => setFormData(prev => ({ ...prev, retest_status: e.target.value }))}
          >
            <option value="FIXED">✓ Fixed - Vulnerability has been remediated</option>
            <option value="NOT_FIXED">✗ Not Fixed - Vulnerability still exists</option>
            <option value="PARTIALLY_FIXED">⚠ Partially Fixed - Some issues remain</option>
          </Select>
        </div>

        {/* Status-specific guidance */}
        {formData.retest_status === 'FIXED' && (
          <div className="rounded-xl border border-green-200 bg-green-50 p-4">
            <div className="flex gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h5 className="font-semibold text-green-900 mb-1">Vulnerability Fixed</h5>
                <p className="text-sm text-green-700">
                  Please confirm that you've thoroughly tested the fix and the vulnerability can no longer be exploited.
                </p>
              </div>
            </div>
          </div>
        )}

        {formData.retest_status === 'NOT_FIXED' && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex gap-3">
              <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h5 className="font-semibold text-red-900 mb-1">Vulnerability Not Fixed</h5>
                <p className="text-sm text-red-700">
                  Please provide detailed evidence showing that the vulnerability still exists and can be exploited.
                </p>
              </div>
            </div>
          </div>
        )}

        {formData.retest_status === 'PARTIALLY_FIXED' && (
          <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h5 className="font-semibold text-orange-900 mb-1">Partially Fixed</h5>
                <p className="text-sm text-orange-700">
                  Please explain which aspects have been fixed and which issues remain.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Retest Notes */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Retest Notes <span className="text-red-500">*</span>
          </label>
          <Textarea
            value={formData.retest_notes}
            onChange={(e) => setFormData(prev => ({ ...prev, retest_notes: e.target.value }))}
            placeholder="Describe your retest process and findings in detail..."
            rows={6}
            className="w-full"
          />
          <p className="mt-1 text-xs text-[#8b8177]">
            Minimum 20 characters. Include steps taken to verify the fix.
          </p>
        </div>

        {/* Retest Evidence */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Retest Evidence
          </label>
          <Textarea
            value={formData.retest_evidence}
            onChange={(e) => setFormData(prev => ({ ...prev, retest_evidence: e.target.value }))}
            placeholder="Provide technical evidence (logs, screenshots description, test results)..."
            rows={4}
            className="w-full"
          />
        </div>

        {/* Screenshot Upload Placeholder */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Screenshots (Optional)
          </label>
          <div className="border-2 border-dashed border-[#e6ddd4] rounded-xl p-6 text-center">
            <Upload className="h-8 w-8 text-[#8b8177] mx-auto mb-2" />
            <p className="text-sm text-[#6d6760] mb-1">Upload retest screenshots</p>
            <p className="text-xs text-[#8b8177]">PNG, JPG up to 10MB each</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            className="flex-1"
            isLoading={isSubmitting}
            disabled={!formData.retest_notes || formData.retest_notes.length < 20}
          >
            Submit Retest Results
          </Button>
        </div>
      </div>
    </Modal>
  );
}
