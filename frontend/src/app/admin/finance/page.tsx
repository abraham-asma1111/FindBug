'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function AdminFinancePage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: stats } = useApiQuery<any>({
    endpoint: '/admin/finance/statistics',
  });

  const { data: recentTransactions } = useApiQuery<any>({
    endpoint: '/admin/finance/transactions?limit=5',
  });

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finance"
          subtitle="Platform financial overview"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Financial Overview
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Finance
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Monitor platform revenue, payouts, and financial metrics.
              </p>
            </div>
          </section>

          {/* Financial Stats */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Revenue
              </p>
              <p className="mt-2 text-3xl font-bold text-[#10B981]">
                {stats?.total_revenue?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Payouts
              </p>
              <p className="mt-2 text-3xl font-bold text-[#EF4444]">
                {stats?.total_payouts?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Platform Fees
              </p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">
                {stats?.platform_fees?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Net Profit
              </p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">
                {stats?.net_profit?.toLocaleString() || 0} ETB
              </p>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F8FAFC]">Recent Transactions</h2>
              <Link href="/finance/reports">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>
            <div className="space-y-3">
              {!recentTransactions?.transactions || recentTransactions.transactions.length === 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                  <p className="text-[#94A3B8]">No transactions found</p>
                </div>
              ) : (
                recentTransactions.transactions.map((transaction: any) => (
                  <div key={transaction.id} className="bg-[#1E293B] rounded-lg border border-[#334155] p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-[#F8FAFC] mb-1">
                          {transaction.description}
                        </h3>
                        <p className="text-sm text-[#94A3B8]">
                          {transaction.type} • {new Date(transaction.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                          transaction.type === 'credit' ? 'text-[#10B981]' : 'text-[#EF4444]'
                        }`}>
                          {transaction.type === 'credit' ? '+' : '-'}{transaction.amount?.toLocaleString()} ETB
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
