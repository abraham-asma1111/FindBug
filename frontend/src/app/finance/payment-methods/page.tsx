'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import PaymentMethodsTable from '@/components/finance/PaymentMethodsTable';
import BulkActionBar from '@/components/finance/BulkActionBar';
import ConfirmationDialog from '@/components/finance/ConfirmationDialog';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

export default function FinancePaymentMethodsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const statusFilter = searchParams.get('status') || 'pending';
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({ isOpen: false, type: 'approve' });

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch data based on status filter - use specific endpoint for each status
  const endpoint = `/payment-methods/status/${statusFilter}`;

  const { data, isLoading, refetch } = useApiQuery<any>({ 
    endpoint,
    // Add status as a query key dependency so it refetches when status changes
    queryKey: [endpoint, statusFilter]
  });

  // Refetch data when status filter changes
  useEffect(() => {
    refetch();
  }, [statusFilter, refetch]);

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint, statusFilter] });
      refetch(); // Refetch immediately after approval
      setSelectedIds([]);
      setConfirmDialog({ isOpen: false, type: 'approve' });
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint, statusFilter] });
      refetch(); // Refetch immediately after rejection
      setSelectedIds([]);
      setConfirmDialog({ isOpen: false, type: 'reject' });
    },
  });



  // Payment methods are returned as an array directly (already filtered by backend)
  const paymentMethods = Array.isArray(data) ? data : [];

  // Apply search filter only (status filtering done by backend)
  const filteredPayments = paymentMethods.filter((payment: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payment.researcher?.username?.toLowerCase().includes(query) ||
        payment.researcher?.email?.toLowerCase().includes(query) ||
        payment.account_name?.toLowerCase().includes(query) ||
        payment.account_number?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const columns = [
    {
      key: 'researcher',
      label: 'Researcher',
      sortable: true,
      render: (value: any) => (
        <div className="min-w-0">
          <p className="text-[#F8FAFC] truncate">{value?.username || value?.full_name || 'Unknown'}</p>
          <p className="text-xs text-[#94A3B8] truncate">{value?.email}</p>
        </div>
      ),
    },
    {
      key: 'account_name',
      label: 'Account Holder',
      sortable: true,
      render: (value: any, row: any) => (
        <div className="min-w-0">
          <p className="font-semibold text-[#F8FAFC] truncate">{value || 'N/A'}</p>
          <p className="text-xs text-[#94A3B8] truncate">
            {row.method_type?.replace('_', ' ').toUpperCase()}
          </p>
        </div>
      ),
    },
    {
      key: 'account_number',
      label: 'Account Details',
      sortable: true,
      render: (value: any, row: any) => (
        <div className="min-w-0">
          <p className="font-medium text-[#F8FAFC] truncate">
            {row.method_type === 'bank_transfer' ? `****${value?.slice(-4)}` : value}
          </p>
          {row.bank_name && (
            <p className="text-xs text-[#94A3B8] truncate">{row.bank_name}</p>
          )}
        </div>
      ),
    },
    {
      key: 'kyc',
      label: 'KYC STATUS',
      sortable: false,
      render: (value: any) => {
        if (!value) {
          return <span className="inline-block px-2 py-1 rounded text-xs font-bold bg-[#64748B] text-white whitespace-nowrap">NO KYC</span>;
        }
        const isVerified = value.email_verified && value.persona_verified;
        return (
          <span className={`inline-block px-2 py-1 rounded text-xs font-bold whitespace-nowrap ${
            isVerified ? 'bg-[#10B981]' : 'bg-[#F59E0B]'
          } text-white`}>
            {isVerified ? '✓ VERIFIED' : 'PARTIAL'}
          </span>
        );
      },
    },
    {
      key: 'is_verified',
      label: 'Status',
      sortable: true,
      render: (value: any, row: any) => {
        if (row.status === 'rejected') {
          return <span className="inline-block px-2 py-1 rounded text-xs font-bold uppercase bg-[#EF4444] text-white whitespace-nowrap">REJECTED</span>;
        }
        return (
          <span className={`inline-block px-2 py-1 rounded text-xs font-bold uppercase whitespace-nowrap ${
            value ? 'bg-[#10B981]' : 'bg-[#F59E0B]'
          } text-white`}>
            {value ? 'APPROVED' : 'PENDING'}
          </span>
        );
      },
    },
    {
      key: 'created_at',
      label: 'Submitted',
      sortable: true,
      render: (value: any) => <span className="text-[#94A3B8] whitespace-nowrap text-sm">{new Date(value).toLocaleDateString()}</span>,
    },
  ];

  const handleBulkApprove = () => setConfirmDialog({ isOpen: true, type: 'approve' });
  const handleBulkReject = () => setConfirmDialog({ isOpen: true, type: 'reject' });

  const handleConfirmAction = async (notes?: string) => {
    for (const id of selectedIds) {
      if (confirmDialog.type === 'approve') {
        await approveMutation.mutateAsync({ endpoint: `/payment-methods/${id}/approve`, data: {} });
      } else {
        await rejectMutation.mutateAsync({ endpoint: `/payment-methods/${id}/reject`, data: { reason: notes } });
      }
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payment Method Verification"
          subtitle={`${filteredPayments.length} payment methods`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="mb-6 flex gap-2">
            <Link href="/finance/payment-methods?status=pending">
              <Button variant={statusFilter === 'pending' ? 'warning' : 'secondary'} size="sm">
                Pending
              </Button>
            </Link>
            <Link href="/finance/payment-methods?status=approved">
              <Button variant={statusFilter === 'approved' ? 'success' : 'secondary'} size="sm">
                Approved
              </Button>
            </Link>
            <Link href="/finance/payment-methods?status=rejected">
              <Button variant={statusFilter === 'rejected' ? 'danger' : 'secondary'} size="sm">
                Rejected
              </Button>
            </Link>
          </div>

          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher, account name, or account number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading payment methods...</p>
            </div>
          ) : (
            <PaymentMethodsTable
              data={filteredPayments}
              columns={columns}
              selectable={statusFilter === 'pending'}
              onSelectionChange={setSelectedIds}
              onRowClick={(row) => window.location.href = `/finance/payment-methods/${row.id}`}
            />
          )}

          {statusFilter === 'pending' && (
            <BulkActionBar
              selectedCount={selectedIds.length}
              totalCount={filteredPayments.length}
              onClearSelection={() => setSelectedIds([])}
              actions={[
                {
                  label: 'Approve Selected',
                  onClick: handleBulkApprove,
                  variant: 'primary',
                  icon: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>,
                },
                {
                  label: 'Reject Selected',
                  onClick: handleBulkReject,
                  variant: 'danger',
                  icon: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>,
                },
              ]}
            />
          )}

          <ConfirmationDialog
            isOpen={confirmDialog.isOpen}
            onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
            onConfirm={handleConfirmAction}
            title={confirmDialog.type === 'approve' ? `Approve ${selectedIds.length} Payment Methods?` : `Reject ${selectedIds.length} Payment Methods?`}
            message={confirmDialog.type === 'approve' ? 'Approve these payment methods for researcher payouts.' : 'Provide rejection reason for these payment methods.'}
            confirmText={confirmDialog.type === 'approve' ? 'Approve Payment Methods' : 'Reject Payment Methods'}
            type={confirmDialog.type}
            requireNotes={confirmDialog.type === 'reject'}
            notesLabel={confirmDialog.type === 'reject' ? 'Rejection Reason' : 'Notes'}
            isLoading={approveMutation.isLoading || rejectMutation.isLoading}
          />
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
