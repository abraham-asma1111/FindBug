'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { AlertCircle } from 'lucide-react';

interface AIRedTeamingEngagementCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const modelTypes = [
  { value: 'llm', label: 'Large Language Model (LLM)' },
  { value: 'ml_model', label: 'Machine Learning Model' },
  { value: 'ai_agent', label: 'AI Agent' },
  { value: 'chatbot', label: 'Chatbot' },
  { value: 'recommendation_system', label: 'Recommendation System' },
  { value: 'computer_vision', label: 'Computer Vision' },
];

const testingFocus = [
  'Prompt Injection',
  'Jailbreaking',
  'Data Leakage',
  'Model Manipulation',
  'Bias Detection',
  'Adversarial Attacks',
  'Privacy Violations',
  'Hallucination Testing',
];

export default function AIRedTeamingEngagementCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: AIRedTeamingEngagementCreateModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_ai_system: '',
    model_type: 'llm',
    start_date: '',
    end_date: '',
    testing_objectives: '',
    access_requirements: '',
  });

  const { mutate: createEngagement, isLoading, error } = useApiMutation({
    endpoint: '/ai-red-teaming/engagements',
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
      target_ai_system: '',
      model_type: 'llm',
      start_date: '',
      end_date: '',
      testing_objectives: '',
      access_requirements: '',
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
      title="Create AI Red Teaming Engagement"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-red-900">Error creating engagement</h4>
                <p className="mt-1 text-sm text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Engagement Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-[#2d2a26]">
            Engagement Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            placeholder="e.g., ChatBot Security Assessment Q2 2026"
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
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            placeholder="Describe the AI system and testing objectives..."
          />
        </div>

        {/* Target AI System */}
        <div>
          <label htmlFor="target_ai_system" className="block text-sm font-medium text-[#2d2a26]">
            Target AI System <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="target_ai_system"
            required
            value={formData.target_ai_system}
            onChange={(e) => setFormData({ ...formData, target_ai_system: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            placeholder="e.g., Customer Support AI Assistant"
          />
        </div>

        {/* Model Type */}
        <div>
          <label htmlFor="model_type" className="block text-sm font-medium text-[#2d2a26]">
            Model Type <span className="text-red-500">*</span>
          </label>
          <select
            id="model_type"
            required
            value={formData.model_type}
            onChange={(e) => setFormData({ ...formData, model_type: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
          >
            {modelTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Timeline */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-[#2d2a26]">
              Start Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="start_date"
              required
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            />
          </div>
          <div>
            <label htmlFor="end_date" className="block text-sm font-medium text-[#2d2a26]">
              End Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="end_date"
              required
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            />
          </div>
        </div>

        {/* Testing Objectives */}
        <div>
          <label htmlFor="testing_objectives" className="block text-sm font-medium text-[#2d2a26]">
            Testing Objectives <span className="text-red-500">*</span>
          </label>
          <textarea
            id="testing_objectives"
            required
            rows={4}
            value={formData.testing_objectives}
            onChange={(e) => setFormData({ ...formData, testing_objectives: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            placeholder="Describe what you want to test (e.g., prompt injection, jailbreaking, data leakage)..."
          />
          <div className="mt-2 flex flex-wrap gap-2">
            <p className="w-full text-xs text-[#8b8177]">Common testing areas:</p>
            {testingFocus.map((focus) => (
              <span
                key={focus}
                className="inline-block rounded-lg bg-purple-50 px-2 py-1 text-xs text-purple-700"
              >
                {focus}
              </span>
            ))}
          </div>
        </div>

        {/* Access Requirements */}
        <div>
          <label htmlFor="access_requirements" className="block text-sm font-medium text-[#2d2a26]">
            Access Requirements
          </label>
          <textarea
            id="access_requirements"
            rows={3}
            value={formData.access_requirements}
            onChange={(e) => setFormData({ ...formData, access_requirements: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#8b5cf6] focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/20"
            placeholder="Describe how experts will access the AI system (API keys, credentials, environment setup)..."
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
            Create Engagement
          </Button>
        </div>
      </form>
    </Modal>
  );
}
