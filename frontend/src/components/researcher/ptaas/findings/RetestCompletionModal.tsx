'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';
import { CheckCircle, XCircle, AlertTriangle, FileText, Upload } from 'lucide-react';

interface RetestCompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
  retestId: string;
  findingTitle: string;
  fixDescription: string;
  onSuccess?: () => void;
}

type RetestResult = 'FIXED' | 'NOT_FIXED' | 'PARTIALLY_FIXED' | 'NEW_ISSUE';

const resultOptions: { value: RetestResult; label: string; description: string; icon: any; color: string }[] = [
  {
    value: 'FIXED',
    label: 'Fixed',
    description: 'The vulnerability has been completely resolved',
    icon: CheckCircle,
    color: 'border-green-200 bg-green-50 hover:bg-green-100 text-green-900'
  },
  {
    value: 'NOT_FIXED',
    label: 'Not Fixed',
    description: 'The vulnerability still exists and has not been addressed',
    icon: XCircle,
    color: 'border-red-200 bg-red-50 hover:bg-red-100 text-red-900'
  },
  {
    value: 'PARTIALLY_FIXED',
    label: 'Partially Fixed',
    description: 'Some aspects fixed, but issues remain',
    icon: AlertTriangle,
    color: 'border-orange-200 bg-orange-50 hover:bg-orange-100 text-orange-900'
  },
  {
    value: 'NEW_ISSUE',
    label: 'New Issue Found',
    description: 'Fix introduced new security concerns',
    icon: AlertTriangle,
    color: 'border-purple-200 bg-purple-50 hover:bg-purple-100 text-purple-900'
  }
];

export default function RetestCompletionModal({
  isOpen,
  onClose,
  retestId,
  findingTitle,
  fixDescription,
  onSuccess
}: RetestCompletionModalProps) {
  const [selectedResult, setSelectedResult] = useState<RetestResult | null>(null);
  const [retestNotes, setRetestNotes] = useState('');
  const [evidenceUrls, setEvidenceUrls] = useState<string[]>(['']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddEvidenceUrl = () => {
    setEvidenceUrls([...evidenceUrls, '']);
  };

  const handleRemoveEvidenceUrl = (index: number) => {
    setEvidenceUrls(evidenceUrls.filter((_, i) => i !== index));
  };

  const handleEvidenceUrlChange = (index: number, value: string) => {
    const newUrls = [...evidenceUrls];
    newUrls[index] = value;
    setEvidenceUrls(newUrls);
  };

  const handleSubmit = async () => {
    if (!selectedResult) {
      setError('Please select a retest result');
      return;
    }

    if (!retestNotes.trim() || retestNotes.trim().length < 20) {
      setError('Please provide detailed retest notes (minimum 20 characters)');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Filter out empty URLs
      const validUrls = evidenceUrls.filter(url => url.trim() !== '');

      // Build request payload - only include retest_evidence if there are valid URLs
      const payload: any = {
        retest_result: selectedResult,
        retest_notes: retestNotes.trim()
      };
      
      if (validUrls.length > 0) {
        payload.retest_evidence = validUrls;
      }

      await api.post(`/ptaas/retests/${retestId}/complete`, payload);

      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit retest results');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setSelectedResult(null);
      setRetestNotes('');
      setEvidenceUrls(['']);
      setError(null);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Complete Retest" size="lg">
      <div className="space-y-6">
        {/* Finding Info */}
        <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
          <h3 className="font-semibold text-[#2d2a26] mb-2">{findingTitle}</h3>
          <div className="mt-3">
            <label className="text-xs font-medium text-[#8b8177] uppercase tracking-wide">
              Organization's Fix Description
            </label>
            <p className="mt-1 text-sm text-[#2d2a26] whitespace-pre-wrap">{fixDescription}</p>
          </div>
        </div>

        {/* Result Selection */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-3">
            Retest Result <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 gap-3">
            {resultOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = selectedResult === option.value;
              
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setSelectedResult(option.value)}
                  className={`flex items-start gap-3 p-4 rounded-xl border-2 transition-all text-left ${
                    isSelected
                      ? `${option.color} border-current`
                      : 'border-[#e6ddd4] bg-white hover:bg-[#faf6f1]'
                  }`}
                >
                  <Icon className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                    isSelected ? 'opacity-100' : 'opacity-50'
                  }`} />
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{option.label}</div>
                    <div className={`text-xs mt-1 ${
                      isSelected ? 'opacity-90' : 'text-[#6d6760]'
                    }`}>
                      {option.description}
                    </div>
                  </div>
                  {isSelected && (
                    <div className="flex-shrink-0">
                      <div className="h-5 w-5 rounded-full bg-current flex items-center justify-center">
                        <CheckCircle className="h-3 w-3 text-white" />
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Retest Notes */}
        <div>
          <label htmlFor="retestNotes" className="block text-sm font-medium text-[#2d2a26] mb-2">
            Detailed Retest Notes <span className="text-red-500">*</span>
          </label>
          <textarea
            id="retestNotes"
            value={retestNotes}
            onChange={(e) => setRetestNotes(e.target.value)}
            rows={6}
            className="w-full px-4 py-3 rounded-xl border border-[#e6ddd4] bg-white text-[#2d2a26] placeholder-[#8b8177] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Provide detailed notes about your retest findings:&#10;- What tests did you perform?&#10;- What were the results?&#10;- Any additional observations?&#10;- Recommendations for the organization?"
          />
          <p className="mt-1 text-xs text-[#8b8177]">
            Minimum 20 characters • {retestNotes.length} characters
          </p>
        </div>

        {/* Evidence URLs */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Retest Evidence (Optional)
          </label>
          <p className="text-xs text-[#6d6760] mb-3">
            Add URLs to screenshots, videos, or other evidence documenting your retest
          </p>
          <div className="space-y-2">
            {evidenceUrls.map((url, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => handleEvidenceUrlChange(index, e.target.value)}
                  placeholder="https://example.com/evidence.png"
                  className="flex-1 px-4 py-2 rounded-lg border border-[#e6ddd4] bg-white text-[#2d2a26] placeholder-[#8b8177] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
                {evidenceUrls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveEvidenceUrl(index)}
                    className="px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors text-sm"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={handleAddEvidenceUrl}
            className="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg border border-[#e6ddd4] text-[#2d2a26] hover:bg-[#faf6f1] transition-colors text-sm"
          >
            <Upload className="h-4 w-4" />
            Add Another URL
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex gap-3">
              <XCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isSubmitting}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !selectedResult || retestNotes.trim().length < 20}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Submitting...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Submit Retest Results
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
