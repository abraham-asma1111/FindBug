'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceTransactionsPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch transactions (using payment history endpoint for now)
  const { data, isLoading } = useApiQuery<any>({
    endpoint: '/payments/history?limit=1000',
  });

  const transactions = data?.payments || [];

  // Filter transactions
  const filteredTransactions = transactions.filter((txn: any) => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch = 
        txn.transaction_id?.toLowerCase().includes(query) ||
        txn.report_title?.toLowerCase().includes(query) ||
        txn.researcher_name?.toLowerCase().includes(query) ||
        txn.organization_name?.toLowerCase().includes(query);
      if (!matchesSearch) return false;
    }

    // Type filter (based on status for now)
    if (typeFilter !== 'all') {
      if (typeFilter === 'bounty' && txn.status !== 'completed') return false;
      if (typeFilter === 'commission' && txn.status !== 'completed') return false;
    }

    // Status filter
    if (statusFilter !== 'all' && txn.status !== statusFilter) return false;

    // Date range filter
    if (dateRange !== 'all') {
      const txnDate = new Date(txn.created_at || txn.approved_at);
      const now = new Date();
      const daysAgo = dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90;
      const cutoffDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
      if (txnDate < cutoffDate) return false;
    }

    return true;
  });

  // Calculate totals
  const totalAmount = filteredTransactions.reduce((sum: number, txn: any) => sum + (txn.total_amount || 0), 0);
  const completedAmount = filteredTransactions
    .filter((txn: any) => txn.status === 'completed')
    .reduce((sum: number, txn: any) => sum + (txn.total_amount || 0), 0);
  const pendingAmount = filteredTransactions
    .filter((txn: any) => txn.status === 'pending' || txn.status === 'approved')
    .reduce((sum: number, txn: any) => sum + (txn.total_amount || 0), 0);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user && (
        <PortalShell
          user={user}
          title="Transactions"
          subtitle="All financial transactions"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Breadcrumb Navigation */}
          <div className="mb-6">
            <nav className="flex items-center gap-2 text-sm">
              <button
                onClick={() => router.push('/finance/dashboard')}
                className="text-[#64748B] hover:text-[#F8FAFC] transition-colors"
              >
                Finance
              </button>
              <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span className="text-[#F8FAFC] font-medium">
                Transactions
              </span>
            </nav>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Total Volume</p>
                <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-[#F8FAFC] mb-1">{totalAmount.toLocaleString()} ETB</p>
              <p className="text-[#64748B] text-sm">{filteredTransactions.length} transactions</p>
            </div>

            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Completed</p>
                <div className="w-10 h-10 rounded-lg bg-[#10B981]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-[#10B981] mb-1">{completedAmount.toLocaleString()} ETB</p>
              <p className="text-[#64748B] text-sm">
                {filteredTransactions.filter((t: any) => t.status === 'completed').length} completed
              </p>
            </div>

            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[#64748B] text-sm font-semibold uppercase tracking-wider">Pending</p>
                <div className="w-10 h-10 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-[#F59E0B] mb-1">{pendingAmount.toLocaleString()} ETB</p>
              <p className="text-[#64748B] text-sm">
                {filteredTransactions.filter((t: any) => t.status === 'pending' || t.status === 'approved').length} pending
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-[#1E293B] rounded-xl p-6 border border-[#334155] mb-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div>
                <label className="block text-[#94A3B8] text-sm font-medium mb-2">Search</label>
                <input
                  type="text"
                  placeholder="Transaction ID, report, researcher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                />
              </div>

              {/* Type Filter */}
              <div>
                <label className="block text-[#94A3B8] text-sm font-medium mb-2">Type</label>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="all">All Types</option>
                  <option value="bounty">Bounty Payment</option>
                  <option value="commission">Commission</option>
                  <option value="subscription">Subscription</option>
                  <option value="refund">Refund</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-[#94A3B8] text-sm font-medium mb-2">Status</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="failed">Failed</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              {/* Date Range */}
              <div>
                <label className="block text-[#94A3B8] text-sm font-medium mb-2">Date Range</label>
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value as any)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 90 days</option>
                  <option value="all">All time</option>
                </select>
              </div>
            </div>
          </div>

          {/* Transactions Table */}
          <div className="bg-[#1E293B] rounded-xl border border-[#334155] overflow-hidden">
            {isLoading ? (
              <div className="p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
                <p className="text-[#94A3B8]">Loading transactions...</p>
              </div>
            ) : filteredTransactions.length === 0 ? (
              <div className="p-12 text-center">
                <div className="w-16 h-16 rounded-full bg-[#334155]/30 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-[#94A3B8] text-lg">No transactions found</p>
                <p className="text-[#64748B] text-sm mt-2">
                  {searchQuery || typeFilter !== 'all' || statusFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Transactions will appear here once payments are processed'}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-[#0F172A]/50 border-b border-[#334155]">
                      <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Transaction ID</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Date</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Type</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Description</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Researcher</th>
                      <th className="px-6 py-4 text-right text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-4 text-center text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Status</th>
                      <th className="px-6 py-4 text-right text-xs font-bold text-[#94A3B8] uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]/30">
                    {filteredTransactions.map((txn: any) => (
                      <tr 
                        key={txn.payment_id} 
                        className="hover:bg-[#1E293B]/30 transition-colors cursor-pointer"
                        onClick={() => router.push(`/finance/transactions/${txn.payment_id}`)}
                      >
                        <td className="px-6 py-4">
                          <span className="text-[#3B82F6] font-mono text-sm">
                            {txn.transaction_id || `TXN-${txn.payment_id?.slice(0, 8)}`}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-[#F8FAFC] text-sm">
                            {new Date(txn.created_at || txn.approved_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            })}
                          </span>
                          <p className="text-[#64748B] text-xs mt-1">
                            {new Date(txn.created_at || txn.approved_at).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-3 py-1 rounded-lg text-xs font-bold uppercase bg-[#8B5CF6]/20 text-[#8B5CF6]">
                            Bounty
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-[#F8FAFC] font-medium">{txn.report_title || 'Payment'}</p>
                          <p className="text-[#64748B] text-sm mt-1">{txn.report_number || 'N/A'}</p>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-[#F8FAFC]">{txn.researcher_name || 'N/A'}</span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <p className="text-[#10B981] font-bold text-lg">
                            {txn.total_amount?.toLocaleString() || 0} ETB
                          </p>
                          <p className="text-[#64748B] text-xs mt-1">
                            Researcher: {txn.researcher_amount?.toLocaleString() || 0} ETB
                          </p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase inline-block ${
                            txn.status === 'completed' ? 'bg-[#10B981]/20 text-[#10B981]' :
                            txn.status === 'approved' ? 'bg-[#3B82F6]/20 text-[#3B82F6]' :
                            txn.status === 'pending' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                            txn.status === 'failed' ? 'bg-[#EF4444]/20 text-[#EF4444]' :
                            'bg-[#64748B]/20 text-[#64748B]'
                          }`}>
                            {txn.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/finance/transactions/${txn.payment_id}`);
                            }}
                            className="text-[#3B82F6] hover:text-[#60A5FA] font-semibold text-sm transition-colors"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
