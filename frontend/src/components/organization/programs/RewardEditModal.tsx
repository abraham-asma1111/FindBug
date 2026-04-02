'use client';

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useApiMutation } from '@/hooks/useApiMutation';

interface RewardTier {
  severity: string;
  min_amount: number;
  max_amount: number;
}

interface RewardEditModalProps {
  programId: string;
  existingRewards: any[];
  onClose: () => void;
  onSuccess: () => void;
}

export default function RewardEditModal({ 
  programId, 
  existingRewards, 
  onClose, 
  onSuccess 
}: RewardEditModalProps) {
  const [rewards, setRewards] = useState<Record<string, { min: string; max: string }>>({
    critical: { min: '', max: '' },
    high: { min: '', max: '' },
    medium: { min: '', max: '' },
    low: { min: '', max: '' },
  });

  // Load existing rewards
  useEffect(() => {
    if (existingRewards && existingRewards.length > 0) {
      const rewardMap: Record<string, { min: string; max: string }> = {
        critical: { min: '', max: '' },
        high: { min: '', max: '' },
        medium: { min: '', max: '' },
        low: { min: '', max: '' },
      };

      existingRewards.forEach((reward: any) => {
        rewardMap[reward.severity] = {
          min: reward.min_amount.toString(),
          max: reward.max_amount.toString(),
        };
      });

      setRewards(rewardMap);
    }
  }, [existingRewards]);

  const { mutate: saveRewards, isLoading, error } = useApiMutation(
    `/programs/${programId}/rewards`,
    'POST',
    {
      onSuccess: () => {
        onSuccess();
      },
    }
  );

  const handleSubmit = () => {
    // Build tiers array from rewards
    const tiers: RewardTier[] = [];

    Object.entries(rewards).forEach(([severity, amounts]) => {
      const minAmount = parseFloat(amounts.min);
      const maxAmount = parseFloat(amounts.max);

      if (minAmount > 0 && maxAmount > 0 && maxAmount >= minAmount) {
        tiers.push({
          severity,
          min_amount: minAmount,
          max_amount: maxAmount,
        });
      }
    });

    if (tiers.length === 0) {
      alert('Please add at least one reward tier');
      return;
    }

    saveRewards({ tiers });
  };

  const updateReward = (severity: string, field: 'min' | 'max', value: string) => {
    setRewards(prev => ({
      ...prev,
      [severity]: {
        ...prev[severity],
        [field]: value,
      },
    }));
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Edit Reward Tiers"
      size="lg"
    >
      <div className="space-y-6">
        <p className="text-sm text-[#6d6760]">
          Set bounty amounts for different severity levels. Leave empty to skip a severity level.
        </p>

        {/* Error Message */}
        {error && (
          <div className="rounded-xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
            <p className="text-sm text-[#b42318]">{error.message || 'An error occurred'}</p>
          </div>
        )}

        {/* Reward Tiers */}
        <div className="space-y-4">
          {(['critical', 'high', 'medium', 'low'] as const).map((severity) => (
            <div key={severity} className="space-y-2">
              <label className="text-sm font-semibold text-[#2d2a26] capitalize">
                {severity}
              </label>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <Input
                    type="number"
                    placeholder="Min amount"
                    value={rewards[severity].min}
                    onChange={(e) => updateReward(severity, 'min', e.target.value)}
                    min="0"
                    step="100"
                  />
                </div>
                <span className="text-sm text-[#6d6760]">to</span>
                <div className="flex-1">
                  <Input
                    type="number"
                    placeholder="Max amount"
                    value={rewards[severity].max}
                    onChange={(e) => updateReward(severity, 'max', e.target.value)}
                    min="0"
                    step="100"
                  />
                </div>
                <span className="text-sm text-[#6d6760] w-12">ETB</span>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded-xl bg-[#faf1e1] border border-[#f0d9a8] p-4">
          <p className="text-sm text-[#9a6412]">
            <strong>Note:</strong> Max amount must be greater than or equal to min amount. 
            This will replace all existing reward tiers.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Rewards'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
