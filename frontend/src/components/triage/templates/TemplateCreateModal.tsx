'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

interface TemplateCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const categories = [
  { value: 'validation', label: 'Validation' },
  { value: 'rejection', label: 'Rejection' },
  { value: 'duplicate', label: 'Duplicate' },
  { value: 'need_info', label: 'Need Info' },
  { value: 'resolved', label: 'Resolved' },
];

export default function TemplateCreateModal({ isOpen, onClose }: TemplateCreateModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: '',
    title: '',
    content: '',
    category: 'validation',
  });
  const [error, setError] = useState<string | null>(null);

  const { mutate: createTemplate, isLoading } = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/triage/templates'] });
      setError(null);
      onClose();
      setFormData({ name: '', title: '', content: '', category: 'validation' });
    },
    onError: (err: Error) => {
      setError(err.message || 'Failed to create template');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTemplate({ 
      endpoint: '/triage/templates',
      name: formData.name,
      title: formData.title,
      content: formData.content,
      category: formData.category
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Template">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-[#EF4444]/10 border border-[#EF4444] rounded-lg p-3">
            <p className="text-sm text-[#EF4444]">{error}</p>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
            Template Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            placeholder="e.g., validation_accepted"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
            Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            placeholder="e.g., Report Validated"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
            Category
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
          >
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
            Content
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] min-h-[150px]"
            placeholder="Enter template content..."
            required
          />
        </div>

        <div className="flex gap-3 justify-end pt-4">
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Template'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
