'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

interface WalletBalance {
  balance: number;
  reserved_balance: number;
  available_balance: number;
  currency: string;
}

interface Transaction {
  transaction_id: string;
  transaction_type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  reference_type: string;
  reference_id: string;
  description: string;
  created_at: string;
}

export default function PlatformWalletPage() {
  const user = useAuthStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('all');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch platform wallet balance
  const { data: balanceData, isLoading: balanceLoading } = useApiQuery<WalletBalance>({
    endpoint: '/wallet/platform/balance',
  });

  // Fetch platform wallet transactions
  const { data: transactionsData, isLoading: transactionsLoading } = useApiQuery<{ transactions: Transaction[] }>({
    endpoint: '/wallet/platform/transactions?limit=100',
  });

  const transactions = transactionsData?.transactions || [];

  // Apply search filter
  const filteredTransactions = transactions.filter((tx) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        tx.transaction_id?.toLowerCase().includes(query) ||
        tx.transaction_type?.toLowerCase().includes(query) ||
        tx.reference_type?.toLowerCase().includes(query) ||
        tx.description?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  // Calculate stats
  const totalTransactions = transactions.length;
  const totalRevenue = balanceData?.balance || 0;
  const avgCommission = totalTransactions > 0 ? totalRevenue / totalTransactions : 0;

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Platform Wallet"
          subtitle="Real-time commission tracking and revenue analytics"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Hero Balance Card with Gradient */}
          <div className="mb-8 relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#3B82F6] via-[#2563EB] to-[#1D4ED8] p-8 shadow-2xl">
            {/* Decorative Elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-32 -mt-32"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-5 rounded-full -ml-24 -mb-24"></div>
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-blue-100 text-sm font-medium mb-1 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Total Platform Revenue
                  </p>
                  {balanceLoading ? (
                    <div className="h-12 w-64 bg-white/10 animate-pulse rounded-lg"></div>
                  ) : (
                    <h1 className="text-5xl font-bold text-white mb-2">
                      {totalRevenue.toLocaleString()} <span className="text-3xl text-blue-100">{balanceData?.currency || 'ETB'}</span>
                    </h1>
                  )}
                  <p className="text-blue-100 text-sm">
                    From {totalTransactions} commission transaction{totalTransactions !== 1 ? 's' : ''}
                  </p>
                </div>
                
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <p className="text-blue-100 text-xs mb-1">Available Balance</p>
                  <p className="text-white text-xl font-bold">{(balanceData?.available_balance || 0).toLocaleString()} ETB</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <p className="text-blue-100 text-xs mb-1">Avg Commission</p>
                  <p className="text-white text-xl font-bold">{avgCommission.toLocaleString(undefined, {maximumFractionDigits: 0})} ETB</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                  <p className="text-blue-100 text-xs mb-1">Commission Rate</p>
                  <p className="text-white text-xl font-bold">45%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Total Transactions */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-6 hover:border-[#3B82F6] transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-[#3B82F6]/10 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <span className="text-[#10B981] text-sm font-semibold">+100%</span>
              </div>
              <h3 className="text-[#94A3B8] text-sm mb-1">Total Transactions</h3>
              <p className="text-[#F8FAFC] text-3xl font-bold">{totalTransactions}</p>
            </div>

            {/* Commission Structure */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-6 hover:border-[#10B981] transition-all duration-300 hover:shadow-lg hover:shadow-green-500/20">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-[#10B981]/10 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-[#3B82F6] text-xs font-semibold">30% + 15%</span>
              </div>
              <h3 className="text-[#94A3B8] text-sm mb-1">Commission Model</h3>
              <p className="text-[#F8FAFC] text-lg font-semibold">Dual Structure</p>
              <p className="text-[#64748B] text-xs mt-1">Org 30% + Researcher 15%</p>
            </div>

            {/* Reserved Balance */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-6 hover:border-[#F59E0B] transition-all duration-300 hover:shadow-lg hover:shadow-amber-500/20">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-[#F59E0B]/10 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <span className="text-[#64748B] text-xs font-semibold">Locked</span>
              </div>
              <h3 className="text-[#94A3B8] text-sm mb-1">Reserved Balance</h3>
              <p className="text-[#F8FAFC] text-3xl font-bold">{(balanceData?.reserved_balance || 0).toLocaleString()}</p>
              <p className="text-[#64748B] text-xs mt-1">ETB</p>
            </div>
          </div>

          {/* Info Banner */}
          <div className="mb-6 bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-[#3B82F6]/30 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-start gap-3">
              <div className="bg-[#3B82F6]/10 p-2 rounded-lg">
                <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-[#F8FAFC] font-semibold mb-1">About Platform Commission</p>
                <p className="text-[#94A3B8] text-sm">
                  The platform earns 45% commission on each bounty payment: 30% from the organization (on top of bounty) + 15% from the researcher (deducted from bounty). All commissions are automatically credited to this wallet when bounty payments are approved.
                </p>
              </div>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="mb-6 flex gap-4">
            <div className="flex-1 relative">
              <svg className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search by transaction ID, type, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-[#1E293B] border border-[#334155] rounded-xl text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent transition-all"
              />
            </div>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-xl text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent transition-all"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          {/* Transactions Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-[#F8FAFC] flex items-center gap-2">
                <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                Commission Transaction History
              </h3>
              <span className="text-[#64748B] text-sm">{filteredTransactions.length} transaction{filteredTransactions.length !== 1 ? 's' : ''}</span>
            </div>

            {/* Loading State */}
            {transactionsLoading && (
              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
                <p className="text-[#94A3B8]">Loading transactions...</p>
              </div>
            )}

            {/* Empty State */}
            {!transactionsLoading && filteredTransactions.length === 0 && (
              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-12 text-center">
                <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Transactions Found</h3>
                <p className="text-[#94A3B8]">
                  {searchQuery
                    ? 'No transactions match your search criteria. Try adjusting your filters.'
                    : 'Commission transactions will appear here when bounty payments are approved.'}
                </p>
              </div>
            )}

            {/* Transactions List */}
            {!transactionsLoading && filteredTransactions.length > 0 && (
              <div className="space-y-4">
                {filteredTransactions.map((tx) => (
                  <div
                    key={tx.transaction_id || Math.random()}
                    className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 hover:border-[#3B82F6] transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      {/* Left Section: Transaction Details */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="text-lg font-semibold text-[#F8FAFC]">
                            Commission from Bounty Payment
                          </h3>
                          <span className="px-2 py-1 bg-[#10B981] rounded text-xs font-bold text-white uppercase">
                            {tx.transaction_type}
                          </span>
                        </div>

                        <p className="text-[#94A3B8] mb-4 line-clamp-1">{tx.description}</p>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-[#64748B] mb-1">Reference Type</p>
                            <p className="text-[#F8FAFC] font-medium capitalize">{tx.reference_type?.replace('_', ' ') || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-[#64748B] mb-1">Transaction Date</p>
                            <p className="text-[#F8FAFC]">
                              {new Date(tx.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-[#64748B] mb-1">Transaction ID</p>
                            <p className="text-[#F8FAFC] font-mono text-xs">{tx.transaction_id ? tx.transaction_id.substring(0, 8) : 'N/A'}...</p>
                          </div>
                          <div>
                            <p className="text-[#64748B] mb-1">Reference ID</p>
                            <p className="text-[#F8FAFC] font-mono text-xs">{tx.reference_id ? tx.reference_id.substring(0, 8) : 'N/A'}...</p>
                          </div>
                        </div>
                      </div>

                      {/* Right Section: Amount Info */}
                      <div className="flex flex-col items-end gap-4 min-w-[240px]">
                        <div className="text-right space-y-2 w-full">
                          <div className="flex justify-between items-center">
                            <span className="text-[#64748B] text-sm">Commission Amount:</span>
                            <span className="text-[#10B981] font-bold text-lg">
                              {tx.amount.toLocaleString()} ETB
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-[#64748B] text-sm">Balance Before:</span>
                            <span className="text-[#94A3B8] font-semibold">
                              {tx.balance_before.toLocaleString()} ETB
                            </span>
                          </div>
                          <div className="border-t border-[#334155] pt-2 flex justify-between items-center">
                            <span className="text-[#94A3B8] text-sm">Balance After:</span>
                            <span className="text-[#F8FAFC] font-bold text-lg">
                              {tx.balance_after.toLocaleString()} ETB
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
