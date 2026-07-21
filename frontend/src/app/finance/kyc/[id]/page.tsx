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

export default function KYCDetailPage() {
  const user = useAuthStore((state) => state.user);
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const kycId = params.id as string;
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

  // Fetch KYC details
  const { data: kyc, isLoading } = useApiQuery<any>({
    endpoint: `/kyc/verifications/${kycId}`,
    queryKey: [`/kyc/verifications/${kycId}`],
  });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/kyc/verifications/${kycId}`] });
      setConfirmDialog({ isOpen: false, type: 'approve' });
      router.push('/finance/kyc?status=approved');
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/kyc/verifications/${kycId}`] });
      setConfirmDialog({ isOpen: false, type: 'reject' });
      router.push('/finance/kyc?status=rejected');
    },
  });

  const handleConfirmAction = async (notes?: string) => {
    if (confirmDialog.type === 'approve') {
      await approveMutation.mutateAsync({
        endpoint: `/kyc/verifications/${kycId}/approve`,
        data: {},
      });
    } else {
      await rejectMutation.mutateAsync({
        endpoint: `/kyc/verifications/${kycId}/reject?reason=${encodeURIComponent(notes || '')}`,
        data: {},
      });
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="KYC Verification Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading KYC details...</p>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  if (!kyc) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user ? (
          <PortalShell
            user={user}
            title="KYC Not Found"
            subtitle="The KYC verification could not be found"
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8] mb-4">KYC verification not found</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/finance/kyc')}
              >
                Back to KYC Verifications
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

  const timelineEvents = [
    {
      id: `${kycId}-created`,
      type: 'created' as const,
      title: 'KYC Verification Submitted',
      description: 'Researcher submitted KYC verification',
      timestamp: kyc.submitted_at || kyc.created_at,
      user: kyc.user_name || 'Researcher',
    },
    ...(kyc.status === 'approved' && kyc.reviewed_at
      ? [
          {
            id: `${kycId}-approved`,
            type: 'approved' as const,
            title: 'KYC Verification Approved',
            description: 'KYC verification approved by finance officer',
            timestamp: kyc.reviewed_at,
            user: 'Finance Officer',
          },
        ]
      : []),
    ...(kyc.status === 'rejected' && kyc.reviewed_at
      ? [
          {
            id: `${kycId}-rejected`,
            type: 'rejected' as const,
            title: 'KYC Verification Rejected',
            description: kyc.rejection_reason || 'KYC verification rejected',
            timestamp: kyc.reviewed_at,
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
          title="KYC Verification Details"
          subtitle={`${kyc.user_name || 'Researcher'} - ${kyc.user_email}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Header Actions */}
          {kyc.status === 'pending' && (
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
                Approve KYC
              </Button>
            </div>
          )}

          {/* Streamlined Single Card Layout */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
            {/* KYC Information Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                KYC Verification Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Status</span>
                  <div className="flex-shrink-0">{getStatusBadge(kyc.status)}</div>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Email Verified</span>
                  <span className={`font-semibold text-right ${kyc.email_verified ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                    {kyc.email_verified ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Persona Verified</span>
                  <span className={`font-semibold text-right ${kyc.persona_verified ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                    {kyc.persona_verified ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                {kyc.document_type && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Document Type</span>
                    <span className="text-[#F8FAFC] font-medium text-right capitalize">
                      {kyc.document_type.replace('_', ' ')}
                    </span>
                  </div>
                )}
                {kyc.document_number && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Document Number</span>
                    <span className="text-[#F8FAFC] font-medium font-mono text-right">
                      {kyc.document_number}
                    </span>
                  </div>
                )}
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Submitted</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {new Date(kyc.submitted_at || kyc.created_at).toLocaleDateString()}
                  </span>
                </div>
                {kyc.reviewed_at && (
                  <div className="flex justify-between items-center gap-4">
                    <span className="text-[#94A3B8] flex-shrink-0">Reviewed</span>
                    <span className="text-[#F8FAFC] font-medium text-right">
                      {new Date(kyc.reviewed_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Researcher Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                Researcher Information
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Name</span>
                  <span className="text-[#F8FAFC] font-medium text-right">
                    {kyc.user_name || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-4">
                  <span className="text-[#94A3B8] flex-shrink-0">Email</span>
                  <span className="text-[#F8FAFC] font-medium text-right">{kyc.user_email}</span>
                </div>
              </div>
            </div>

            {/* Rejection Reason (if applicable) */}
            {kyc.status === 'rejected' && kyc.rejection_reason && (
              <div className="mb-8 p-4 rounded-lg border border-[#EF4444] bg-[#EF4444]/10">
                <h3 className="text-sm font-semibold text-[#EF4444] uppercase mb-2">Rejection Reason</h3>
                <p className="text-sm text-[#F8FAFC]">{kyc.rejection_reason}</p>
                {kyc.reviewed_at && (
                  <p className="text-xs text-[#94A3B8] mt-2">
                    Rejected on {new Date(kyc.reviewed_at).toLocaleString()}
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
                ? 'Approve KYC Verification?'
                : 'Reject KYC Verification?'
            }
            message={
              confirmDialog.type === 'approve'
                ? `You are about to approve KYC verification for ${kyc.user_name}. This will mark their identity as verified.`
                : 'You are about to reject this KYC verification. Please provide a reason for rejection.'
            }
            confirmText={
              confirmDialog.type === 'approve' ? 'Approve KYC' : 'Reject KYC'
            }
            type={confirmDialog.type}
            requireNotes={confirmDialog.type === 'reject'}
            notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
            notesPlaceholder={
              confirmDialog.type === 'reject'
                ? 'Explain why this KYC verification is being rejected...'
                : 'Add optional notes...'
            }
            isLoading={approveMutation.isLoading || rejectMutation.isLoading}
          />
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
