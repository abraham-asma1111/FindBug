'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { useApiMutation } from '@/hooks/useApiMutation';

interface AIRedTeamingEngagementCreateModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const modelTypes = [
  { value: 'llm', label: 'Large Language Model (LLM)' },
  { value: 'ml_model', label: 'ML Model' },
  { value: 'ai_agent', label: 'AI Agent' },
  { value: 'chatbot', label: 'Chatbot' },
  { value: 'recommendation_system', label: 'Recommendation System' },
  { value: 'computer_vision', label: 'Computer Vision' },
];

const attackTypes = [
  { value: 'prompt_injection', label: 'Prompt Injection' },
  { value: 'jailbreak', label: 'Jailbreaking' },
  { value: 'data_leakage', label: 'Data Leakage' },
  { value: 'model_extraction', label: 'Model Extraction' },
  { value: 'adversarial_input', label: 'Adversarial Input' },
  { value: 'bias_exploitation', label: 'Bias Exploitation' },
  { value: 'hallucination_trigger', label: 'Hallucination Trigger' },
  { value: 'context_manipulation', label: 'Context Manipulation' },
  { value: 'training_data_poisoning', label: 'Training Data Poisoning' },
  { value: 'model_inversion', label: 'Model Inversion' },
];

export default function AIRedTeamingEngagementCreateModal({
  onClose,
  onSuccess,
}: AIRedTeamingEngagementCreateModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    target_ai_system: '',
    model_type: 'llm',
    testing_environment: '',
    ethical_guidelines: '',
    scope_description: '',
    allowed_attack_types: [] as string[],
    start_date: '',
    end_date: '',
  });

  const { mutate: createEngagement, isLoading, error } = useApiMutation(
    '/ai-red-teaming/engagements',
    'POST'
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await createEngagement(formData);
      onSuccess();
    } catch (err) {
      // Error is handled by useApiMutation
    }
  };

  const handleAttackTypeToggle = (attackType: string) => {
    setFormData((prev) => ({
      ...prev,
      allowed_attack_types: prev.allowed_attack_types.includes(attackType)
        ? prev.allowed_attack_types.filter((t) => t !== attackType)
        : [...prev.allowed_attack_types, attackType],
    }));
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Create AI Red Teaming Engagement"
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Message */}
        {error && (
          <div className="rounded-lg border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
            {error.message || 'Failed to create engagement'}
          </div>
        )}

        {/* Engagement Name */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Engagement Name *
          </label>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., GPT-4 Security Assessment"
            required
          />
        </div>

        {/* Target AI System */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Target AI System *
          </label>
          <Input
            value={formData.target_ai_system}
            onChange={(e) => setFormData({ ...formData, target_ai_system: e.target.value })}
            placeholder="e.g., Customer Support Chatbot"
            required
          />
        </div>

        {/* Model Type */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Model Type *
          </label>
          <Select
            value={formData.model_type}
            onChange={(e) => setFormData({ ...formData, model_type: e.target.value })}
            required
          >
            {modelTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </div>

        {/* Testing Environment */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Testing Environment *
          </label>
          <Textarea
            value={formData.testing_environment}
            onChange={(e) => setFormData({ ...formData, testing_environment: e.target.value })}
            placeholder="Describe the testing environment (e.g., sandbox, staging, isolated instance)"
            rows={3}
            required
          />
        </div>

        {/* Ethical Guidelines */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Ethical Guidelines *
          </label>
          <Textarea
            value={formData.ethical_guidelines}
            onChange={(e) => setFormData({ ...formData, ethical_guidelines: e.target.value })}
            placeholder="Define ethical boundaries and testing constraints"
            rows={3}
            required
          />
        </div>

        {/* Scope Description */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Scope Description
          </label>
          <Textarea
            value={formData.scope_description}
            onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
            placeholder="Describe the testing scope and objectives"
            rows={3}
          />
        </div>

        {/* Allowed Attack Types */}
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
            Allowed Attack Types
          </label>
          <div className="grid grid-cols-2 gap-2">
            {attackTypes.map((type) => (
              <label
                key={type.value}
                className="flex items-center gap-2 rounded-lg border border-[#e6ddd4] dark:border-gray-700 p-3 cursor-pointer hover:bg-[#faf6f1] dark:hover:bg-slate-700 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={formData.allowed_attack_types.includes(type.value)}
                  onChange={() => handleAttackTypeToggle(type.value)}
                  className="rounded border-[#d8d0c8] text-[#2d2a26] focus:ring-[#2d2a26]"
                />
                <span className="text-sm text-[#2d2a26] dark:text-slate-100">
                  {type.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
              Start Date
            </label>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
              End Date
            </label>
            <Input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4] dark:border-gray-700">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Engagement'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
