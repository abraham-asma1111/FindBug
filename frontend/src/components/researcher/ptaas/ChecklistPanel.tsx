'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import Modal from '@/components/ui/Modal';
import { CheckCircle, Circle, FileText, Link as LinkIcon } from 'lucide-react';

interface ChecklistItem {
  id: string;
  phase_id: string;
  engagement_id: string;
  item_name: string;
  description: string;
  category: string;
  is_completed: boolean;
  is_required: boolean;
  completed_by?: string;
  completed_at?: string;
  notes?: string;
  evidence_url?: string;
}

interface ChecklistPanelProps {
  phaseId: string;
  engagementId: string;
  onUpdate: () => void;
}

export default function ChecklistPanel({ phaseId, engagementId, onUpdate }: ChecklistPanelProps) {
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ChecklistItem | null>(null);
  const [notes, setNotes] = useState('');
  const [evidenceUrl, setEvidenceUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: checklist, isLoading, error } = useApiQuery<ChecklistItem[]>({
    endpoint: `/ptaas/phases/${phaseId}/checklist`,
    queryKey: ['ptaas-checklist', phaseId],
  });

  const handleCompleteClick = (item: ChecklistItem) => {
    setSelectedItem(item);
    setNotes('');
    setEvidenceUrl('');
    setShowCompleteModal(true);
  };

  const handleCompleteItem = async () => {
    if (!selectedItem) return;

    setIsSubmitting(true);
    try {
      await api.post(`/ptaas/checklist/${selectedItem.id}/complete`, {
        notes: notes || undefined,
        evidence_url: evidenceUrl || undefined,
      });
      alert('Checklist item completed!');
      setShowCompleteModal(false);
      onUpdate(); // Refresh parent to update phase progress
    } catch (error: any) {
      alert(error.message || 'Failed to complete checklist item');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 bg-[#faf6f1] rounded animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-600">
        Failed to load checklist items
      </div>
    );
  }

  if (!checklist || checklist.length === 0) {
    return (
      <div className="text-center py-6 text-sm text-[#6d6760]">
        No checklist items for this phase
      </div>
    );
  }

  const completedCount = checklist.filter(item => item.is_completed).length;
  const requiredCount = checklist.filter(item => item.is_required).length;
  const completedRequired = checklist.filter(item => item.is_required && item.is_completed).length;

  return (
    <div className="space-y-4">
      {/* Progress Summary */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-[#6d6760]">
          {completedCount} of {checklist.length} items completed
          {requiredCount > 0 && ` (${completedRequired}/${requiredCount} required)`}
        </span>
      </div>

      {/* Checklist Items */}
      <div className="space-y-2">
        {checklist.map((item) => (
          <div
            key={item.id}
            className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
              item.is_completed
                ? 'bg-green-50 border-green-200'
                : 'bg-white border-[#e6ddd4] hover:bg-[#faf6f1]'
            }`}
          >
            {/* Checkbox */}
            <button
              onClick={() => !item.is_completed && handleCompleteClick(item)}
              disabled={item.is_completed}
              className="flex-shrink-0 mt-0.5"
            >
              {item.is_completed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <Circle className="h-5 w-5 text-[#8b8177] hover:text-blue-600" />
              )}
            </button>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <h5 className={`text-sm font-medium ${
                    item.is_completed ? 'text-green-900 line-through' : 'text-[#2d2a26]'
                  }`}>
                    {item.item_name}
                    {item.is_required && (
                      <span className="ml-2 text-xs text-red-600">*Required</span>
                    )}
                  </h5>
                  {item.description && (
                    <p className="text-xs text-[#6d6760] mt-1">{item.description}</p>
                  )}
                  {item.category && (
                    <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700">
                      {item.category}
                    </span>
                  )}
                </div>
              </div>

              {/* Completion Info */}
              {item.is_completed && (
                <div className="mt-2 pt-2 border-t border-green-200">
                  <div className="flex items-center gap-4 text-xs text-green-700">
                    <span>
                      Completed {item.completed_at && new Date(item.completed_at).toLocaleDateString()}
                    </span>
                    {item.notes && (
                      <div className="flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        <span>Has notes</span>
                      </div>
                    )}
                    {item.evidence_url && (
                      <div className="flex items-center gap-1">
                        <LinkIcon className="h-3 w-3" />
                        <span>Has evidence</span>
                      </div>
                    )}
                  </div>
                  {item.notes && (
                    <p className="mt-1 text-xs text-green-800 italic">
                      "{item.notes}"
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Complete Item Modal */}
      <Modal
        isOpen={showCompleteModal}
        onClose={() => setShowCompleteModal(false)}
        title="Complete Checklist Item"
      >
        {selectedItem && (
          <div className="space-y-4">
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
              <h4 className="font-semibold text-blue-900 mb-1">{selectedItem.item_name}</h4>
              {selectedItem.description && (
                <p className="text-sm text-blue-700">{selectedItem.description}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">
                Notes (Optional)
              </label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                placeholder="Add any notes about completing this item..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">
                Evidence URL (Optional)
              </label>
              <input
                type="url"
                value={evidenceUrl}
                onChange={(e) => setEvidenceUrl(e.target.value)}
                className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com/evidence"
              />
              <p className="mt-1 text-xs text-[#8b8177]">
                Link to screenshots, documents, or other evidence
              </p>
            </div>

            <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
              <Button
                variant="outline"
                onClick={() => setShowCompleteModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleCompleteItem}
                isLoading={isSubmitting}
                className="flex-1"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Mark Complete
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
