'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';

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
  const [isPayoutModalOpen, setIsPayoutModalOpen] = useState(false);
  const [isConfigureMethodsOpen, setIsConfigureMethodsOpen] = useState(false);
  const [addMethodOpen, setAddMethodOpen] = useState(false);
  const [addMethodForm, setAddMethodForm] = useState({ method_type: 'bank_transfer', account_name: '', account_number: '', bank_name: '' });
  const [addMethodError, setAddMethodError] = useState('');
  const [payoutAmount, setPayoutAmount] = useState('');
  const [selectedMethodId, setSelectedMethodId] = useState('');
  const [payoutError, setPayoutError] = useState<string | null>(null);


  // Fetch platform wallet balance
  const { data: balanceData, isLoading: balanceLoading } = useApiQuery<WalletBalance>({
    endpoint: '/wallet/platform/balance',
  });

  // Fetch platform wallet transactions
  const { data: transactionsData, isLoading: transactionsLoading, refetch: refetchTransactions } = useApiQuery<{ transactions: Transaction[] }>({
    endpoint: '/wallet/platform/transactions?limit=100',
  });

  // Fetch completed bounty payments to compute true total commission
  const { data: bountyData, isLoading: bountyLoading } = useApiQuery<any>({
    endpoint: '/bounty-payments?status_filter=completed',
  });

  // Fetch admin payment methods
  const { data: methodsData, refetch: refetchMethods } = useApiQuery<any[]>(
    `/payment-methods/${user?.id || ''}`,
    { enabled: !!user?.id }
  );
  const paymentMethods = Array.isArray(methodsData) ? methodsData : [];

  const { mutate: withdrawCommission, isLoading: isWithdrawing } = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      setIsPayoutModalOpen(false);
      setPayoutAmount('');
      setSelectedMethodId('');
      setPayoutError(null);
      window.location.reload();
    },
    onError: (error: any) => {
      setPayoutError(error.message || 'Failed to process payout.');
    }
  });

  const handlePayoutSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPayoutError(null);

    const amountNum = parseFloat(payoutAmount);
    if (!amountNum || amountNum <= 0) {
      setPayoutError('Please enter a valid amount.');
      return;
    }
    if (amountNum > (balanceData?.available_balance || 0)) {
      setPayoutError('Amount exceeds available balance.');
      return;
    }
    if (!selectedMethodId) {
      setPayoutError('Please select a payment method.');
      return;
    }
    
    const selectedMethod = paymentMethods.find(m => m.id === selectedMethodId);
    if (!selectedMethod) {
      setPayoutError('Invalid payment method selected.');
      return;
    }

    const accountDetails = {
      account_name: selectedMethod.account_name,
      account_number: selectedMethod.account_number,
      bank_name: selectedMethod.bank_name || undefined
    };

    withdrawCommission({
      endpoint: '/wallet/platform/withdraw',
      amount: amountNum,
      payment_method: selectedMethod.method_type,
      account_details: accountDetails
    });
  };

  const handleAddMethod = () => {
    setAddMethodError('');
    if (!addMethodForm.account_name || !addMethodForm.account_number) {
      setAddMethodError('Please fill in all required fields');
      return;
    }
    if (addMethodForm.method_type === 'bank_transfer' && !addMethodForm.bank_name) {
      setAddMethodError('Bank name is required for bank transfers');
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payment-methods/${user?.id || ''}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(addMethodForm),
    }).then((res) => {
      if (res.ok) {
        setAddMethodForm({ method_type: 'bank_transfer', account_name: '', account_number: '', bank_name: '' });
        setAddMethodOpen(false);
        refetchMethods();
      } else {
        res.json().then(d => setAddMethodError(d.detail || 'Failed to add method'));
      }
    });
  };

  const handleDeleteMethod = (methodId: string) => {
    if (confirm('Delete this payment method?')) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payment-methods/${methodId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      }).then(() => refetchMethods());
    }
  };

  const transactions = transactionsData?.transactions || [];

  // Apply search and period filters
  const filteredTransactions = transactions.filter((tx) => {
    // Hide incorrect historical debit entries that were mistakenly recorded as bounty_payments on the platform wallet
    if (tx.transaction_type === 'debit' && tx.reference_type === 'bounty_payment') {
      return false;
    }

    // Show all valid platform transactions (both credits and debits)
    // Credits = commission earned, Debits = payouts made
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch = (
        tx.transaction_id?.toLowerCase().includes(query) ||
        tx.transaction_type?.toLowerCase().includes(query) ||
        tx.reference_type?.toLowerCase().includes(query) ||
        tx.description?.toLowerCase().includes(query)
      );
      if (!matchesSearch) return false;
    }

    // Period filter
    if (selectedPeriod !== 'all') {
      const txDate = new Date(tx.created_at);
      const now = new Date();
      
      if (selectedPeriod === 'today') {
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        if (txDate < today) return false;
      } else if (selectedPeriod === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        if (txDate < weekAgo) return false;
      } else if (selectedPeriod === 'month') {
        const monthAgo = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
        if (txDate < monthAgo) return false;
      }
    }

    return true;
  });

  // Calculate stats
  const completedBounties = bountyData?.bounty_payments || [];
  const trueTotalCommission = completedBounties.reduce((sum: number, p: any) => sum + (p.commission_amount || 0), 0);
  const totalBountyTransactions = completedBounties.length;
  
  // Total valid transactions in the platform wallet (excluding the incorrect historical debits)
  const totalValidTransactions = transactions.filter(tx => !(tx.transaction_type === 'debit' && tx.reference_type === 'bounty_payment')).length;
  
  // Use actual wallet available_balance as the main balance (reflects payouts made)
  const currentBalance = balanceData?.available_balance || 0;
  const avgCommission = totalBountyTransactions > 0 ? trueTotalCommission / totalBountyTransactions : 0;
  // Count payout transactions (debits)
  const payoutCount = transactions.filter(tx => tx.transaction_type === 'debit' && tx.reference_type !== 'bounty_payment').length;

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Platform Wallet"
          subtitle="Real-time commission tracking and revenue analytics"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
          forceDark={true}
        >
          {/* Hero Balance Card - Dark Theme */}
          <div className="mb-6 relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] p-8 shadow-2xl">
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-[#94A3B8] text-sm font-medium mb-1">
                    Current Platform Balance
                  </p>
                  {balanceLoading ? (
                    <div className="h-12 w-64 bg-[#334155]/30 animate-pulse rounded-lg"></div>
                  ) : (
                    <h1 className="text-5xl font-bold text-[#F8FAFC] mb-2">
                      {currentBalance.toLocaleString()} <span className="text-3xl text-[#94A3B8]">{balanceData?.currency || 'ETB'}</span>
                    </h1>
                  )}
                  <p className="text-[#64748B] text-sm">
                    Total earned: <span className="text-[#10B981] font-semibold">{trueTotalCommission.toLocaleString()} ETB</span>
                    {payoutCount > 0 && <span className="ml-2">· {payoutCount} payout{payoutCount !== 1 ? 's' : ''} made</span>}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsConfigureMethodsOpen(true)}
                    className="px-5 py-3 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] font-semibold rounded-xl shadow-lg transition-all flex items-center gap-2 border border-[#475569]"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Configure Methods
                    {paymentMethods.length > 0 && (
                      <span className="ml-1 bg-[#3B82F6] text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">{paymentMethods.length}</span>
                    )}
                  </button>
                  <button
                    onClick={() => setIsPayoutModalOpen(true)}
                    className="px-6 py-3 bg-[#3B82F6] hover:bg-[#2563EB] text-white font-semibold rounded-xl shadow-lg transition-all flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Payout Commission
                  </button>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-[#334155]/30 backdrop-blur-sm rounded-xl p-4 border border-[#334155]">
                  <p className="text-[#94A3B8] text-xs mb-1">Available Balance</p>
                  <p className="text-[#F8FAFC] text-xl font-bold">{(balanceData?.available_balance || 0).toLocaleString()} ETB</p>
                </div>
                <div className="bg-[#334155]/30 backdrop-blur-sm rounded-xl p-4 border border-[#334155]">
                  <p className="text-[#94A3B8] text-xs mb-1">Avg Commission</p>
                  <p className="text-[#F8FAFC] text-xl font-bold">{avgCommission.toLocaleString(undefined, {maximumFractionDigits: 0})} ETB</p>
                </div>
                <div className="bg-[#334155]/30 backdrop-blur-sm rounded-xl p-4 border border-[#334155]">
                  <p className="text-[#94A3B8] text-xs mb-1">Commission Rate</p>
                  <p className="text-[#F8FAFC] text-xl font-bold">45%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            {/* Total Transactions */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-10 transition-all duration-300">
              <h3 className="text-[#94A3B8] text-sm mb-4">Total Transactions</h3>
              <p className="text-[#F8FAFC] text-3xl font-bold">{totalValidTransactions}</p>
            </div>

            {/* Commission Structure */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-10 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[#94A3B8] text-sm">Commission Model</h3>
                <span className="text-[#3B82F6] text-xs font-semibold">30% + 15%</span>
              </div>
              <p className="text-[#F8FAFC] text-lg font-semibold">Dual Structure</p>
              <p className="text-[#64748B] text-xs mt-1">Org 30% + Researcher 15%</p>
            </div>

            {/* Reserved Balance */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-xl p-10 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[#94A3B8] text-sm">Reserved Balance</h3>
                <span className="text-[#64748B] text-xs font-semibold">Locked</span>
              </div>
              <p className="text-[#F8FAFC] text-3xl font-bold">{(balanceData?.reserved_balance || 0).toLocaleString()}</p>
              <p className="text-[#64748B] text-xs mt-1">ETB</p>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="mb-5 flex gap-4">
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
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold text-[#F8FAFC]">
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
              <div className="bg-[#1E293B] border border-[#334155] rounded-xl overflow-hidden divide-y divide-[#334155]">
                {filteredTransactions.map((tx) => {
                  const isDebit = tx.transaction_type === 'debit';
                  return (
                    <div
                      key={tx.transaction_id || Math.random()}
                      className="p-6 hover:bg-[#334155]/20 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        {/* Left Section: Transaction Details */}
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDebit ? 'bg-orange-500/20' : 'bg-[#10B981]/20'}`}>
                              {isDebit ? (
                                <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9l-5 5-5-5" />
                                </svg>
                              ) : (
                                <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5 5 5" />
                                </svg>
                              )}
                            </div>
                            <h3 className="text-lg font-semibold text-[#F8FAFC]">
                              {isDebit ? 'Platform Payout' : 'Commission from Bounty Payment'}
                            </h3>
                            <span className={`px-2 py-1 rounded text-xs font-bold text-white uppercase ${isDebit ? 'bg-orange-500' : 'bg-[#10B981]'}`}>
                              {isDebit ? 'Payout' : 'Commission'}
                            </span>
                          </div>

                          <p className="text-[#94A3B8] mb-4 line-clamp-1">{tx.description || (isDebit ? 'Platform commission withdrawal' : 'Commission received')}</p>

                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-[#64748B] mb-1">Reference Type</p>
                              <p className="text-[#F8FAFC] font-medium capitalize">{tx.reference_type?.replace(/_/g, ' ') || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-[#64748B] mb-1">Transaction Date</p>
                              <p className="text-[#F8FAFC]">{new Date(tx.created_at).toLocaleDateString()}</p>
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
                              <span className="text-[#64748B] text-sm">{isDebit ? 'Payout Amount:' : 'Commission Amount:'}</span>
                              <span className={`font-bold text-lg ${isDebit ? 'text-orange-400' : 'text-[#10B981]'}`}>
                                {isDebit ? '-' : '+'}{tx.amount.toLocaleString()} ETB
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-[#64748B] text-sm">Balance Before:</span>
                              <span className="text-[#94A3B8] font-semibold">{tx.balance_before.toLocaleString()} ETB</span>
                            </div>
                            <div className="border-t border-[#334155] pt-2 flex justify-between items-center">
                              <span className="text-[#94A3B8] text-sm">Balance After:</span>
                              <span className="text-[#F8FAFC] font-bold text-lg">{tx.balance_after.toLocaleString()} ETB</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Payout Modal */}
          {isPayoutModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
              <div className="bg-[#1E293B] border border-[#334155] rounded-2xl p-8 max-w-md w-full shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
                <button 
                  onClick={() => setIsPayoutModalOpen(false)}
                  className="absolute top-4 right-4 text-[#64748B] hover:text-[#F8FAFC] transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                
                <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">Payout Platform Commission</h2>
                <p className="text-[#94A3B8] text-sm mb-6">Withdraw platform accumulated commission to a specific payment method.</p>
                
                {payoutError && (
                  <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {payoutError}
                  </div>
                )}
                
                <form onSubmit={handlePayoutSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-1">
                      Amount ({balanceData?.currency || 'ETB'})
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max={balanceData?.available_balance || 0}
                      value={payoutAmount}
                      onChange={(e) => setPayoutAmount(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                      placeholder="e.g. 50000"
                      required
                    />
                    <p className="text-xs text-[#64748B] mt-1">Available: {(balanceData?.available_balance || 0).toLocaleString()}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-1">
                      Saved Payment Method
                    </label>
                    <select
                      value={selectedMethodId}
                      onChange={(e) => setSelectedMethodId(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                      required
                    >
                      <option value="" disabled>Select a configured method</option>
                      {paymentMethods.map(method => (
                        <option key={method.id} value={method.id}>
                          {method.method_type.replace('_', ' ').toUpperCase()} - {method.account_name} ({method.account_number.slice(-4)})
                        </option>
                      ))}
                    </select>
                    {paymentMethods.length === 0 && (
                      <p className="text-xs text-amber-500 mt-2">
                        You need to configure a payment method first. Close this modal and add one above.
                      </p>
                    )}
                  </div>
                  
                  <div className="pt-4 flex gap-3">
                    <button
                      type="button"
                      onClick={() => setIsPayoutModalOpen(false)}
                      className="flex-1 px-4 py-2 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] font-medium rounded-lg transition-colors"
                      disabled={isWithdrawing}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-[#10B981] hover:bg-[#059669] text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                      disabled={isWithdrawing}
                    >
                      {isWithdrawing ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Processing...
                        </>
                      ) : (
                        'Confirm Payout'
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Configure Methods Modal */}
          {isConfigureMethodsOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
              <div className="bg-[#1E293B] border border-[#334155] rounded-2xl p-8 max-w-xl w-full shadow-2xl relative animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
                <button
                  onClick={() => { setIsConfigureMethodsOpen(false); setAddMethodOpen(false); setAddMethodError(''); }}
                  className="absolute top-4 right-4 text-[#64748B] hover:text-[#F8FAFC] transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <h2 className="text-2xl font-bold text-[#F8FAFC] mb-1">Payout Methods</h2>
                <p className="text-[#94A3B8] text-sm mb-6">Configure destinations for withdrawing platform commissions.</p>

                {/* Existing Methods */}
                {paymentMethods.length === 0 ? (
                  <div className="text-center py-8 mb-6 border border-dashed border-[#334155] rounded-xl">
                    <div className="w-12 h-12 bg-[#0F172A] rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                    </div>
                    <p className="text-[#64748B] text-sm">No payout methods configured yet.</p>
                  </div>
                ) : (
                  <div className="space-y-3 mb-6">
                    {paymentMethods.map((method: any) => (
                      <div key={method.id} className="flex items-center justify-between bg-[#0F172A] border border-[#334155] rounded-xl p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-[#1E293B] flex items-center justify-center text-[#3B82F6]">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                            </svg>
                          </div>
                          <div>
                            <p className="text-[#F8FAFC] text-sm font-semibold capitalize">{method.method_type.replace(/_/g, ' ')}</p>
                            <p className="text-[#94A3B8] text-xs">{method.account_name} {method.bank_name ? `· ${method.bank_name}` : ''} · ****{method.account_number.slice(-4)}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteMethod(method.id)}
                          className="text-[#64748B] hover:text-red-400 p-2 rounded-lg hover:bg-red-500/10 transition-all"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add Method Toggle */}
                {!addMethodOpen ? (
                  <button
                    onClick={() => setAddMethodOpen(true)}
                    className="w-full py-3 border border-dashed border-[#3B82F6] text-[#3B82F6] rounded-xl font-medium text-sm hover:bg-[#3B82F6]/10 transition-all flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add New Payment Method
                  </button>
                ) : (
                  <div className="bg-[#0F172A] border border-[#334155] rounded-xl p-5 space-y-4">
                    <h3 className="text-[#F8FAFC] font-semibold text-sm">New Payout Method</h3>

                    {addMethodError && (
                      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                        {addMethodError}
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">Method Type</label>
                        <select
                          value={addMethodForm.method_type}
                          onChange={(e) => setAddMethodForm({ ...addMethodForm, method_type: e.target.value })}
                          className="w-full px-3 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                        >
                          <option value="bank_transfer">Bank Transfer</option>
                          <option value="telebirr">Telebirr</option>
                          <option value="cbe_birr">CBE Birr</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">Account Name</label>
                        <input
                          type="text"
                          placeholder="e.g., Platform Operations"
                          value={addMethodForm.account_name}
                          onChange={(e) => setAddMethodForm({ ...addMethodForm, account_name: e.target.value })}
                          className="w-full px-3 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] text-sm focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                        />
                      </div>
                      {addMethodForm.method_type === 'bank_transfer' && (
                        <div>
                          <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">Bank Name</label>
                          <input
                            type="text"
                            placeholder="e.g., CBE"
                            value={addMethodForm.bank_name}
                            onChange={(e) => setAddMethodForm({ ...addMethodForm, bank_name: e.target.value })}
                            className="w-full px-3 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] text-sm focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                          />
                        </div>
                      )}
                      <div>
                        <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">Account Number / Phone</label>
                        <input
                          type="text"
                          placeholder="Account or phone number"
                          value={addMethodForm.account_number}
                          onChange={(e) => setAddMethodForm({ ...addMethodForm, account_number: e.target.value })}
                          className="w-full px-3 py-2 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder:text-[#475569] text-sm focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                        />
                      </div>
                    </div>

                    <div className="flex gap-3 pt-1">
                      <button
                        onClick={() => { setAddMethodOpen(false); setAddMethodError(''); }}
                        className="flex-1 py-2 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleAddMethod}
                        className="flex-1 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-sm font-semibold rounded-lg transition-colors"
                      >
                        Save Method
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
