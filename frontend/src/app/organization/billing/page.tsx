'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';

interface Subscription {
  subscription_id: string;
  tier: string;
  status: string;
  subscription_fee: number;
  currency: string;
  billing_cycle_months: number;
  payments_per_year: number;
  current_period_start: string;
  current_period_end: string;
  next_billing_date: string;
  is_trial: boolean;
  trial_end_date: string | null;
}

interface Payment {
  payment_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
  payment_date: string;
  invoice_number: string;
  description: string;
}

interface WalletBalance {
  balance: number;
  reserved_balance: number;
  available_balance: number;
  currency: string;
}

export default function OrganizationBillingPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const [selectedTab, setSelectedTab] = useState<'subscription' | 'payments' | 'wallet'>('subscription');
  const [showRechargeModal, setShowRechargeModal] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
    setIsMounted(true);
  }, []);

  // Recharge wallet mutation
  const rechargeMutation = useApiMutation({
    method: 'POST',
    onSuccess: (data) => {
      alert(`Wallet recharged successfully! New balance: ${data.new_balance} ETB`);
      setShowRechargeModal(false);
      setRechargeAmount('');
      setPaymentMethod('bank_transfer');
      // Refetch wallet balance
      window.location.reload();
    },
    onError: (error) => {
      alert(`Failed to recharge wallet: ${error.message}`);
    },
  });

  // Fetch subscription data - only on client side
  const { data: subscriptionData, isLoading: subscriptionLoading, isError: subscriptionError, refetch: refetchSubscription } = useApiQuery<Subscription>({
    endpoint: isMounted ? '/subscriptions/current' : undefined,
    enabled: isMounted && selectedTab === 'subscription',
    retry: 0, // Don't retry on 404
  });

  // Fetch payment history - only if we have a subscription
  const { data: paymentsData, isLoading: paymentsLoading, refetch: refetchPayments } = useApiQuery<Payment[]>({
    endpoint: isMounted && subscriptionData ? `/subscriptions/${subscriptionData.subscription_id}/payments?limit=50` : undefined,
    enabled: isMounted && !!subscriptionData && selectedTab === 'payments',
  });

  // Fetch wallet balance - only on client side
  const { data: walletData, isLoading: walletLoading } = useApiQuery<WalletBalance>({
    endpoint: isMounted ? '/wallet/balance' : undefined,
    enabled: isMounted,
  });

  const handleRechargeWallet = async () => {
    const amount = parseFloat(rechargeAmount);
    
    if (!amount || amount < 1000) {
      alert('Minimum recharge amount is 1,000 ETB');
      return;
    }

    await rechargeMutation.mutate({
      endpoint: `/wallet/recharge?amount=${amount}&payment_method=${paymentMethod}`,
    });
  };

  const handleViewTransactions = () => {
    // Navigate to transactions page or show transactions modal
    window.location.href = '/organization/wallet/transactions';
  };

  const subscription = subscriptionData;
  const payments = paymentsData || [];

  const getTierBadgeColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'enterprise':
        return 'bg-gradient-to-r from-purple-500 to-pink-500';
      case 'professional':
      case 'pro':
        return 'bg-gradient-to-r from-blue-500 to-cyan-500';
      case 'basic':
        return 'bg-gradient-to-r from-green-500 to-emerald-500';
      default:
        return 'bg-gradient-to-r from-gray-500 to-slate-500';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-[#10B981] text-white';
      case 'pending':
        return 'bg-[#F59E0B] text-white';
      case 'cancelled':
      case 'expired':
        return 'bg-[#EF4444] text-white';
      default:
        return 'bg-[#64748B] text-white';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Billing & Subscription"
          subtitle="Manage your subscription, payments, and wallet"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Tabs - Centered */}
          <div className="mb-8 flex justify-center gap-2 border-b border-[#334155]">
            <button
              onClick={() => setSelectedTab('subscription')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'subscription'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Subscription
            </button>
            <button
              onClick={() => setSelectedTab('payments')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'payments'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Payment History
            </button>
            <button
              onClick={() => setSelectedTab('wallet')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'wallet'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Wallet
            </button>
          </div>

          {/* Subscription Tab */}
          {selectedTab === 'subscription' && (
            <div className="space-y-6">
              {!isMounted || subscriptionLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading subscription...</p>
                </div>
              ) : subscriptionError || (!subscriptionLoading && !subscription) ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Active Subscription</h3>
                  <p className="text-[#94A3B8] mb-2">You do not have an active subscription</p>
                  <p className="text-[#64748B] text-sm mb-6">Choose a plan to get started with our platform</p>
                  <button 
                    onClick={() => router.push('/organization/billing/manage-plan')}
                    className="px-6 py-3 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors"
                  >
                    View Plans
                  </button>
                </div>
              ) : subscription ? (
                <>
                  {/* Current Plan Card */}
                  <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-8">
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h2 className="text-2xl font-bold text-[#F8FAFC]">Current Plan</h2>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getTierBadgeColor(subscription.tier)} text-white`}>
                            {subscription.tier}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getStatusBadgeColor(subscription.status)}`}>
                            {subscription.status}
                          </span>
                        </div>
                        {subscription.is_trial && subscription.trial_end_date && (
                          <p className="text-[#F59E0B] text-sm">
                            Trial ends on {new Date(subscription.trial_end_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-3xl font-bold text-[#F8FAFC]">
                          {subscription.subscription_fee.toLocaleString()} {subscription.currency}
                        </p>
                        <p className="text-[#94A3B8] text-sm">
                          per {subscription.billing_cycle_months} month{subscription.billing_cycle_months > 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-6">
                      <div className="bg-[#334155]/30 rounded-lg p-4">
                        <p className="text-[#94A3B8] text-sm mb-1">Billing Cycle</p>
                        <p className="text-[#F8FAFC] font-semibold">
                          Every {subscription.billing_cycle_months} month{subscription.billing_cycle_months > 1 ? 's' : ''}
                        </p>
                      </div>
                      <div className="bg-[#334155]/30 rounded-lg p-4">
                        <p className="text-[#94A3B8] text-sm mb-1">Payments Per Year</p>
                        <p className="text-[#F8FAFC] font-semibold">{subscription.payments_per_year}</p>
                      </div>
                      <div className="bg-[#334155]/30 rounded-lg p-4">
                        <p className="text-[#94A3B8] text-sm mb-1">Next Billing Date</p>
                        <p className="text-[#F8FAFC] font-semibold">
                          {new Date(subscription.next_billing_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-[#334155]">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-[#94A3B8] text-sm">Current Period</p>
                          <p className="text-[#F8FAFC] font-medium">
                            {new Date(subscription.current_period_start).toLocaleDateString()} - {new Date(subscription.current_period_end).toLocaleDateString()}
                          </p>
                        </div>
                        <button 
                          onClick={() => router.push('/organization/billing/manage-plan')}
                          className="px-6 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors"
                        >
                          Manage Plan
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          )}

          {/* Payment History Tab */}
          {selectedTab === 'payments' && (
            <div>
              {!isMounted || paymentsLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading payments...</p>
                </div>
              ) : payments.length > 0 ? (
                <div className="space-y-3">
                  {payments.map((payment) => (
                    <div key={payment.payment_id} className="bg-[#1E293B] rounded-lg p-5 hover:bg-[#1E293B]/80 transition-all shadow-sm">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-semibold text-[#F8FAFC]">{payment.description || 'Subscription Payment'}</h3>
                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getStatusBadgeColor(payment.status)}`}>
                              {payment.status}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-[#94A3B8]">
                            <span>Invoice: {payment.invoice_number}</span>
                            <span>•</span>
                            <span>{payment.payment_method}</span>
                            <span>•</span>
                            <span>{new Date(payment.payment_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-[#F8FAFC]">
                            {payment.amount.toLocaleString()} {payment.currency}
                          </p>
                          <button className="text-[#3B82F6] hover:text-[#2563EB] text-sm font-medium mt-1">
                            Download Invoice
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Payment History</h3>
                  <p className="text-[#94A3B8]">Your payment history will appear here</p>
                </div>
              )}
            </div>
          )}

          {/* Wallet Tab */}
          {selectedTab === 'wallet' && (
            <div className="space-y-6">
              {!isMounted || walletLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading wallet...</p>
                </div>
              ) : walletData ? (
                <>
                  {/* Wallet Balance Card */}
                  <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-8">
                    <h2 className="text-xl font-bold text-[#F8FAFC] mb-6">Wallet Balance</h2>
                    <div className="grid grid-cols-3 gap-6">
                      <div className="bg-[#334155]/30 rounded-lg p-6">
                        <p className="text-[#94A3B8] text-sm mb-2">Total Balance</p>
                        <p className="text-3xl font-bold text-[#F8FAFC]">
                          {walletData.balance.toLocaleString()} {walletData.currency}
                        </p>
                      </div>
                      <div className="bg-[#334155]/30 rounded-lg p-6">
                        <p className="text-[#94A3B8] text-sm mb-2">Available Balance</p>
                        <p className="text-3xl font-bold text-[#10B981]">
                          {walletData.available_balance.toLocaleString()} {walletData.currency}
                        </p>
                      </div>
                      <div className="bg-[#334155]/30 rounded-lg p-6">
                        <p className="text-[#94A3B8] text-sm mb-2">Reserved Balance</p>
                        <p className="text-3xl font-bold text-[#F59E0B]">
                          {walletData.reserved_balance.toLocaleString()} {walletData.currency}
                        </p>
                      </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-[#334155] flex gap-4">
                      <button 
                        onClick={() => setShowRechargeModal(true)}
                        className="flex-1 px-6 py-3 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors"
                      >
                        Recharge Wallet
                      </button>
                      <button 
                        onClick={handleViewTransactions}
                        className="flex-1 px-6 py-3 bg-[#334155] hover:bg-[#475569] text-white rounded-lg font-medium transition-colors"
                      >
                        View Transactions
                      </button>
                    </div>
                  </div>

                  {/* Wallet Info */}
                  <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-6">
                    <h3 className="text-lg font-bold text-[#F8FAFC] mb-4">About Your Wallet</h3>
                    <div className="space-y-3 text-[#94A3B8]">
                      <p>• Use your wallet balance to fund bug bounty programs</p>
                      <p>• Reserved balance is allocated to active bounty programs</p>
                      <p>• Recharge your wallet using bank transfer, TeleBirr, or CBE Birr</p>
                      <p>• Minimum recharge amount: 1,000 {walletData.currency}</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <p className="text-[#94A3B8]">Unable to load wallet information</p>
                </div>
              )}
            </div>
          )}

          {/* Recharge Wallet Modal */}
          {showRechargeModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 max-w-md w-full mx-4">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">Recharge Wallet</h2>
                  <button
                    onClick={() => setShowRechargeModal(false)}
                    className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Amount Input */}
                  <div>
                    <label className="block text-[#F8FAFC] font-medium mb-2">
                      Amount (ETB)
                    </label>
                    <input
                      type="number"
                      value={rechargeAmount}
                      onChange={(e) => setRechargeAmount(e.target.value)}
                      placeholder="Enter amount (min. 1,000 ETB)"
                      className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6]"
                      min="1000"
                      step="100"
                    />
                    <p className="text-[#94A3B8] text-sm mt-2">Minimum recharge: 1,000 ETB</p>
                  </div>

                  {/* Payment Method */}
                  <div>
                    <label className="block text-[#F8FAFC] font-medium mb-2">
                      Payment Method
                    </label>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
                    >
                      <option value="bank_transfer">Bank Transfer</option>
                      <option value="telebirr">TeleBirr</option>
                      <option value="cbe_birr">CBE Birr</option>
                    </select>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-4">
                    <button
                      onClick={() => setShowRechargeModal(false)}
                      className="flex-1 px-6 py-3 bg-[#334155] hover:bg-[#475569] text-white rounded-lg font-medium transition-colors"
                      disabled={rechargeMutation.isLoading}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleRechargeWallet}
                      disabled={rechargeMutation.isLoading}
                      className="flex-1 px-6 py-3 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {rechargeMutation.isLoading ? 'Processing...' : 'Recharge'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
