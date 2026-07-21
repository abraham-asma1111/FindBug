'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Timeline from '@/components/finance/Timeline';
import ConfirmationDialog from '@/components/finance/ConfirmationDialog';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

export default function PaymentMethodDetailPage() {
  const user = useAuthStore((state) => state.user);
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const methodId = params.id as string;
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({ isOpen: false, type: 'approve' });

  // Force dark mode immediately
  if (typeof window !== 'undefined') {
    document.documentElement.classList.add('dark');
  }

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch payment method details
  const { data: paymentMethod, isLoading } = useApiQuery<any>({
    endpoint: `/payment-methods/details/${methodId}`,
    queryKey: [`/payment-methods/details/${methodId}`],
  });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/payment-methods/details/${methodId}`] });
      setConfirmDialog({ isOpen: false, type: 'approve' });
      router.push('/finance/payment-methods?status=approved');
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/payment-methods/details/${methodId}`] });
      setConfirmDialog({ isOpen: false, type: 'reject' });
      router.push('/finance/payment-methods?status=rejected');
    },
  });

  const handleConfirmAction = async (notes?: string) => {
    if (confirmDialog.type === 'approve') {
      await approveMutation.mutateAsync({
        endpoint: `/payment-methods/${methodId}/approve`,
        data: {},
      });
    } else {
      await rejectMutation.mutateAsync({
        endpoint: `/payment-methods/${methodId}/reject`,
        data: { reason: notes },
      });
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="Payment Method Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading payment method details...</p>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  if (!paymentMethod) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="Payment Method Not Found"
            subtitle="The payment method could not be found"
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8] mb-4">Payment method not found</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/finance/payment-methods')}
              >
                Back to Payment Methods
              </Button>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; label: string }> = {
      pending: { bg: 'bg-[#F59E0B]', label: 'PENDING' },
      approved: { bg: 'bg-[#10B981]', label: 'APPROVED' },
      rejected: { bg: 'bg-[#EF4444]', label: 'REJECTED' },
    };
    const config = statusMap[status] || { bg: 'bg-[#94A3B8]', label: status.toUpperCase() };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const getKYCBadge = (kyc: any) => {
    if (!kyc) {
      return <span className="px-2 py-1 rounded text-xs font-bold bg-[#64748B] text-white">NO KYC</span>;
    }
    const isVerified = kyc.email_verified && kyc.persona_verified;
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold ${
        isVerified ? 'bg-[#10B981]' : 'bg-[#F59E0B]'
      } text-white`}>
        {isVerified ? '✓ VERIFIED' : 'PARTIAL'}
      </span>
    );
  };

  const timelineEvents = [
    {
      id: `${methodId}-created`,
      type: 'created' as const,
      title: 'Payment Method Submitted',
      description: 'Researcher submitted payment method for verification',
      timestamp: paymentMethod.created_at,
      user: paymentMethod.researcher?.username || 'Researcher',
    },
    ...(paymentMethod.status === 'approved' && paymentMethod.updated_at
      ? [
          {
            id: `${methodId}-approved`,
            type: 'approved' as const,
            title: 'Payment Method Approved',
            description: 'Payment method verified and approved for payouts',
            timestamp: paymentMethod.updated_at,
            user: 'Finance Officer',
          },
        ]
      : []),
    ...(paymentMethod.status === 'rejected' && paymentMethod.rejected_at
      ? [
          {
            id: `${methodId}-rejected`,
            type: 'rejected' as const,
            title: 'Payment Method Rejected',
            description: paymentMethod.rejection_reason || 'Payment method rejected',
            timestamp: paymentMethod.rejected_at,
            user: 'Finance Officer',
          },
        ]
      : []),
  ];

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title={`Payment Method Details`}
          subtitle={`${paymentMethod.method_type?.replace('_', ' ').toUpperCase()} - ${paymentMethod.account_name}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Header Actions */}
          {paymentMethod.status === 'pending' && (
            <div className="mb-6 flex gap-2 justify-end">
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
                Approve Payment Method
              </Button>
            </div>
          )}

          {/* Streamlined Single Card Layout */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
            {/* Payment Method Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Payment Method Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Method Type</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {paymentMethod.method_type?.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Status</span>
                  <div className="flex-shrink-0">{getStatusBadge(paymentMethod.status)}</div>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Account Holder</span>
                  <span className="text-[#F8FAFC] font-medium text-right">{paymentMethod.account_name || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Account Number</span>
                  <span className="text-[#F8FAFC] font-medium font-mono text-right">
                    {paymentMethod.method_type === 'bank_transfer'
                      ? `****${paymentMethod.account_number?.slice(-4)}`
                      : paymentMethod.account_number}
                  </span>
                </div>
                {paymentMethod.bank_name && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Bank Name</span>
                    <span className="text-[#F8FAFC] font-medium text-right">{paymentMethod.bank_name}</span>
                  </div>
                )}
                {paymentMethod.phone_number && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Phone Number</span>
                    <span className="text-[#F8FAFC] font-medium text-right">{paymentMethod.phone_number}</span>
                  </div>
                )}
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Default Method</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {paymentMethod.is_default ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Submitted</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {new Date(paymentMethod.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Researcher Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Researcher Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Username</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {paymentMethod.researcher?.username || paymentMethod.researcher?.full_name || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Email</span>
                  <span className="text-[#F8FAFC] font-medium text-right">{paymentMethod.researcher?.email}</span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">KYC Status</span>
                  <div className="flex-shrink-0">{getKYCBadge(paymentMethod.kyc)}</div>
                </div>
                {paymentMethod.kyc && (
                  <>
                    <div className="flex justify-between items-center gap-4">
                      <span className="text-[#94A3B8] flex-shrink-0">Email Verified</span>
                      <span className="text-[#F8FAFC] font-medium text-right">
                        {paymentMethod.kyc.email_verified ? '✓ Yes' : '✗ No'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center gap-4">
                      <span className="text-[#94A3B8] flex-shrink-0">Persona Verified</span>
                      <span className="text-[#F8FAFC] font-medium text-right">
                        {paymentMethod.kyc.persona_verified ? '✓ Yes' : '✗ No'}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Rejection Reason (if applicable) */}
            {paymentMethod.status === 'rejected' && paymentMethod.rejection_reason && (
              <div className="mb-8 p-4 rounded-lg border border-[#EF4444] bg-[#EF4444]/10">
                <h3 className="text-sm font-semibold text-[#EF4444] uppercase mb-2">Rejection Reason</h3>
                <p className="text-sm text-[#F8FAFC]">{paymentMethod.rejection_reason}</p>
                {paymentMethod.rejected_at && (
                  <p className="text-xs text-[#94A3B8] mt-2">
                    Rejected on {new Date(paymentMethod.rejected_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}

            {/* Timeline Section */}
            <div>
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Activity Timeline
              </h2>
              <Timeline events={timelineEvents} />
            </div>
          </div>

          {/* Confirmation Dialog */}
          <ConfirmationDialog
            isOpen={confirmDialog.isOpen}
            onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
            onConfirm={handleConfirmAction}
            title={
              confirmDialog.type === 'approve'
                ? 'Approve Payment Method?'
                : 'Reject Payment Method?'
            }
            message={
              confirmDialog.type === 'approve'
                ? `You are about to approve this payment method for ${paymentMethod.researcher?.username}. This will allow them to receive payouts using this method.`
                : 'You are about to reject this payment method. Please provide a reason for rejection.'
            }
            confirmText={
              confirmDialog.type === 'approve' ? 'Approve Payment Method' : 'Reject Payment Method'
            }
            type={confirmDialog.type}
            requireNotes={confirmDialog.type === 'reject'}
            notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
            notesPlaceholder={
              confirmDialog.type === 'reject'
                ? 'Explain why this payment method is being rejected...'
                : 'Add optional notes...'
            }
            isLoading={approveMutation.isLoading || rejectMutation.isLoading}
          />
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
