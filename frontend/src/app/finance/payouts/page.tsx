'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import TransactionTable from '@/components/finance/TransactionTable';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinancePayoutsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || 'requested';
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: `/wallet/payouts?status=${statusFilter}&limit=1000`,
  });

  const payouts = data?.payouts || [];

  const filteredPayouts = payouts.filter((payout: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payout.researcher_name?.toLowerCase().includes(query) ||
        payout.id?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const columns = [
    {
      key: 'id',
      label: 'Payout ID',
      sortable: true,
      render: (value: any) => (
        <span className="font-semibold text-[#F8FAFC]">#{value.slice(0, 8)}</span>
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
      render: (value: any) => (
        <span className="font-bold text-[#10B981]">${(value || 0).toLocaleString()} ETB</span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value: any) => {
        const colors: Record<string, string> = {
          requested: 'bg-[#F59E0B]',
          processing: 'bg-[#3B82F6]',
          completed: 'bg-[#10B981]',
          failed: 'bg-[#EF4444]',
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

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Payouts"
          subtitle={`${filteredPayouts.length} payouts`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="mb-6 flex gap-2">
            <Link href="/finance/payouts?status=requested">
              <Button variant={statusFilter === 'requested' ? 'warning' : 'secondary'} size="sm">
                Requested
              </Button>
            </Link>
            <Link href="/finance/payouts?status=processing">
              <Button variant={statusFilter === 'processing' ? 'warning' : 'secondary'} size="sm">
                Processing
              </Button>
            </Link>
            <Link href="/finance/payouts?status=completed">
              <Button variant={statusFilter === 'completed' ? 'success' : 'secondary'} size="sm">
                Completed
              </Button>
            </Link>
          </div>

          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher or payout ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading payouts...</p>
            </div>
          ) : (
            <TransactionTable
              data={filteredPayouts}
              columns={columns}
              selectable={false}
              linkPrefix="/finance/payouts"
            />
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
