'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import TransactionTable from '@/components/finance/TransactionTable';

export default function FinanceTransactionsPage() {
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data, isLoading } = useApiQuery<any>({
    endpoint: '/wallet/transactions?limit=1000',
  });

  const transactions = data?.transactions || [];

  const filteredTransactions = transactions.filter((txn: any) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        txn.description?.toLowerCase().includes(query) ||
        txn.id?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const columns = [
    {
      key: 'id',
      label: 'Transaction ID',
      sortable: true,
      render: (value: any) => (
        <span className="font-semibold text-[#F8FAFC]">#{value.slice(0, 8)}</span>
      ),
    },
    {
      key: 'type',
      label: 'Type',
      sortable: true,
      render: (value: any) => (
        <span className="text-[#94A3B8] capitalize">{value?.replace('_', ' ')}</span>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      sortable: true,
      render: (value: any) => <span className="text-[#F8FAFC]">{value || '-'}</span>,
    },
    {
      key: 'amount',
      label: 'Amount',
      sortable: true,
      render: (value: any) => (
        <span className={`font-bold ${value >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
          {value >= 0 ? '+' : ''}${Math.abs(value || 0).toLocaleString()} ETB
        </span>
      ),
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
          title="All Transactions"
          subtitle={`${filteredTransactions.length} transactions`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading transactions...</p>
            </div>
          ) : (
            <TransactionTable
              data={filteredTransactions}
              columns={columns}
              selectable={false}
            />
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
