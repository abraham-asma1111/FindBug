'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import TransactionTable from '@/components/finance/TransactionTable';
import BulkActionBar from '@/components/finance/BulkActionBar';
import ConfirmationDialog from '@/components/finance/ConfirmationDialog';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';

export default function FinancePaymentsPage() {
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

  const endpoint = `/payments/history?status=${statusFilter}&limit=1000`;

  const { data, isLoading } = useApiQuery<any>({ endpoint });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint] });
      setSelectedIds([]);
      setConfirmDialog({ isOpen: false, type: 'approve' });
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint] });
      setSelectedIds([]);
      setConfirmDialog({ isOpen: false, type: 'reject' });
    },
  });

  const payments = data?.payments || [];

  const filteredPayments = payments.filter((payment: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payment.researcher_name?.toLowerCase().includes(query) ||
        payment.report_number?.toLowerCase().includes(query) ||
        payment.id?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const columns = [
    {
      key: 'report_title',
      label: 'Report',
      sortable: true,
      render: (value: any, row: any) => (
        <div>
          <p className="font-semibold text-[#F8FAFC]">
            {value || `Payment #${row.id.slice(0, 8)}`}
          </p>
          <p className="text-xs text-[#94A3B8]">
            Report #{row.report_number || row.id.slice(0, 8)}
          </p>
        </div>
      ),
    },
    {
      key: 'researcher_name',
      label: 'Researcher',
      sortable: true,
      render: (value: any) => <span className="text-[#F8FAFC]">{value || 'Unknown'}</span>,
    },
    {
      key: 'amount',
      label: 'Amount',
      sortable: true,
      render: (value: any) => {
        const commission = (value || 0) * 0.3;
        return (
          <div>
            <p className="font-bold text-[#10B981]">${(value || 0).toLocaleString()} ETB</p>
            <p className="text-xs text-[#94A3B8]">+ ${commission.toLocaleString()} commission</p>
          </div>
        );
      },
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value: any) => {
        const colors: Record<string, string> = {
          pending: 'bg-[#F59E0B]',
          approved: 'bg-[#3B82F6]',
          completed: 'bg-[#10B981]',
          rejected: 'bg-[#EF4444]',
        };
        return (
          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${colors[value] || 'bg-[#94A3B8]'} text-white`}>
            {value}
          </span>
        );
      },
    },
    {
      key: 'created_at',
      label: 'Date',
      sortable: true,
      render: (value: any) => <span className="text-[#94A3B8]">{new Date(value).toLocaleDateString()}</span>,
    },
  ];

  const handleBulkApprove = () => setConfirmDialog({ isOpen: true, type: 'approve' });
  const handleBulkReject = () => setConfirmDialog({ isOpen: true, type: 'reject' });

  const handleConfirmAction = async (notes?: string) => {
    for (const id of selectedIds) {
      if (confirmDialog.type === 'approve') {
        await approveMutation.mutateAsync({ endpoint: `/payments/${id}/approve`, data: { notes } });
      } else {
        await rejectMutation.mutateAsync({ endpoint: `/payments/${id}/reject`, data: { reason: notes } });
      }
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Bounty Payments"
          subtitle={`${filteredPayments.length} payments`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="mb-6 flex gap-2">
            <Link href="/finance/payments?status=pending">
              <Button variant={statusFilter === 'pending' ? 'warning' : 'secondary'} size="sm">
                Pending
              </Button>
            </Link>
            <Link href="/finance/payments?status=approved">
              <Button variant={statusFilter === 'approved' ? 'success' : 'secondary'} size="sm">
                Approved
              </Button>
            </Link>
            <Link href="/finance/payments?status=completed">
              <Button variant={statusFilter === 'completed' ? 'success' : 'secondary'} size="sm">
                Completed
              </Button>
            </Link>
          </div>

          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher, report ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading payments...</p>
            </div>
          ) : (
            <TransactionTable
              data={filteredPayments}
              columns={columns}
              selectable={statusFilter === 'pending'}
              onSelectionChange={setSelectedIds}
              linkPrefix="/finance/payments"
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
            title={confirmDialog.type === 'approve' ? `Approve ${selectedIds.length} Payments?` : `Reject ${selectedIds.length} Payments?`}
            message={confirmDialog.type === 'approve' ? 'Process payments and transfer funds to researchers.' : 'Provide rejection reason.'}
            confirmText={confirmDialog.type === 'approve' ? 'Approve Payments' : 'Reject Payments'}
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
