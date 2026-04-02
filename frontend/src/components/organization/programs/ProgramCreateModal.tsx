'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import api from '@/lib/api';

interface ProgramCreateModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function ProgramCreateModal({ onClose, onSuccess }: ProgramCreateModalProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'bounty',
    scope: '',
    reward_tiers: [] as any[],
    rules: '',
  });

  const { mutate: createProgram, isLoading, error } = useApiMutation(
    '/programs',
    'POST',
    {
      onSuccess: async (program: any) => {
        // After program is created, add scopes
        if (formData.scope.trim()) {
          try {
            // Parse scope text into individual lines
            const scopeLines = formData.scope
              .split('\n')
              .map(line => line.trim())
              .filter(line => line.length > 0 && !line.startsWith('#'));

            // Create a scope for each line
            for (const line of scopeLines) {
              // Remove leading dashes/bullets
              const cleanLine = line.replace(/^[-•*]\s*/, '').trim();
              
              if (cleanLine) {
                await api.post(`/programs/${program.id}/scopes`, {
                  asset_type: 'web_app', // Default type
                  asset_identifier: cleanLine,
                  is_in_scope: true,
                  description: cleanLine,
                  max_severity: 'critical'
                });
              }
            }
          } catch (err) {
            console.error('Error creating scopes:', err);
          }
        }

        // After scopes, add reward tiers if any
        if (formData.reward_tiers.length > 0) {
          try {
            await api.post(`/programs/${program.id}/rewards`, {
              tiers: formData.reward_tiers
            });
          } catch (err) {
            console.error('Error creating reward tiers:', err);
          }
        }

        onSuccess();
      },
    }
  );

  const handleSubmit = () => {
    // Remove scope, reward_tiers, and rules from the payload as they're handled separately
    const { scope, reward_tiers, rules, ...programData } = formData;
    
    // Add rules_of_engagement if rules were provided
    const payload = rules.trim() 
      ? { ...programData, rules_of_engagement: rules }
      : programData;
    
    createProgram(payload);
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return formData.name.trim().length > 0 && formData.description.trim().length > 0;
      case 2:
        return formData.scope.trim().length > 0;
      case 3:
        return true; // Reward tiers are optional
      case 4:
        return true; // Rules are optional
      default:
        return false;
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-[#2d2a26]">Basic Information</h3>
            
            <Input
              label="Program Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Acme Corp Bug Bounty Program"
              required
            />

            <Textarea
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe your program, what you're looking for, and any important details..."
              rows={4}
              required
            />

            <Select
              label="Program Type"
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              options={[
                { value: 'bounty', label: 'Bug Bounty (Paid)' },
                { value: 'vdp', label: 'VDP (Vulnerability Disclosure Program)' },
              ]}
            />
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-[#2d2a26]">Scope Definition</h3>
            <p className="text-sm text-[#6d6760]">
              Define what's in scope for your program. Include domains, applications, and any specific assets.
            </p>

            <Textarea
              label="In-Scope Assets"
              value={formData.scope}
              onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
              placeholder="Example:&#10;- *.example.com&#10;- https://app.example.com&#10;- https://api.example.com&#10;- Mobile apps (iOS/Android)"
              rows={8}
              required
            />

            <div className="rounded-xl bg-[#edf5fb] border border-[#b8d9f2] p-4">
              <p className="text-sm text-[#2d78a8]">
                <strong>Tip:</strong> Be specific about what's in scope. You can add out-of-scope items and detailed scope rules in the next steps.
              </p>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-[#2d2a26]">Reward Structure (Optional)</h3>
            <p className="text-sm text-[#6d6760]">
              Set bounty amounts for different severity levels. You can skip this for VDP programs or configure later.
            </p>

            <div className="space-y-3">
              {['critical', 'high', 'medium', 'low'].map((severity) => (
                <div key={severity} className="flex items-center gap-4">
                  <div className="w-24">
                    <span className="text-sm font-semibold text-[#2d2a26] capitalize">
                      {severity}
                    </span>
                  </div>
                  <Input
                    type="number"
                    placeholder="0"
                    className="flex-1"
                    onChange={(e) => {
                      const value = parseFloat(e.target.value) || 0;
                      const tiers = formData.reward_tiers.filter(t => t.severity !== severity);
                      if (value > 0) {
                        tiers.push({ severity, min_amount: value, max_amount: value });
                      }
                      setFormData({ ...formData, reward_tiers: tiers });
                    }}
                  />
                  <span className="text-sm text-[#6d6760]">ETB</span>
                </div>
              ))}
            </div>

            <div className="rounded-xl bg-[#faf1e1] border border-[#f0d9a8] p-4">
              <p className="text-sm text-[#9a6412]">
                <strong>Note:</strong> You can set ranges and adjust rewards after creating the program.
              </p>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-[#2d2a26]">Rules & Guidelines (Optional)</h3>
            <p className="text-sm text-[#6d6760]">
              Define program rules, disclosure policies, and any special requirements for researchers.
            </p>

            <Textarea
              label="Program Rules"
              value={formData.rules}
              onChange={(e) => setFormData({ ...formData, rules: e.target.value })}
              placeholder="Example:&#10;- No social engineering&#10;- No denial of service attacks&#10;- Report must include proof of concept&#10;- 90-day disclosure policy&#10;- One vulnerability per report"
              rows={10}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Create Bug Bounty Program"
      size="xl"
    >
      <div className="space-y-6">
        {/* Progress Steps */}
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold ${
                  s === step
                    ? 'bg-[#2d2a26] text-white'
                    : s < step
                    ? 'bg-[#0d7a3d] text-white'
                    : 'bg-[#e6ddd4] text-[#8b8177]'
                }`}
              >
                {s < step ? '✓' : s}
              </div>
              {s < 4 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    s < step ? 'bg-[#0d7a3d]' : 'bg-[#e6ddd4]'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Labels */}
        <div className="flex items-center justify-between text-xs text-[#6d6760]">
          <span className={step === 1 ? 'font-semibold text-[#2d2a26]' : ''}>Basic Info</span>
          <span className={step === 2 ? 'font-semibold text-[#2d2a26]' : ''}>Scope</span>
          <span className={step === 3 ? 'font-semibold text-[#2d2a26]' : ''}>Rewards</span>
          <span className={step === 4 ? 'font-semibold text-[#2d2a26]' : ''}>Rules</span>
        </div>

        {/* Error Message */}
        {error && (
          <div className="rounded-xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
            <p className="text-sm text-[#b42318]">{error.message || 'An error occurred'}</p>
          </div>
        )}

        {/* Step Content */}
        <div className="min-h-[400px]">
          {renderStep()}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-[#e6ddd4]">
          <div>
            {step > 1 && (
              <Button
                variant="secondary"
                onClick={() => setStep(step - 1)}
                disabled={isLoading}
              >
                Back
              </Button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>

            {step < 4 ? (
              <Button
                onClick={() => setStep(step + 1)}
                disabled={!isStepValid() || isLoading}
              >
                Next
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!isStepValid() || isLoading}
              >
                {isLoading ? 'Creating...' : 'Create Program'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}
