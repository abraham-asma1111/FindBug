'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

interface CodeReviewEngagementCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const reviewTypes = [
  { value: 'security', label: 'Security Review' },
  { value: 'performance', label: 'Performance Review' },
  { value: 'best_practices', label: 'Best Practices' },
  { value: 'architecture', label: 'Architecture Review' },
  { value: 'full_review', label: 'Full Code Review' },
];

export default function CodeReviewEngagementCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: CodeReviewEngagementCreateModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    repository_url: '',
    review_type: 'security',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = () => {
    setFormData({
      title: '',
      repository_url: '',
      review_type: 'security',
    });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      await api.post('/code-review/engagements', {
        title: formData.title.trim(),
        repository_url: formData.repository_url.trim(),
        review_type: formData.review_type,
      });
      resetForm();
      onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string | { msg: string }[] } } };
      const detail = axiosErr.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Failed to create code review engagement.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      resetForm();
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Request Expert Code Review" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-600" />
              <div>
                <h4 className="font-semibold text-red-900">Error creating review request</h4>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        ) : null}

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-[#2d2a26]">
            Review title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            placeholder="e.g., Payment API security review"
          />
        </div>

        <div>
          <label htmlFor="repository_url" className="block text-sm font-medium text-[#2d2a26]">
            Repository URL <span className="text-red-500">*</span>
          </label>
          <input
            type="url"
            id="repository_url"
            required
            value={formData.repository_url}
            onChange={(e) => setFormData({ ...formData, repository_url: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            placeholder="https://github.com/org/repo"
          />
          <p className="mt-1.5 text-xs text-[#8b8177]">
            Grant the assigned reviewer read access before they start the review.
          </p>
        </div>

        <div>
          <label htmlFor="review_type" className="block text-sm font-medium text-[#2d2a26]">
            Review type <span className="text-red-500">*</span>
          </label>
          <select
            id="review_type"
            required
            value={formData.review_type}
            onChange={(e) => setFormData({ ...formData, review_type: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
          >
            {reviewTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end gap-3 border-t border-[#e6ddd4] pt-6">
          <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading} disabled={isLoading}>
            Request review
          </Button>
        </div>
      </form>
    </Modal>
  );
}
