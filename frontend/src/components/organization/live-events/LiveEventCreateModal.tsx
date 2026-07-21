"use client";

import { useState } from "react";
import { useApiMutation } from "@/hooks/useApiMutation";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Textarea from "@/components/ui/Textarea";
import { useToast } from "@/components/ui/Toast";

interface LiveEventCreateModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

interface EventFormData {
  name: string;
  description: string;
  start_time: string;
  end_time: string;
  max_participants: string;
  prize_pool: string;
  scope_description: string;
  target_assets: string;
  reward_policy: string;
}

export function LiveEventCreateModal({ onClose, onSuccess }: LiveEventCreateModalProps) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState<EventFormData>({
    name: "",
    description: "",
    start_time: "",
    end_time: "",
    max_participants: "",
    prize_pool: "",
    scope_description: "",
    target_assets: "",
    reward_policy: "",
  });

  const createMutation = useApiMutation("/live-events", "POST", {
    onSuccess: () => {
      showToast("Event created successfully", "success");
      onSuccess();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to create event", "error");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name || !formData.description || !formData.start_time || !formData.end_time) {
      showToast("Please fill in all required fields", "error");
      return;
    }

    // Prepare data
    const data = {
      name: formData.name,
      description: formData.description,
      start_time: new Date(formData.start_time).toISOString(),
      end_time: new Date(formData.end_time).toISOString(),
      max_participants: formData.max_participants ? parseInt(formData.max_participants) : null,
      prize_pool: formData.prize_pool ? parseFloat(formData.prize_pool) : null,
      scope_description: formData.scope_description || null,
      target_assets: formData.target_assets || null,
      reward_policy: formData.reward_policy || null,
    };

    createMutation.mutate(data);
  };

  const handleChange = (field: keyof EventFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Create Live Hacking Event"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Event Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Event Name *
          </label>
          <Input
            value={formData.name}
            onChange={(e) => handleChange("name", e.target.value)}
            placeholder="e.g., Summer Security Sprint 2026"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description *
          </label>
          <Textarea
            value={formData.description}
            onChange={(e) => handleChange("description", e.target.value)}
            placeholder="Describe the event objectives and rules..."
            rows={3}
            required
          />
        </div>

        {/* Time Window */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Start Time *
            </label>
            <Input
              type="datetime-local"
              value={formData.start_time}
              onChange={(e) => handleChange("start_time", e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              End Time *
            </label>
            <Input
              type="datetime-local"
              value={formData.end_time}
              onChange={(e) => handleChange("end_time", e.target.value)}
              required
            />
          </div>
        </div>

        {/* Configuration */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Participants
            </label>
            <Input
              type="number"
              value={formData.max_participants}
              onChange={(e) => handleChange("max_participants", e.target.value)}
              placeholder="e.g., 50"
              min="1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Prize Pool (ETB)
            </label>
            <Input
              type="number"
              value={formData.prize_pool}
              onChange={(e) => handleChange("prize_pool", e.target.value)}
              placeholder="e.g., 100000"
              min="0"
              step="0.01"
            />
          </div>
        </div>

        {/* Scope Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Scope Description
          </label>
          <Textarea
            value={formData.scope_description}
            onChange={(e) => handleChange("scope_description", e.target.value)}
            placeholder="Define what's in scope for this event..."
            rows={3}
          />
        </div>

        {/* Target Assets */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Target Assets
          </label>
          <Textarea
            value={formData.target_assets}
            onChange={(e) => handleChange("target_assets", e.target.value)}
            placeholder="List target URLs, IPs, or systems (one per line)"
            rows={3}
          />
        </div>

        {/* Reward Policy */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Reward Policy
          </label>
          <Textarea
            value={formData.reward_policy}
            onChange={(e) => handleChange("reward_policy", e.target.value)}
            placeholder="Describe how prizes will be distributed..."
            rows={3}
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Default: 1st: 40%, 2nd: 25%, 3rd: 15%, 4th-10th: 20% split
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={createMutation.isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={createMutation.isLoading}
          >
            {createMutation.isLoading ? "Creating..." : "Create Event"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
