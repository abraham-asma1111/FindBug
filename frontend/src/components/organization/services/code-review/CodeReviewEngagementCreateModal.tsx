'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { AlertCircle } from 'lucide-react';

interface CodeReviewEngagementCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const languages = [
  'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'C++', 'Other'
];

const reviewTypes = [
  { value: 'security', label: 'Security Review' },
  { value: 'full', label: 'Full Code Review' },
  { value: 'authentication', label: 'Authentication & Authorization' },
  { value: 'api', label: 'API Security' },
  { value: 'cryptography', label: 'Cryptography Review' },
];

export default function CodeReviewEngagementCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: CodeReviewEngagementCreateModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    repository_url: '',
    branch: 'main',
    language: 'JavaScript',
    review_type: 'security',
    end_date: '',
    focus_areas: '',
  });

  const { mutate: createEngagement, isLoading, error } = useApiMutation({
    endpoint: '/code-review/engagements',
    method: 'POST',
    onSuccess: () => {
      onSuccess();
      resetForm();
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      repository_url: '',
      branch: 'main',
      language: 'JavaScript',
      review_type: 'security',
      end_date: '',
      focus_areas: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createEngagement(formData);
  };

  const handleClose = () => {
    if (!isLoading) {
      resetForm();
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Request Code Review"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-red-900">Error creating review request</h4>
                <p className="mt-1 text-sm text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Review Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-[#2d2a26]">
            Review Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            placeholder="e.g., Authentication Module Security Review"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-[#2d2a26]">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="description"
            required
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            placeholder="Describe what you want reviewed..."
          />
        </div>

        {/* Repository URL */}
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
            placeholder="https://github.com/username/repository"
          />
          <p className="mt-1.5 text-xs text-[#8b8177]">
            Ensure the repository is accessible to reviewers
          </p>
        </div>

        {/* Branch & Language */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="branch" className="block text-sm font-medium text-[#2d2a26]">
              Branch <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="branch"
              required
              value={formData.branch}
              onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            />
          </div>
          <div>
            <label htmlFor="language" className="block text-sm font-medium text-[#2d2a26]">
              Primary Language <span className="text-red-500">*</span>
            </label>
            <select
              id="language"
              required
              value={formData.language}
              onChange={(e) => setFormData({ ...formData, language: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            >
              {languages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Review Type */}
        <div>
          <label htmlFor="review_type" className="block text-sm font-medium text-[#2d2a26]">
            Review Type <span className="text-red-500">*</span>
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

        {/* Deadline */}
        <div>
          <label htmlFor="end_date" className="block text-sm font-medium text-[#2d2a26]">
            Review Deadline <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            id="end_date"
            required
            value={formData.end_date}
            onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
          />
        </div>

        {/* Focus Areas */}
        <div>
          <label htmlFor="focus_areas" className="block text-sm font-medium text-[#2d2a26]">
            Focus Areas
          </label>
          <textarea
            id="focus_areas"
            rows={3}
            value={formData.focus_areas}
            onChange={(e) => setFormData({ ...formData, focus_areas: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#10b981] focus:outline-none focus:ring-2 focus:ring-[#10b981]/20"
            placeholder="Specific files, modules, or security concerns to focus on..."
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 border-t border-[#e6ddd4] pt-6">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={isLoading}
            disabled={isLoading}
          >
            Request Review
          </Button>
        </div>
      </form>
    </Modal>
  );
}
