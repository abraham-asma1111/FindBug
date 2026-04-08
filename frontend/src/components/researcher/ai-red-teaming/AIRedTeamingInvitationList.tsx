'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import { useApiQuery } from '@/hooks/useApiQuery';
import api from '@/lib/api';

interface AIRedTeamingInvitation {
  id: string;
  engagement: {
    id: string;
    name: string;
    target_ai_system: string;
    model_type: string;
    testing_environment: string;
    ethical_guidelines: string;
    start_date?: string;
    end_date?: string;
  };
  status: 'pending' | 'accepted' | 'declined';
  invited_at: string;
}

export default function AIRedTeamingInvitationList() {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const { data: invitations, isLoading, refetch } = useApiQuery<AIRedTeamingInvitation[]>(
    '/ai-red-teaming/my-invitations'
  );

  const handleRespond = async (invitationId: string, accept: boolean) => {
    try {
      setProcessingId(invitationId);
      setError('');
      setSuccess('');

      await api.post(`/ai-red-teaming/invitations/${invitationId}/respond`, {
        accept,
      });

      setSuccess(accept ? 'Invitation accepted! You can now access the engagement.' : 'Invitation declined.');
      refetch();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to respond to invitation');
    } finally {
      setProcessingId(null);
    }
  };

  const modelTypeLabels: Record<string, string> = {
    llm: 'Large Language Model',
    ml_model: 'ML Model',
    ai_agent: 'AI Agent',
    chatbot: 'Chatbot',
    recommendation_system: 'Recommendation System',
    computer_vision: 'Computer Vision',
  };

  const statusColors: Record<string, string> = {
    pending: 'bg-[#faf1e1] text-[#9a6412]',
    accepted: 'bg-[#eef7ef] text-[#24613a]',
    declined: 'bg-[#fff2f1] text-[#9d1f1f]',
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
        </div>
      </Card>
    );
  }

  const pendingInvitations = invitations?.filter((inv) => inv.status === 'pending') || [];
  const respondedInvitations = invitations?.filter((inv) => inv.status !== 'pending') || [];

  return (
    <div className="space-y-6">
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      {/* Pending Invitations */}
      {pendingInvitations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
            Pending Invitations ({pendingInvitations.length})
          </h3>
          <div className="space-y-4">
            {pendingInvitations.map((invitation) => (
              <div
                key={invitation.id}
                className="p-4 rounded-lg border-2 border-[#7d39c2] bg-[#f6efff] dark:bg-purple-900/20"
              >
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="flex-1">
                    <h4 className="font-bold text-[#2d2a26] dark:text-slate-100 mb-1">
                      {invitation.engagement.name}
                    </h4>
                    <p className="text-sm text-[#6d6760] dark:text-slate-400">
                      {invitation.engagement.target_ai_system}
                    </p>
                  </div>
                  <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold bg-[#faf1e1] text-[#9a6412]">
                    Invitation Pending
                  </span>
                </div>

                <div className="grid gap-3 mb-4">
                  <div>
                    <span className="text-xs font-medium text-[#8b8177] dark:text-slate-500">Model Type:</span>
                    <span className="ml-2 text-sm text-[#2d2a26] dark:text-slate-100">
                      {modelTypeLabels[invitation.engagement.model_type] || invitation.engagement.model_type}
                    </span>
                  </div>
                  {invitation.engagement.start_date && (
                    <div>
                      <span className="text-xs font-medium text-[#8b8177] dark:text-slate-500">Timeline:</span>
                      <span className="ml-2 text-sm text-[#2d2a26] dark:text-slate-100">
                        {new Date(invitation.engagement.start_date).toLocaleDateString()} -{' '}
                        {invitation.engagement.end_date
                          ? new Date(invitation.engagement.end_date).toLocaleDateString()
                          : 'TBD'}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => handleRespond(invitation.id, true)}
                    disabled={processingId === invitation.id}
                    isLoading={processingId === invitation.id}
                  >
                    Accept Invitation
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => handleRespond(invitation.id, false)}
                    disabled={processingId === invitation.id}
                  >
                    Decline
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Responded Invitations */}
      {respondedInvitations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
            Previous Responses
          </h3>
          <div className="space-y-3">
            {respondedInvitations.map((invitation) => (
              <div
                key={invitation.id}
                className="p-4 rounded-lg border border-[#e6ddd4] dark:border-gray-700"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-medium text-[#2d2a26] dark:text-slate-100 mb-1">
                      {invitation.engagement.name}
                    </h4>
                    <p className="text-sm text-[#6d6760] dark:text-slate-400">
                      {invitation.engagement.target_ai_system}
                    </p>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                      statusColors[invitation.status]
                    }`}
                  >
                    {invitation.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {!invitations || invitations.length === 0 ? (
        <Card className="p-6">
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-2">
              No AI Red Teaming Invitations
            </h3>
            <p className="text-sm text-[#6d6760] dark:text-slate-400">
              AI Red Teaming is invitation-only. Organizations will invite you based on your AI/ML security expertise.
            </p>
          </div>
        </Card>
      ) : null}
    </div>
  );
}
