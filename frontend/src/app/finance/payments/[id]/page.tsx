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

export default function PaymentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const paymentId = params.id as string;
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({ isOpen: false, type: 'approve' });

  const { data: payment, isLoading } = useApiQuery<any>({
    endpoint: `/payments/bounty/${paymentId}`,
  });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/payments/bounty/${paymentId}`] });
      setConfirmDialog({ isOpen: false, type: 'approve' });
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/payments/bounty/${paymentId}`] });
      setConfirmDialog({ isOpen: false, type: 'reject' });
    },
  });

  const handleConfirmAction = async (notes?: string) => {
    if (confirmDialog.type === 'approve') {
      await approveMutation.mutateAsync({
        endpoint: `/payments/bounty/${paymentId}/process`,
        data: { payment_method: 'bank_transfer', payment_gateway: 'manual', notes },
      });
    } else {
      await rejectMutation.mutateAsync({
        endpoint: `/payments/bounty/${paymentId}/reject`,
        data: { reason: notes },
      });
    }
  };

  if (isLoading) {
    return (
      <FinanceLayout title="Payment Details" subtitle="Loading...">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Loading payment details...</p>
        </div>
      </FinanceLayout>
    );
  }

  if (!payment) {
    return (
      <FinanceLayout title="Payment Not Found" subtitle="The payment could not be found">
        <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
          <p className="text-[#94A3B8]">Payment not found</p>
          <Button variant="outline" size="sm" onClick={() => router.push('/finance/payments')} className="mt-4">
            Back to Payments
          </Button>
        </div>
      </FinanceLayout>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      pending: { bg: 'bg-[#F59E0B]', label: 'PENDING' },
      approved: { bg: 'bg-[#3B82F6]', label: 'APPROVED' },
      completed: { bg: 'bg-[#10B981]', label: 'COMPLETED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      processing: { bg: 'bg-[#F59E0B]', label: 'PROCESSING' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const researcherAmount = payment.researcher_amount || 0;
  const commission = payment.commission_amount || 0;
  const total = payment.total_amount || 0;

  const timelineEvents = [
    {
      type: 'created' as const,
      title: 'Payment Created',
      description: 'Payment request initiated',
      timestamp: payment.created_at,
      user: 'System',
    },
    ...(payment.approved_at
      ? [
          {
            type: 'approved' as const,
            title: 'Payment Approved',
            description: payment.approval_notes || 'Payment approved for processing',
            timestamp: payment.approved_at,
            user: payment.approved_by_name || 'Finance Officer',
          },
        ]
      : []),
    ...(payment.rejected_at
      ? [
          {
            type: 'rejected' as const,
            title: 'Payment Rejected',
            description: payment.rejection_reason || 'Payment rejected',
            timestamp: payment.rejected_at,
            user: payment.rejected_by_name || 'Finance Officer',
          },
        ]
      : []),
    ...(payment.completed_at
      ? [
          {
            type: 'completed' as const,
            title: 'Payment Completed',
            description: 'Funds transferred to researcher',
            timestamp: payment.completed_at,
            user: 'System',
          },
        ]
      : []),
  ];

  return (
    <FinanceLayout
      title={`Payment #${paymentId.slice(0, 8)}`}
      subtitle={`Status: ${payment.status}`}
      headerActions={
        payment.status === 'pending' ? (
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
              Approve Payment
            </Button>
          </div>
        ) : null
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Payment Info */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payment Information</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Report</span>
                <span className="text-[#F8FAFC] font-medium">
                  {payment.report_title || `Report #${payment.report_number || payment.report_id?.slice(0, 8)}`}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Researcher</span>
                <span className="text-[#F8FAFC] font-medium">{payment.researcher_name || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Organization</span>
                <span className="text-[#F8FAFC] font-medium">{payment.organization_name || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Severity</span>
                <span className="text-[#F8FAFC] font-medium">{payment.severity || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#94A3B8]">Status</span>
                {getStatusBadge(payment.status)}
              </div>
              <div className="border-t border-[#334155] pt-4 mt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-[#94A3B8]">Researcher Amount</span>
                  <span className="text-[#F8FAFC] font-medium">${researcherAmount.toLocaleString()} ETB</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-[#94A3B8]">Platform Commission (30%)</span>
                  <span className="text-[#F8FAFC] font-medium">${commission.toLocaleString()} ETB</span>
                </div>
                <div className="flex justify-between text-lg font-bold">
                  <span className="text-[#F8FAFC]">Total Payment</span>
                  <span className="text-[#10B981]">${total.toLocaleString()} ETB</span>
                </div>
              </div>
            </div>
          </div>

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
                <p className="text-xs text-[#64748B]">Created</p>
                <p className="text-sm text-[#F8FAFC]">{new Date(payment.created_at).toLocaleString()}</p>
              </div>
              {payment.approved_at && (
                <div>
                  <p className="text-xs text-[#64748B]">Approved</p>
                  <p className="text-sm text-[#F8FAFC]">{new Date(payment.approved_at).toLocaleString()}</p>
                </div>
              )}
              {payment.completed_at && (
                <div>
                  <p className="text-xs text-[#64748B]">Completed</p>
                  <p className="text-sm text-[#F8FAFC]">{new Date(payment.completed_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>

          {/* Notes */}
          {(payment.approval_notes || payment.rejection_reason) && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <h3 className="text-sm font-semibold text-[#94A3B8] uppercase mb-4">Notes</h3>
              <p className="text-sm text-[#F8FAFC]">
                {payment.approval_notes || payment.rejection_reason}
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
        title={confirmDialog.type === 'approve' ? 'Approve Payment?' : 'Reject Payment?'}
        message={
          confirmDialog.type === 'approve'
            ? `You are about to approve this payment of $${total.toLocaleString()}. This action will process the payment and transfer funds to the researcher.`
            : 'You are about to reject this payment. Please provide a reason for rejection.'
        }
        confirmText={confirmDialog.type === 'approve' ? 'Approve Payment' : 'Reject Payment'}
        type={confirmDialog.type}
        requireNotes={confirmDialog.type === 'reject'}
        notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
        notesPlaceholder={
          confirmDialog.type === 'reject'
            ? 'Explain why this payment is being rejected...'
            : 'Add optional notes...'
        }
        isLoading={approveMutation.isLoading || rejectMutation.isLoading}
      />
    </FinanceLayout>
  );
}
