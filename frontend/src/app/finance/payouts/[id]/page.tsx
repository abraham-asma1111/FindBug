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

export default function PayoutDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const payoutId = params.id as string;
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({ isOpen: false, type: 'approve' });

  const { data: payout, isLoading } = useApiQuery<any>({
    endpoint: `/wallet/payouts/${payoutId}`,
  });

  const processMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/wallet/payouts/${payoutId}`] });
      setConfirmDialog({ isOpen: false, type: 'approve' });
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/wallet/payouts/${payoutId}`] });
      setConfirmDialog({ isOpen: false, type: 'reject' });
    },
  });

  const handleConfirmAction = async (notes?: string) => {
    if (confirmDialog.type === 'approve') {
      await processMutation.mutateAsync({
        endpoint: `/wallet/payouts/${payoutId}/approve`,
        data: { notes },
      });
    } else {
      await rejectMutation.mutateAsync({
        endpoint: `/wallet/payouts/${payoutId}/reject?reason=${encodeURIComponent(notes || '')}`,
        data: {},
      });
    }
  };

  if (isLoading) {
    return (
      <FinanceLayout title="Payout Details" subtitle="Loading...">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Loading payout details...</p>
        </div>
      </FinanceLayout>
    );
  }

  if (!payout) {
    return (
      <FinanceLayout title="Payout Not Found" subtitle="The payout could not be found">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Payout not found</p>
          <Button variant="outline" size="sm" onClick={() => router.push('/finance/payouts')} className="mt-4">
            Back to Payouts
          </Button>
        </div>
      </FinanceLayout>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      requested: { bg: 'bg-[#3B82F6]', label: 'REQUESTED' },
      processing: { bg: 'bg-[#F59E0B]', label: 'PROCESSING' },
      completed: { bg: 'bg-[#10B981]', label: 'COMPLETED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
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
      title: 'Payout Requested',
      description: 'Researcher requested payout',
      timestamp: payout.requested_at,
      user: payout.researcher_name || 'Researcher',
    },
    ...(payout.processed_at
      ? [
          {
            type: 'approved' as const,
            title: 'Payout Processing',
            description: payout.processing_notes || 'Payout is being processed',
            timestamp: payout.processed_at,
            user: payout.processed_by_name || 'Finance Officer',
          },
        ]
      : []),
    ...(payout.rejected_at
      ? [
          {
            type: 'rejected' as const,
            title: 'Payout Rejected',
            description: payout.rejection_reason || 'Payout rejected',
            timestamp: payout.rejected_at,
            user: payout.rejected_by_name || 'Finance Officer',
          },
        ]
      : []),
    ...(payout.completed_at
      ? [
          {
            type: 'completed' as const,
            title: 'Payout Completed',
            description: 'Funds transferred successfully',
            timestamp: payout.completed_at,
            user: 'System',
          },
        ]
      : []),
  ];

  return (
    <FinanceLayout
      title={`Payout #${payoutId.slice(0, 8)}`}
      subtitle={`Status: ${payout.status}`}
      headerActions={
        payout.status === 'requested' ? (
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
              Process Payout
            </Button>
          </div>
        ) : null
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Payout Info */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payout Information</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Researcher</span>
                <span className="text-[#F8FAFC] font-medium">{payout.researcher_name || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Amount</span>
                <span className="text-[#10B981] font-bold text-xl">${(payout.amount || 0).toLocaleString()} ETB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Payment Method</span>
                <span className="text-[#F8FAFC] font-medium">{payout.payment_method || 'Bank Transfer'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Status</span>
                {getStatusBadge(payout.status)}
              </div>
            </div>
            
            {/* Cross-Portal Link to Researcher */}
            {payout.researcher_id && (
              <div className="mt-4 pt-4 border-t border-[#334155]">
                <a
                  href={`/researcher/earnings?researcher_id=${payout.researcher_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[#3B82F6] hover:underline flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  View Researcher Profile →
                </a>
              </div>
            )}
          </div>

          {/* Payment Details */}
          {payout.payment_details && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payment Details</h2>
              <div className="space-y-3">
                {payout.payment_details.account_number && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Account Number</span>
                    <span className="text-[#F8FAFC] font-mono">
                      ****{payout.payment_details.account_number.slice(-4)}
                    </span>
                  </div>
                )}
                {payout.payment_details.bank_name && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Bank Name</span>
                    <span className="text-[#F8FAFC]">{payout.payment_details.bank_name}</span>
                  </div>
                )}
                {payout.payment_details.account_holder && (
                  <div className="flex justify-between">
                    <span className="text-[#94A3B8]">Account Holder</span>
                    <span className="text-[#F8FAFC]">{payout.payment_details.account_holder}</span>
                  </div>
                )}
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
                <p className="text-xs text-[#64748B]">Requested</p>
                <p className="text-sm text-[#F8FAFC]">{new Date(payout.requested_at).toLocaleString()}</p>
              </div>
              {payout.processed_at && (
                <div>
                  <p className="text-xs text-[#64748B]">Processed</p>
                  <p className="text-sm text-[#F8FAFC]">{new Date(payout.processed_at).toLocaleString()}</p>
                </div>
              )}
              {payout.completed_at && (
                <div>
                  <p className="text-xs text-[#64748B]">Completed</p>
                  <p className="text-sm text-[#F8FAFC]">{new Date(payout.completed_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>

          {/* Notes */}
          {(payout.processing_notes || payout.rejection_reason) && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h3 className="text-sm font-semibold text-[#94A3B8] uppercase mb-4">Notes</h3>
              <p className="text-sm text-[#F8FAFC]">
                {payout.processing_notes || payout.rejection_reason}
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
        title={confirmDialog.type === 'approve' ? 'Process Payout?' : 'Reject Payout?'}
        message={
          confirmDialog.type === 'approve'
            ? `You are about to process this payout of $${(payout.amount || 0).toLocaleString()}. This action will transfer funds to the researcher's payment method.`
            : 'You are about to reject this payout. Please provide a reason for rejection.'
        }
        confirmText={confirmDialog.type === 'approve' ? 'Process Payout' : 'Reject Payout'}
        type={confirmDialog.type}
        requireNotes={confirmDialog.type === 'reject'}
        notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
        notesPlaceholder={
          confirmDialog.type === 'reject'
            ? 'Explain why this payout is being rejected...'
            : 'Add optional notes...'
        }
        isLoading={processMutation.isLoading || rejectMutation.isLoading}
      />
    </FinanceLayout>
  );
}
