'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import Checkbox from '@/components/ui/Checkbox';
import { api } from '@/lib/api';

interface AIRedTeamingEnvironmentSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  onSuccess: () => void;
}

export default function AIRedTeamingEnvironmentSetupModal({
  isOpen,
  onClose,
  engagementId,
  onSuccess,
}: AIRedTeamingEnvironmentSetupModalProps) {
  const [formData, setFormData] = useState({
    model_type: 'llm',
    sandbox_url: '',
    api_endpoint: '',
    access_token: '',
    is_isolated: true,
    max_requests_per_minute: '60',
    max_concurrent_requests: '10',
    timeout_seconds: '30',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    // Validation
    if (!formData.sandbox_url || !formData.api_endpoint || !formData.access_token) {
      setError('Sandbox URL, API endpoint, and access token are required');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');

      await api.post(`/ai-red-teaming/engagements/${engagementId}/testing-environment`, {
        model_type: formData.model_type,
        sandbox_url: formData.sandbox_url,
        api_endpoint: formData.api_endpoint,
        access_token: formData.access_token,
        is_isolated: formData.is_isolated,
        access_controls: {
          network_restricted: true,
          isolated: formData.is_isolated,
        },
        rate_limits: {
          max_requests_per_minute: parseInt(formData.max_requests_per_minute),
          max_concurrent_requests: parseInt(formData.max_concurrent_requests),
          timeout_seconds: parseInt(formData.timeout_seconds),
        },
      });

      onSuccess();
      onClose();
      
      // Reset form
      setFormData({
        model_type: 'llm',
        sandbox_url: '',
        api_endpoint: '',
        access_token: '',
        is_isolated: true,
        max_requests_per_minute: '60',
        max_concurrent_requests: '10',
        timeout_seconds: '30',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup testing environment');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Setup Testing Environment"
      size="large"
    >
      <div className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}

        <Alert variant="info">
          Configure an isolated sandbox environment for AI security testing. Access tokens are encrypted for secure storage.
        </Alert>

        <Input
          label="Sandbox URL"
          value={formData.sandbox_url}
          onChange={(e) => setFormData({ ...formData, sandbox_url: e.target.value })}
          placeholder="https://sandbox.example.com"
          required
        />

        <Input
          label="API Endpoint"
          value={formData.api_endpoint}
          onChange={(e) => setFormData({ ...formData, api_endpoint: e.target.value })}
          placeholder="https://api.example.com/v1/chat"
          required
        />

        <Textarea
          label="Access Token"
          value={formData.access_token}
          onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
          placeholder="sk-..."
          rows={3}
          required
        />

        <div className="grid grid-cols-3 gap-4">
          <Input
            label="Max Requests/Min"
            type="number"
            value={formData.max_requests_per_minute}
            onChange={(e) => setFormData({ ...formData, max_requests_per_minute: e.target.value })}
          />
          <Input
            label="Max Concurrent"
            type="number"
            value={formData.max_concurrent_requests}
            onChange={(e) => setFormData({ ...formData, max_concurrent_requests: e.target.value })}
          />
          <Input
            label="Timeout (seconds)"
            type="number"
            value={formData.timeout_seconds}
            onChange={(e) => setFormData({ ...formData, timeout_seconds: e.target.value })}
          />
        </div>

        <Checkbox
          label="Isolated Environment"
          checked={formData.is_isolated}
          onChange={(e) => setFormData({ ...formData, is_isolated: e.target.checked })}
          helperText="Recommended: Isolate testing environment from production systems"
        />

        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} isLoading={isSubmitting}>
            Setup Environment
          </Button>
        </div>
      </div>
    </Modal>
  );
}
