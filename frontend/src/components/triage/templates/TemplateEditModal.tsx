'use client';

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

interface Template {
  id: string;
  name: string;
  title: string;
  content: string;
  category: string;
  is_active: boolean;
}

interface TemplateEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  template: Template | null;
}

const categories = [
  { value: 'validation', label: 'Validation' },
  { value: 'rejection', label: 'Rejection' },
  { value: 'duplicate', label: 'Duplicate' },
  { value: 'need_info', label: 'Need Info' },
  { value: 'resolved', label: 'Resolved' },
];

export default function TemplateEditModal({ isOpen, onClose, template }: TemplateEditModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: '',
    title: '',
    content: '',
    category: 'validation',
    is_active: true,
  });

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        title: template.title,
        content: template.content,
        category: template.category,
        is_active: template.is_active,
      });
    }
  }, [template]);

  const { mutate: updateTemplate, isLoading } = useApiMutation({
    method: 'PUT',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/triage/templates'] });
      onClose();
    },
    onError: (error: Error) => {
      console.error('Update error:', error);
      alert(`Failed to update: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!template) return;
    updateTemplate({ 
      endpoint: `/triage/templates/${template.id}`,
      name: formData.name,
      title: formData.title,
      content: formData.content,
      category: formData.category,
      is_active: formData.is_active
    });
  };

  if (!template) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Template">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
            Template Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
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
            required
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            className="w-4 h-4 rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6]"
          />
          <label htmlFor="is_active" className="text-sm text-[#F8FAFC]">
            Active
          </label>
        </div>

        <div className="flex gap-3 justify-end pt-4">
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Updating...' : 'Update Template'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
