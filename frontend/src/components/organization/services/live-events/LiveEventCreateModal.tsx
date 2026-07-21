'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { AlertCircle } from 'lucide-react';

interface LiveEventCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function LiveEventCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: LiveEventCreateModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_time: '',
    end_time: '',
    max_participants: '50',
    prize_pool: '',
    scope_description: '',
    target_assets: '',
    reward_policy: '',
  });

  const { mutate: createEvent, isLoading, error } = useApiMutation({
    endpoint: '/live-events',
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
      start_time: '',
      end_time: '',
      max_participants: '50',
      prize_pool: '',
      scope_description: '',
      target_assets: '',
      reward_policy: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createEvent({
      ...formData,
      max_participants: parseInt(formData.max_participants),
      prize_pool: formData.prize_pool ? parseFloat(formData.prize_pool) : undefined,
    });
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
      title="Create Live Hacking Event"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-red-900">Error creating event</h4>
                <p className="mt-1 text-sm text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Event Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-[#2d2a26]">
            Event Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            placeholder="e.g., Spring 2026 Bug Bash"
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
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            placeholder="Describe the event, objectives, and what participants can expect..."
          />
        </div>

        {/* Event Schedule */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="start_time" className="block text-sm font-medium text-[#2d2a26]">
              Start Time <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              id="start_time"
              required
              value={formData.start_time}
              onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            />
          </div>
          <div>
            <label htmlFor="end_time" className="block text-sm font-medium text-[#2d2a26]">
              End Time <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              id="end_time"
              required
              value={formData.end_time}
              onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            />
          </div>
        </div>

        {/* Participants & Prize Pool */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="max_participants" className="block text-sm font-medium text-[#2d2a26]">
              Max Participants <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="max_participants"
              required
              min="1"
              value={formData.max_participants}
              onChange={(e) => setFormData({ ...formData, max_participants: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            />
          </div>
          <div>
            <label htmlFor="prize_pool" className="block text-sm font-medium text-[#2d2a26]">
              Prize Pool (ETB)
            </label>
            <input
              type="number"
              id="prize_pool"
              min="0"
              step="0.01"
              value={formData.prize_pool}
              onChange={(e) => setFormData({ ...formData, prize_pool: e.target.value })}
              className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
              placeholder="0.00"
            />
          </div>
        </div>

        {/* Scope Description */}
        <div>
          <label htmlFor="scope_description" className="block text-sm font-medium text-[#2d2a26]">
            Scope Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="scope_description"
            required
            rows={3}
            value={formData.scope_description}
            onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            placeholder="Define what's in scope for testing during the event..."
          />
        </div>

        {/* Target Assets */}
        <div>
          <label htmlFor="target_assets" className="block text-sm font-medium text-[#2d2a26]">
            Target Assets <span className="text-red-500">*</span>
          </label>
          <textarea
            id="target_assets"
            required
            rows={3}
            value={formData.target_assets}
            onChange={(e) => setFormData({ ...formData, target_assets: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            placeholder="List URLs, IP ranges, applications, or systems to be tested..."
          />
          <p className="mt-1.5 text-xs text-[#8b8177]">
            Provide clear target information for participants
          </p>
        </div>

        {/* Reward Policy */}
        <div>
          <label htmlFor="reward_policy" className="block text-sm font-medium text-[#2d2a26]">
            Reward Policy
          </label>
          <textarea
            id="reward_policy"
            rows={3}
            value={formData.reward_policy}
            onChange={(e) => setFormData({ ...formData, reward_policy: e.target.value })}
            className="mt-2 block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#f59e0b] focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/20"
            placeholder="Describe how rewards will be distributed (e.g., by severity, first-to-find, leaderboard position)..."
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
            Create Event
          </Button>
        </div>
      </form>
    </Modal>
  );
}
