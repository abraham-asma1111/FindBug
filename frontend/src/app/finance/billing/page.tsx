'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';

interface PendingPayment {
  payment_id: string;
  subscription_id: string;
  organization_id: string;
  organization_name: string;
  amount: number;
  currency: string;
  tier: string;
  due_date: string;
  invoice_number: string;
  period_start: string;
  period_end: string;
}

export default function FinanceBillingPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedTab, setSelectedTab] = useState<'pending' | 'overdue' | 'revenue'>('pending');
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<PendingPayment | null>(null);
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [transactionId, setTransactionId] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch pending payments
  const { data: pendingPayments, refetch: refetchPending, isLoading: pendingLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/pending-payments',
    enabled: selectedTab === 'pending',
  });

  // Fetch overdue subscriptions
  const { data: overdueData, refetch: refetchOverdue, isLoading: overdueLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/overdue',
    enabled: selectedTab === 'overdue',
  });

  // Fetch revenue report
  const { data: revenueData, refetch: refetchRevenue, isLoading: revenueLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/revenue-report',
    enabled: selectedTab === 'revenue',
  });

  // Mark payment as paid mutation
  const verifyPaymentMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      alert('Payment verified successfully!');
      setShowVerifyModal(false);
      setSelectedPayment(null);
      setPaymentMethod('bank_transfer');
      setTransactionId('');
      // CRITICAL FIX: Refetch all tabs to update UI immediately
      refetchPending();
      refetchOverdue();
      refetchRevenue();
    },
    onError: (error) => {
      alert(`Failed to verify payment: ${error.message}`);
    },
  });

  const handleVerifyPayment = async () => {
    if (!selectedPayment) return;

    if (!transactionId.trim()) {
      alert('Please enter a transaction ID');
      return;
    }

    await verifyPaymentMutation.mutate({
      endpoint: `/subscriptions/payments/${selectedPayment.payment_id}/mark-paid`,
      payment_method: paymentMethod,
      gateway_transaction_id: transactionId,
    });
  };

  const pending = pendingPayments?.payments || [];
  const overdue = overdueData || [];
  const revenue = revenueData || null;

  const getTierBadgeColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'enterprise':
        return 'bg-gradient-to-r from-purple-500 to-pink-500';
      case 'professional':
        return 'bg-gradient-to-r from-blue-500 to-cyan-500';
      case 'basic':
        return 'bg-gradient-to-r from-green-500 to-emerald-500';
      default:
        return 'bg-gradient-to-r from-gray-500 to-slate-500';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Subscription Management"
          subtitle="Manage organization subscriptions and payments"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Tabs - Centered */}
          <div className="mb-8 flex justify-center gap-2 border-b border-[#334155]">
            <button
              onClick={() => setSelectedTab('pending')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'pending'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Pending Payments
              {pending.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-[#F59E0B] text-white text-xs rounded-full">
                  {pending.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setSelectedTab('overdue')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'overdue'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Overdue
              {overdue.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-[#EF4444] text-white text-xs rounded-full">
                  {overdue.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setSelectedTab('revenue')}
              className={`px-6 py-3 font-medium transition-all ${
                selectedTab === 'revenue'
                  ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Revenue Report
            </button>
          </div>

          {/* Pending Payments Tab */}
          {selectedTab === 'pending' && (
            <div>
              {pendingLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading pending payments...</p>
                </div>
              ) : pending.length > 0 ? (
                <div className="space-y-4">
                  {pending.map((payment: PendingPayment) => (
                    <div key={payment.payment_id} className="bg-[#1E293B] rounded-xl border border-[#334155] p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-[#F8FAFC]">
                              {payment.organization_name}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(payment.tier)}`}>
                              {payment.tier}
                            </span>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-[#94A3B8]">Invoice Number</p>
                              <p className="text-[#F8FAFC] font-medium">{payment.invoice_number}</p>
                            </div>
                            <div>
                              <p className="text-[#94A3B8]">Due Date</p>
                              <p className="text-[#F8FAFC] font-medium">
                                {new Date(payment.due_date).toLocaleDateString()}
                              </p>
                            </div>
                            <div>
                              <p className="text-[#94A3B8]">Billing Period</p>
                              <p className="text-[#F8FAFC] font-medium">
                                {new Date(payment.period_start).toLocaleDateString()} - {new Date(payment.period_end).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="text-right ml-6">
                          <p className="text-3xl font-bold text-[#F8FAFC] mb-2">
                            {payment.amount.toLocaleString()} {payment.currency}
                          </p>
                          <button
                            onClick={() => {
                              setSelectedPayment(payment);
                              setShowVerifyModal(true);
                            }}
                            className="px-6 py-2 bg-[#10B981] hover:bg-[#059669] text-white rounded-lg font-medium transition-colors"
                          >
                            Verify Payment
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">All Caught Up!</h3>
                  <p className="text-[#94A3B8]">No pending payments to verify</p>
                </div>
              )}
            </div>
          )}

          {/* Overdue Tab */}
          {selectedTab === 'overdue' && (
            <div>
              {overdueLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading overdue subscriptions...</p>
                </div>
              ) : overdue.length > 0 ? (
                <div className="space-y-4">
                  {overdue.map((item: any) => (
                    <div key={item.subscription_id} className="bg-[#1E293B] rounded-xl border border-[#EF4444]/30 p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-[#F8FAFC] mb-2">
                            Organization ID: {item.organization_id}
                          </h3>
                          <div className="flex items-center gap-4 text-sm">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(item.tier)}`}>
                              {item.tier}
                            </span>
                            <span className="text-[#94A3B8]">
                              Due: {new Date(item.due_date).toLocaleDateString()}
                            </span>
                            <span className="text-[#EF4444] font-semibold">
                              {item.days_overdue} days overdue
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-[#EF4444]">
                            {item.amount.toLocaleString()} ETB
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Overdue Payments</h3>
                  <p className="text-[#94A3B8]">All subscriptions are up to date</p>
                </div>
              )}
            </div>
          )}

          {/* Revenue Report Tab */}
          {selectedTab === 'revenue' && (
            <div>
              {revenueLoading ? (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading revenue report...</p>
                </div>
              ) : revenue ? (
                <div className="space-y-6">
                  {/* Summary Cards */}
                  <div className="grid grid-cols-3 gap-6">
                    <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
                      <p className="text-[#94A3B8] text-sm mb-2">Total Revenue</p>
                      <p className="text-3xl font-bold text-[#10B981]">
                        {revenue.total_revenue.toLocaleString()} ETB
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
                      <p className="text-[#94A3B8] text-sm mb-2">Total Payments</p>
                      <p className="text-3xl font-bold text-[#3B82F6]">
                        {revenue.payment_count}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
                      <p className="text-[#94A3B8] text-sm mb-2">Average Payment</p>
                      <p className="text-3xl font-bold text-[#F8FAFC]">
                        {revenue.average_payment.toLocaleString()} ETB
                      </p>
                    </div>
                  </div>

                  {/* Revenue by Tier */}
                  <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-6">
                    <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Revenue by Tier</h3>
                    <div className="space-y-4">
                      {Object.entries(revenue.by_tier || {}).map(([tier, data]: [string, any]) => (
                        <div key={tier} className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(tier)}`}>
                                {tier}
                              </span>
                              <span className="text-[#94A3B8]">{data.count} payments</span>
                            </div>
                            <div className="text-right">
                              <p className="text-xl font-bold text-[#F8FAFC]">
                                {data.revenue.toLocaleString()} ETB
                              </p>
                              <p className="text-sm text-[#94A3B8]">
                                Avg: {data.average.toLocaleString()} ETB
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 text-center">
                  <p className="text-[#94A3B8]">No revenue data available</p>
                </div>
              )}
            </div>
          )}

          {/* Verify Payment Modal */}
          {showVerifyModal && selectedPayment && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 max-w-md w-full mx-4">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">Verify Payment</h2>
                  <button
                    onClick={() => {
                      setShowVerifyModal(false);
                      setSelectedPayment(null);
                    }}
                    className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Payment Details */}
                  <div className="bg-[#334155]/30 rounded-lg p-4">
                    <p className="text-[#94A3B8] text-sm mb-1">Organization</p>
                    <p className="text-[#F8FAFC] font-semibold mb-3">{selectedPayment.organization_name}</p>
                    
                    <p className="text-[#94A3B8] text-sm mb-1">Amount</p>
                    <p className="text-[#3B82F6] font-bold text-2xl mb-3">
                      {selectedPayment.amount.toLocaleString()} {selectedPayment.currency}
                    </p>

                    <p className="text-[#94A3B8] text-sm mb-1">Invoice Number</p>
                    <p className="text-[#F8FAFC] font-medium">{selectedPayment.invoice_number}</p>
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
                      <option value="cash">Cash</option>
                    </select>
                  </div>

                  {/* Transaction ID */}
                  <div>
                    <label className="block text-[#F8FAFC] font-medium mb-2">
                      Transaction ID / Reference Number
                    </label>
                    <input
                      type="text"
                      value={transactionId}
                      onChange={(e) => setTransactionId(e.target.value)}
                      placeholder="Enter transaction reference"
                      className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6]"
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-4">
                    <button
                      onClick={() => {
                        setShowVerifyModal(false);
                        setSelectedPayment(null);
                      }}
                      className="flex-1 px-6 py-3 bg-[#334155] hover:bg-[#475569] text-white rounded-lg font-medium transition-colors"
                      disabled={verifyPaymentMutation.isLoading}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleVerifyPayment}
                      disabled={verifyPaymentMutation.isLoading}
                      className="flex-1 px-6 py-3 bg-[#10B981] hover:bg-[#059669] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {verifyPaymentMutation.isLoading ? 'Verifying...' : 'Verify & Activate'}
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
