'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import FinanceLayout from '@/components/finance/FinanceLayout';
import Timeline from '@/components/finance/Timeline';
import ConfirmationDialog from '@/components/finance/ConfirmationDialog';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

export default function KYCDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const verificationId = params.id as string;
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({ isOpen: false, type: 'approve' });

  const { data: verification, isLoading } = useApiQuery<any>({
    endpoint: `/kyc/verifications/${verificationId}`,
  });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/kyc/verifications/${verificationId}`] });
      setConfirmDialog({ isOpen: false, type: 'approve' });
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/kyc/verifications/${verificationId}`] });
      setConfirmDialog({ isOpen: false, type: 'reject' });
    },
  });

  const handleConfirmAction = async (notes?: string) => {
    if (confirmDialog.type === 'approve') {
      await approveMutation.mutateAsync({
        endpoint: `/kyc/verifications/${verificationId}/approve`,
        data: {},
      });
    } else {
      await rejectMutation.mutateAsync({
        endpoint: `/kyc/verifications/${verificationId}/reject?reason=${encodeURIComponent(notes || '')}`,
        data: {},
      });
    }
  };

  if (isLoading) {
    return (
      <FinanceLayout title="KYC Verification Details" subtitle="Loading...">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Loading verification details...</p>
        </div>
      </FinanceLayout>
    );
  }

  if (!verification) {
    return (
      <FinanceLayout title="Verification Not Found" subtitle="The verification could not be found">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Verification not found</p>
          <Button variant="outline" size="sm" onClick={() => router.push('/finance/kyc')} className="mt-4">
            Back to KYC
          </Button>
        </div>
      </FinanceLayout>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      pending: { bg: 'bg-[#F59E0B]', label: 'PENDING' },
      approved: { bg: 'bg-[#10B981]', label: 'APPROVED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      under_review: { bg: 'bg-[#3B82F6]', label: 'UNDER REVIEW' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const timelineEvents = [
    {
      type: 'created' as const,
      title: 'Verification Submitted',
      description: 'KYC documents submitted for review',
      timestamp: verification.submitted_at,
      user: verification.researcher_name || 'Researcher',
    },
    ...(verification.reviewed_at
      ? [
          {
            type: verification.status === 'approved' ? ('approved' as const) : ('rejected' as const),
            title: verification.status === 'approved' ? 'Verification Approved' : 'Verification Rejected',
            description: verification.review_notes || verification.rejection_reason || 'Verification reviewed',
            timestamp: verification.reviewed_at,
            user: verification.reviewed_by_name || 'Finance Officer',
          },
        ]
      : []),
  ];

  return (
    <FinanceLayout
      title={`KYC Verification #${verificationId.slice(0, 8)}`}
      subtitle={`Status: ${verification.status}`}
      headerActions={
        verification.status === 'pending' ? (
          <div className="flex gap-2">
            <Button
              variant="danger"
              size="sm"
              onClick={() => setConfirmDialog({ isOpen: true, type: 'reject' })}
            >
              Reject
            </Button>
            <Button
              variant="success"
              size="sm"
              onClick={() => setConfirmDialog({ isOpen: true, type: 'approve' })}
            >
              Approve Verification
            </Button>
          </div>
        ) : null
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Verification Info */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Verification Information</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">User</span>
                <span className="text-[#F8FAFC] font-medium">{verification.user_name || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Email</span>
                <span className="text-[#F8FAFC] font-medium">{verification.user_email || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Document Type</span>
                <span className="text-[#F8FAFC] font-medium capitalize">{(verification.document_type || 'ID Document').replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Document Number</span>
                <span className="text-[#F8FAFC] font-mono">****{(verification.document_number || '').slice(-4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Status</span>
                {getStatusBadge(verification.status)}
              </div>
            </div>
          </div>

          {/* Document Details */}
          {verification.document_data && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Document Details</h2>
              <div className="space-y-3">
                {verification.document_data.full_name && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Full Name</span>
                    <span className="text-[#F8FAFC]">{verification.document_data.full_name}</span>
                  </div>
                )}
                {verification.document_data.document_number && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Document Number</span>
                    <span className="text-[#F8FAFC] font-mono">
                      ****{verification.document_data.document_number.slice(-4)}
                    </span>
                  </div>
                )}
                {verification.document_data.date_of_birth && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Date of Birth</span>
                    <span className="text-[#F8FAFC]">
                      {new Date(verification.document_data.date_of_birth).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {verification.document_data.nationality && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Nationality</span>
                    <span className="text-[#F8FAFC]">{verification.document_data.nationality}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Document Images */}
          {verification.document_urls && verification.document_urls.length > 0 && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Document Images</h2>
              <div className="grid grid-cols-2 gap-4">
                {verification.document_urls.map((url: string, index: number) => (
                  <div key={index} className="border border-[#334155] rounded-lg overflow-hidden">
                    <img
                      src={url}
                      alt={`Document ${index + 1}`}
                      className="w-full h-auto"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Activity Timeline</h2>
            <Timeline events={timelineEvents} />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
            <h3 className="text-sm font-semibold text-[#94A3B8] uppercase mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-[#64748B]">Submitted</p>
                <p className="text-sm text-[#F8FAFC]">{new Date(verification.submitted_at).toLocaleString()}</p>
              </div>
              {verification.reviewed_at && (
                <div>
                  <p className="text-xs text-[#64748B]">Reviewed</p>
                  <p className="text-sm text-[#F8FAFC]">{new Date(verification.reviewed_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>

          {/* Persona Data */}
          {verification.persona_inquiry_id && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h3 className="text-sm font-semibold text-[#94A3B8] uppercase mb-4">Persona Integration</h3>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-[#64748B]">Inquiry ID</p>
                  <p className="text-xs text-[#F8FAFC] font-mono break-all">
                    {verification.persona_inquiry_id}
                  </p>
                </div>
                {verification.persona_verification_status && (
                  <div>
                    <p className="text-xs text-[#64748B]">Persona Status</p>
                    <p className="text-xs text-[#F8FAFC]">{verification.persona_verification_status}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {(verification.review_notes || verification.rejection_reason) && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h3 className="text-sm font-semibold text-[#94A3B8] uppercase mb-4">Review Notes</h3>
              <p className="text-sm text-[#F8FAFC]">
                {verification.review_notes || verification.rejection_reason}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={confirmDialog.isOpen}
        onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
        onConfirm={handleConfirmAction}
        title={confirmDialog.type === 'approve' ? 'Approve Verification?' : 'Reject Verification?'}
        message={
          confirmDialog.type === 'approve'
            ? 'You are about to approve this KYC verification. This will allow the researcher to receive payments.'
            : 'You are about to reject this KYC verification. Please provide a reason for rejection.'
        }
        confirmText={confirmDialog.type === 'approve' ? 'Approve Verification' : 'Reject Verification'}
        type={confirmDialog.type}
        requireNotes={confirmDialog.type === 'reject'}
        notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
        notesPlaceholder={
          confirmDialog.type === 'reject'
            ? 'Explain why this verification is being rejected...'
            : 'Add optional notes...'
        }
        isLoading={approveMutation.isLoading || rejectMutation.isLoading}
      />
    </FinanceLayout>
  );
}
