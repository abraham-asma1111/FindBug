'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';

interface Subscription {
  subscription_id: string;
  organization_id: string;
  organization_name: string;
  tier: string;
  status: string;
  subscription_fee: number;
  currency: string;
  start_date: string;
  next_billing_date: string;
  is_trial: boolean;
  trial_end_date: string | null;
  created_at: string;
}

interface SubscriptionDetails {
  subscription: any;
  organization: any;
  payment_history: any[];
  stats: any;
}

export default function FinanceBillingPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedTab, setSelectedTab] = useState<'pending' | 'overdue' | 'revenue' | 'subscriptions'>('pending');
  const [selectedTier, setSelectedTier] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<Subscription | null>(null);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<any>(null);
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [transactionId, setTransactionId] = useState('');
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionType, setActionType] = useState<'suspend' | 'resume' | 'cancel' | 'reminder' | null>(null);
  const [actionSubscription, setActionSubscription] = useState<Subscription | null>(null);
  const [actionReason, setActionReason] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Build query params for subscriptions tab
  const queryParams = new URLSearchParams();
  if (selectedTier) queryParams.append('tier', selectedTier);
  if (selectedStatus) queryParams.append('status', selectedStatus);
  if (searchQuery) queryParams.append('search', searchQuery);

  // Fetch subscriptions (for subscriptions tab)
  const { data: subscriptionsData, isLoading: subscriptionsLoading, refetch: refetchSubscriptions } = useApiQuery<any>({
    endpoint: `/subscriptions/all?${queryParams.toString()}`,
    enabled: selectedTab === 'subscriptions',
  });

  // Fetch pending payments (for pending tab)
  const { data: pendingPayments, refetch: refetchPending, isLoading: pendingLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/pending-payments',
    enabled: selectedTab === 'pending',
  });

  // Fetch overdue subscriptions (for overdue tab)
  const { data: overdueData, refetch: refetchOverdue, isLoading: overdueLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/overdue',
    enabled: selectedTab === 'overdue',
  });

  // Fetch revenue report (for revenue tab)
  const { data: revenueData, refetch: refetchRevenue, isLoading: revenueLoading } = useApiQuery<any>({
    endpoint: '/subscriptions/revenue-report',
    enabled: selectedTab === 'revenue',
  });

  // Fetch subscription details when modal opens
  const { data: detailsData, isLoading: detailsLoading } = useApiQuery<SubscriptionDetails>({
    endpoint: selectedSubscription ? `/subscriptions/${selectedSubscription.subscription_id}/details` : undefined,
    enabled: !!selectedSubscription,
  });

  const subscriptions = subscriptionsData?.subscriptions || [];
  const total = subscriptionsData?.total || 0;
  const pending = pendingPayments?.payments || [];
  const overdue = overdueData || [];
  const revenue = revenueData || null;

  // Convert by_tier object to array for rendering
  const revenueByTierArray = revenue?.by_tier 
    ? Object.entries(revenue.by_tier).map(([tier, data]: [string, any]) => ({
        tier,
        count: data.count,
        revenue: data.revenue,
        average: data.average
      }))
    : [];

  // Mark payment as paid mutation
  const verifyPaymentMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      alert('Payment verified successfully!');
      setShowVerifyModal(false);
      setSelectedPayment(null);
      setPaymentMethod('bank_transfer');
      setTransactionId('');
      // Refetch all tabs
      refetchPending();
      refetchOverdue();
      refetchRevenue();
      refetchSubscriptions();
    },
    onError: (error) => {
      alert(`Failed to verify payment: ${error.message}`);
    },
  });

  // Subscription action mutation
  const subscriptionActionMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      const actionMessages = {
        suspend: 'Subscription suspended successfully!',
        resume: 'Subscription resumed successfully!',
        cancel: 'Subscription cancelled successfully!',
        reminder: 'Payment reminder sent successfully!',
      };
      alert(actionMessages[actionType!]);
      setShowActionModal(false);
      setActionType(null);
      setActionSubscription(null);
      setActionReason('');
      // Refetch data
      refetchSubscriptions();
      refetchOverdue();
    },
    onError: (error) => {
      alert(`Failed to ${actionType} subscription: ${error.message}`);
    },
  });

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

  const getStatusBadgeColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-[#10B981] text-white';
      case 'pending':
        return 'bg-[#F59E0B] text-white';
      case 'suspended':
        return 'bg-[#EF4444] text-white';
      case 'cancelled':
        return 'bg-[#6B7280] text-white';
      default:
        return 'bg-[#64748B] text-white';
    }
  };

  const handleViewDetails = (subscription: Subscription) => {
    setSelectedSubscription(subscription);
    setShowDetailsModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailsModal(false);
    setSelectedSubscription(null);
  };

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

  const handleSubscriptionAction = (subscription: Subscription, action: 'suspend' | 'resume' | 'cancel' | 'reminder') => {
    setActionSubscription(subscription);
    setActionType(action);
    setShowActionModal(true);
  };

  const confirmSubscriptionAction = async () => {
    if (!actionSubscription || !actionType) return;

    const endpoints = {
      suspend: `/subscriptions/${actionSubscription.subscription_id}/suspend`,
      resume: `/subscriptions/${actionSubscription.subscription_id}/resume`,
      cancel: `/subscriptions/${actionSubscription.subscription_id}/cancel`,
      reminder: `/subscriptions/${actionSubscription.subscription_id}/send-reminder`,
    };

    await subscriptionActionMutation.mutate({
      endpoint: endpoints[actionType],
      reason: actionReason || undefined,
    });
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Invoices & Billing"
          subtitle="Manage subscription payments, invoices, and billing"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Tabs */}
          <div className="mb-4 flex justify-center gap-1 border-b border-[#334155]">
            <button
              onClick={() => setSelectedTab('pending')}
              className={`px-6 py-3 font-medium transition-all relative ${
                selectedTab === 'pending'
                  ? 'text-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Pending Payments
              {pending.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-[#F59E0B] text-white text-xs rounded-full">
                  {pending.length}
                </span>
              )}
              {selectedTab === 'pending' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3B82F6]"></div>
              )}
            </button>
            <button
              onClick={() => setSelectedTab('subscriptions')}
              className={`px-6 py-3 font-medium transition-all relative ${
                selectedTab === 'subscriptions'
                  ? 'text-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              All Subscriptions
              {selectedTab === 'subscriptions' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3B82F6]"></div>
              )}
            </button>
            <button
              onClick={() => setSelectedTab('overdue')}
              className={`px-6 py-3 font-medium transition-all relative ${
                selectedTab === 'overdue'
                  ? 'text-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Overdue
              {overdue.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-[#EF4444] text-white text-xs rounded-full">
                  {overdue.length}
                </span>
              )}
              {selectedTab === 'overdue' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3B82F6]"></div>
              )}
            </button>
            <button
              onClick={() => setSelectedTab('revenue')}
              className={`px-6 py-3 font-medium transition-all relative ${
                selectedTab === 'revenue'
                  ? 'text-[#3B82F6]'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Revenue Report
              {selectedTab === 'revenue' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3B82F6]"></div>
              )}
            </button>
          </div>

          {/* Pending Payments Tab */}
          {selectedTab === 'pending' && (
            <div>
              {pendingLoading ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading pending payments...</p>
                </div>
              ) : pending.length > 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
                  {pending.map((payment: any, index: number) => (
                    <div key={payment.payment_id}>
                      {/* Payment Header */}
                      <div className="mb-6">
                        <div className="flex items-center justify-between mb-6 pb-3 border-b border-[#334155]">
                          <div className="flex items-center gap-3">
                            <h2 className="text-xl font-semibold text-[#F8FAFC]">
                              {payment.organization_name}
                            </h2>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(payment.tier)}`}>
                              {payment.tier}
                            </span>
                          </div>
                          <button
                            onClick={() => {
                              setSelectedPayment(payment);
                              setShowVerifyModal(true);
                            }}
                            className="px-6 py-2 bg-[#10B981] hover:bg-[#059669] text-white rounded-lg font-semibold transition-colors"
                          >
                            Verify Payment
                          </button>
                        </div>

                        {/* Payment Details */}
                        <div className="space-y-4">
                          <div className="flex justify-between items-center gap-4">
                            <span className="text-[#94A3B8] flex-shrink-0">Invoice Number</span>
                            <span className="text-[#F8FAFC] font-medium text-right">{payment.invoice_number}</span>
                          </div>
                          <div className="flex justify-between items-center gap-4">
                            <span className="text-[#94A3B8] flex-shrink-0">Amount</span>
                            <span className="text-[#F8FAFC] font-medium text-right text-xl">
                              {payment.amount.toLocaleString()} {payment.currency}
                            </span>
                          </div>
                          <div className="flex justify-between items-center gap-4">
                            <span className="text-[#94A3B8] flex-shrink-0">Due Date</span>
                            <span className="text-[#F8FAFC] font-medium text-right">
                              {new Date(payment.due_date).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </span>
                          </div>
                          <div className="flex justify-between items-center gap-4">
                            <span className="text-[#94A3B8] flex-shrink-0">Billing Period</span>
                            <span className="text-[#F8FAFC] font-medium text-right">
                              {new Date(payment.period_start).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })} - {new Date(payment.period_end).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Separator between payments */}
                      {index < pending.length - 1 && (
                        <div className="my-8 border-t-2 border-[#334155]"></div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
                  <div className="bg-[#10B981]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
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

          {/* All Subscriptions Tab */}
          {selectedTab === 'subscriptions' && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
          {/* Filters */}
          <div className="mb-6 pb-6 border-b border-[#334155]">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              {/* Search */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Search Organization
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by company name..."
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6]"
                />
              </div>

              {/* Tier Filter */}
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Tier
                </label>
                <select
                  value={selectedTier}
                  onChange={(e) => setSelectedTier(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
                >
                  <option value="">All Tiers</option>
                  <option value="BASIC">Basic</option>
                  <option value="PROFESSIONAL">Professional</option>
                  <option value="ENTERPRISE">Enterprise</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Status
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
                >
                  <option value="">All Status</option>
                  <option value="ACTIVE">Active</option>
                  <option value="PENDING">Pending</option>
                  <option value="SUSPENDED">Suspended</option>
                  <option value="CANCELLED">Cancelled</option>
                </select>
              </div>
            </div>

            {/* Clear Filters */}
            {(selectedTier || selectedStatus || searchQuery) && (
              <div className="mt-4">
                <button
                  onClick={() => {
                    setSelectedTier('');
                    setSelectedStatus('');
                    setSearchQuery('');
                  }}
                  className="text-[#3B82F6] hover:text-[#2563EB] text-sm font-medium"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>

          {/* Stats Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 pb-6 border-b border-[#334155]">
            <div className="bg-[#0F172A] border border-[#334155] p-4 rounded-lg">
              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Total Subscriptions</p>
              <p className="text-2xl font-bold text-[#F8FAFC]">{total}</p>
            </div>
            <div className="bg-[#0F172A] border border-[#334155] p-4 rounded-lg">
              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Active</p>
              <p className="text-2xl font-bold text-[#10B981]">
                {subscriptions.filter((s: Subscription) => s.status?.toUpperCase() === 'ACTIVE').length}
              </p>
            </div>
            <div className="bg-[#0F172A] border border-[#334155] p-4 rounded-lg">
              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Pending</p>
              <p className="text-2xl font-bold text-[#F59E0B]">
                {subscriptions.filter((s: Subscription) => s.status?.toUpperCase() === 'PENDING').length}
              </p>
            </div>
            <div className="bg-[#0F172A] border border-[#334155] p-4 rounded-lg">
              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Suspended</p>
              <p className="text-2xl font-bold text-[#EF4444]">
                {subscriptions.filter((s: Subscription) => s.status?.toUpperCase() === 'SUSPENDED').length}
              </p>
            </div>
          </div>

          {/* Subscriptions List */}
          {subscriptionsLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
              <p className="text-[#94A3B8] mt-4">Loading subscriptions...</p>
            </div>
          ) : subscriptions.length > 0 ? (
            <div className="space-y-0">
              {subscriptions.map((subscription: Subscription, index: number) => (
                <div key={subscription.subscription_id}>
                  <div className="pb-6 mb-6 border-b border-[#334155] last:border-b-0 last:pb-0 last:mb-0">
                    <div
                      onClick={() => handleViewDetails(subscription)}
                      className="cursor-pointer hover:opacity-80 transition-opacity"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-4">
                            <h3 className="text-xl font-bold text-[#F8FAFC]">
                              {subscription.organization_name}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(subscription.tier)}`}>
                              {subscription.tier}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getStatusBadgeColor(subscription.status)}`}>
                              {subscription.status}
                            </span>
                            {subscription.is_trial && (
                              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-[#8B5CF6] text-white">
                                TRIAL
                              </span>
                            )}
                          </div>

                          <div className="grid grid-cols-4 gap-6 text-sm">
                            <div>
                              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Subscription Fee</p>
                              <p className="text-[#F8FAFC] font-semibold">
                                {subscription.subscription_fee.toLocaleString()} {subscription.currency}
                              </p>
                            </div>
                            <div>
                              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Start Date</p>
                              <p className="text-[#F8FAFC] font-semibold">
                                {new Date(subscription.start_date).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </p>
                            </div>
                            <div>
                              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Next Billing</p>
                              <p className="text-[#F8FAFC] font-semibold">
                                {new Date(subscription.next_billing_date).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </p>
                            </div>
                            <div>
                              <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Created</p>
                              <p className="text-[#F8FAFC] font-semibold">
                                {new Date(subscription.created_at).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </p>
                            </div>
                          </div>
                        </div>

                        <button className="ml-6 text-[#3B82F6] hover:text-[#2563EB] transition-colors">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>

                        {/* Action Menu */}
                        <div className="relative ml-3" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              const menu = e.currentTarget.nextElementSibling as HTMLElement;
                              menu.classList.toggle('hidden');
                            }}
                            className="p-2 hover:bg-[#334155] rounded-lg transition-colors border border-[#334155]"
                            title="Actions"
                          >
                            <svg className="w-5 h-5 text-[#F8FAFC]" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                            </svg>
                          </button>
                          <div className="hidden absolute right-0 mt-2 w-48 bg-[#1E293B] border border-[#334155] rounded-lg shadow-xl z-50">
                            {subscription.status === 'ACTIVE' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSubscriptionAction(subscription, 'suspend');
                                  const menu = e.currentTarget.parentElement as HTMLElement;
                                  menu.classList.add('hidden');
                                }}
                                className="w-full px-4 py-2 text-left text-[#F8FAFC] hover:bg-[#334155] transition-colors flex items-center gap-2 rounded-t-lg"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Suspend
                              </button>
                            )}
                            {subscription.status === 'SUSPENDED' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSubscriptionAction(subscription, 'resume');
                                  const menu = e.currentTarget.parentElement as HTMLElement;
                                  menu.classList.add('hidden');
                                }}
                                className="w-full px-4 py-2 text-left text-[#F8FAFC] hover:bg-[#334155] transition-colors flex items-center gap-2 rounded-t-lg"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Resume
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSubscriptionAction(subscription, 'cancel');
                                const menu = e.currentTarget.parentElement as HTMLElement;
                                menu.classList.add('hidden');
                              }}
                              className="w-full px-4 py-2 text-left text-[#EF4444] hover:bg-[#334155] transition-colors flex items-center gap-2 rounded-b-lg"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              Cancel Subscription
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="bg-[#3B82F6]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Subscriptions Found</h3>
              <p className="text-[#94A3B8]">
                {selectedTier || selectedStatus || searchQuery
                  ? 'Try adjusting your filters'
                  : 'No subscriptions have been created yet'}
              </p>
            </div>
          )}
        </div>
          )}

          {/* Subscription Details Modal */}
          {showDetailsModal && selectedSubscription && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                {/* Modal Header */}
                <div className="sticky top-0 bg-[#1E293B] border-b border-[#334155] p-6 flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-1">
                      Subscription Details
                    </h2>
                    <p className="text-[#94A3B8]">{selectedSubscription.organization_name}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => window.print()}
                      className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors no-print"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                      </svg>
                      Print Receipt
                    </button>
                    <button
                      onClick={handleCloseModal}
                      className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors no-print"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Modal Content */}
                {detailsLoading ? (
                  <div className="p-12 text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                    <p className="text-[#94A3B8] mt-4">Loading details...</p>
                  </div>
                ) : detailsData ? (
                  <div 
                    className="p-6 space-y-6" 
                    data-print-content="subscription-receipt"
                  >
                    {/* Print-only Receipt Header */}
                    <div className="hidden print:block border-4 border-double border-black p-6 mb-8 text-center font-mono">
                      <div className="text-2xl font-bold mb-2 tracking-wider">BUG BOUNTY PLATFORM</div>
                      <div className="text-xl font-bold mb-4">SUBSCRIPTION PAYMENT RECEIPT</div>
                      <div className="border-t-2 border-b-2 border-black py-3 my-3">
                        <div className="text-base"><strong>Organization:</strong> {detailsData.subscription.organization_name}</div>
                        <div className="text-sm mt-1"><strong>Date Issued:</strong> {new Date().toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'short', 
                          day: 'numeric' 
                        })}</div>
                      </div>
                    </div>

                    {/* Print-only Subscription Info */}
                    <div className="hidden print:block bg-white border-2 border-black p-6 mb-6">
                      <h3 className="text-lg font-semibold mb-4 uppercase tracking-wide">Subscription Information</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Tier:</span>
                          <span className="font-bold">{detailsData.subscription.tier}</span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Status:</span>
                          <span className="font-bold">{detailsData.subscription.status}</span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Subscription Fee:</span>
                          <span className="font-bold">
                            {detailsData.subscription.subscription_fee.toLocaleString()} {detailsData.subscription.currency}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Billing Cycle:</span>
                          <span className="font-medium">
                            Every {detailsData.subscription.billing_cycle_months} months
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Start Date:</span>
                          <span className="font-medium">
                            {new Date(detailsData.subscription.start_date).toLocaleDateString('en-US', { 
                              year: 'numeric', 
                              month: 'short', 
                              day: 'numeric' 
                            })}
                          </span>
                        </div>
                        <div className="flex justify-between pb-2">
                          <span className="font-medium">Next Billing Date:</span>
                          <span className="font-medium">
                            {new Date(detailsData.subscription.next_billing_date).toLocaleDateString('en-US', { 
                              year: 'numeric', 
                              month: 'short', 
                              day: 'numeric' 
                            })}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Print-only Payment Summary */}
                    <div className="hidden print:block bg-white border-2 border-black p-6 mb-6">
                      <h3 className="text-lg font-semibold mb-4 uppercase tracking-wide">Payment Summary</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Total Payments:</span>
                          <span className="font-bold text-lg">{detailsData.stats.total_payments}</span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Paid:</span>
                          <span className="font-bold text-lg">{detailsData.stats.paid_payments}</span>
                        </div>
                        <div className="flex justify-between border-b border-dotted border-gray-600 pb-2">
                          <span className="font-medium">Pending:</span>
                          <span className="font-bold text-lg">{detailsData.stats.pending_payments}</span>
                        </div>
                        <div className="flex justify-between pt-2 border-t-2 border-black">
                          <span className="font-bold">TOTAL PAID:</span>
                          <span className="font-bold text-xl">
                            {detailsData.stats.total_paid.toLocaleString()} ETB
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Print-only Payment History */}
                    <div className="hidden print:block bg-white border-2 border-black p-6 mb-6">
                      <h3 className="text-lg font-semibold mb-4 uppercase tracking-wide">Payment History</h3>
                      {detailsData.payment_history.length > 0 ? (
                        <div className="space-y-4">
                          {detailsData.payment_history.map((payment: any) => (
                            <div
                              key={payment.payment_id}
                              className="border-2 border-black p-4"
                            >
                              <div className="flex justify-between items-center mb-3 pb-2 border-b border-dotted border-gray-600">
                                <span className="font-bold">Invoice: {payment.invoice_number}</span>
                                <span className="font-bold uppercase px-3 py-1 border-2 border-black">
                                  {payment.status}
                                </span>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="font-medium">Amount:</span>
                                  <span className="font-bold">
                                    {payment.amount.toLocaleString()} {payment.currency}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-medium">Due Date:</span>
                                  <span>
                                    {new Date(payment.due_date).toLocaleDateString('en-US', { 
                                      year: 'numeric', 
                                      month: 'short', 
                                      day: 'numeric' 
                                    })}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-medium">
                                    {payment.status === 'paid' ? 'Paid At:' : 'Created:'}
                                  </span>
                                  <span>
                                    {payment.paid_at
                                      ? new Date(payment.paid_at).toLocaleDateString('en-US', { 
                                          year: 'numeric', 
                                          month: 'short', 
                                          day: 'numeric' 
                                        })
                                      : new Date(payment.created_at).toLocaleDateString('en-US', { 
                                          year: 'numeric', 
                                          month: 'short', 
                                          day: 'numeric' 
                                        })}
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-center py-4">No payment history</p>
                      )}
                    </div>

                    {/* Screen-only sections (hidden when printing) */}
                    <div className="print:hidden space-y-6">
                      {/* Subscription Info */}
                      <div className="bg-[#0F172A] rounded-lg p-6 border border-[#334155]">
                        <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Subscription Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-[#94A3B8] text-sm">Tier</p>
                            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(detailsData.subscription.tier)}`}>
                              {detailsData.subscription.tier}
                            </span>
                          </div>
                          <div>
                            <p className="text-[#94A3B8] text-sm">Status</p>
                            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-bold uppercase ${getStatusBadgeColor(detailsData.subscription.status)}`}>
                              {detailsData.subscription.status}
                            </span>
                          </div>
                          <div>
                            <p className="text-[#94A3B8] text-sm">Subscription Fee</p>
                            <p className="text-[#F8FAFC] font-medium mt-1">
                              {detailsData.subscription.subscription_fee.toLocaleString()} {detailsData.subscription.currency}
                            </p>
                          </div>
                          <div>
                            <p className="text-[#94A3B8] text-sm">Billing Cycle</p>
                            <p className="text-[#F8FAFC] font-medium mt-1">
                              Every {detailsData.subscription.billing_cycle_months} months
                            </p>
                          </div>
                          <div>
                            <p className="text-[#94A3B8] text-sm">Start Date</p>
                            <p className="text-[#F8FAFC] font-medium mt-1">
                              {new Date(detailsData.subscription.start_date).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </p>
                          </div>
                          <div>
                            <p className="text-[#94A3B8] text-sm">Next Billing Date</p>
                            <p className="text-[#F8FAFC] font-medium mt-1">
                              {new Date(detailsData.subscription.next_billing_date).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Payment Stats */}
                      <div className="grid grid-cols-4 gap-4">
                        <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                          <p className="text-[#94A3B8] text-sm">Total Payments</p>
                          <p className="text-2xl font-bold text-[#F8FAFC] mt-1">
                            {detailsData.stats.total_payments}
                          </p>
                        </div>
                        <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                          <p className="text-[#94A3B8] text-sm">Paid</p>
                          <p className="text-2xl font-bold text-[#10B981] mt-1">
                            {detailsData.stats.paid_payments}
                          </p>
                        </div>
                        <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                          <p className="text-[#94A3B8] text-sm">Pending</p>
                          <p className="text-2xl font-bold text-[#F59E0B] mt-1">
                            {detailsData.stats.pending_payments}
                          </p>
                        </div>
                        <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                          <p className="text-[#94A3B8] text-sm">Total Paid</p>
                          <p className="text-2xl font-bold text-[#3B82F6] mt-1">
                            {detailsData.stats.total_paid.toLocaleString()}
                          </p>
                        </div>
                      </div>

                      {/* Payment History */}
                      <div className="bg-[#0F172A] rounded-lg p-6 border border-[#334155]">
                        <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payment History</h3>
                        {detailsData.payment_history.length > 0 ? (
                          <div className="space-y-3">
                            {detailsData.payment_history.map((payment: any) => (
                              <div
                                key={payment.payment_id}
                                className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]"
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                      <p className="text-[#F8FAFC] font-medium">{payment.invoice_number}</p>
                                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                        payment.status === 'paid' ? 'bg-[#10B981] text-white' : 'bg-[#F59E0B] text-white'
                                      }`}>
                                        {payment.status}
                                      </span>
                                    </div>
                                    <div className="grid grid-cols-3 gap-4 text-sm">
                                      <div>
                                        <p className="text-[#94A3B8]">Amount</p>
                                        <p className="text-[#F8FAFC]">
                                          {payment.amount.toLocaleString()} {payment.currency}
                                        </p>
                                      </div>
                                      <div>
                                        <p className="text-[#94A3B8]">Due Date</p>
                                        <p className="text-[#F8FAFC]">
                                          {new Date(payment.due_date).toLocaleDateString('en-US', { 
                                            year: 'numeric', 
                                            month: 'short', 
                                            day: 'numeric' 
                                          })}
                                        </p>
                                      </div>
                                      <div>
                                        <p className="text-[#94A3B8]">
                                          {payment.status === 'paid' ? 'Paid At' : 'Created'}
                                        </p>
                                        <p className="text-[#F8FAFC]">
                                          {payment.paid_at
                                            ? new Date(payment.paid_at).toLocaleDateString('en-US', { 
                                                year: 'numeric', 
                                                month: 'short', 
                                                day: 'numeric' 
                                              })
                                            : new Date(payment.created_at).toLocaleDateString('en-US', { 
                                                year: 'numeric', 
                                                month: 'short', 
                                                day: 'numeric' 
                                              })}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[#94A3B8] text-center py-4">No payment history</p>
                        )}
                      </div>
                    </div>

                    {/* Print-only Receipt Footer */}
                    <div className="hidden print:block border-t-4 border-double border-black pt-6 mt-8 text-center font-mono">
                      <div className="text-base font-bold mb-3 tracking-wider">*** OFFICIAL RECEIPT ***</div>
                      <div className="text-sm mb-1">This is a computer-generated receipt.</div>
                      <div className="text-sm mb-1">No signature required.</div>
                      <div className="text-sm mt-4 font-bold">Thank you for your business!</div>
                      <div className="text-xs mt-3 text-gray-600">Bug Bounty Platform - Finance Department</div>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          )}

          {/* Overdue Tab */}
          {selectedTab === 'overdue' && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8">
              {overdueLoading ? (
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading overdue subscriptions...</p>
                </div>
              ) : overdue.length > 0 ? (
                <div className="space-y-0">
                  {overdue.map((subscription: any, index: number) => (
                    <div key={subscription.subscription_id}>
                      <div className="pb-6 mb-6 border-b border-[#EF4444]/30 last:border-b-0 last:pb-0 last:mb-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-4">
                              <h3 className="text-xl font-bold text-[#F8FAFC]">
                                {subscription.organization_name}
                              </h3>
                              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(subscription.tier)}`}>
                                {subscription.tier}
                              </span>
                              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-[#EF4444] text-white">
                                OVERDUE
                              </span>
                            </div>

                            <div className="grid grid-cols-4 gap-6 text-sm">
                              <div>
                                <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Days Overdue</p>
                                <p className="text-[#EF4444] font-bold text-xl">
                                  {subscription.days_overdue} days
                                </p>
                              </div>
                              <div>
                                <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Amount Due</p>
                                <p className="text-[#F8FAFC] font-semibold">
                                  {subscription.subscription_fee.toLocaleString()} {subscription.currency}
                                </p>
                              </div>
                              <div>
                                <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Last Payment Date</p>
                                <p className="text-[#F8FAFC] font-semibold">
                                  {new Date(subscription.next_billing_date).toLocaleDateString('en-US', { 
                                    year: 'numeric', 
                                    month: 'short', 
                                    day: 'numeric' 
                                  })}
                                </p>
                              </div>
                              <div>
                                <p className="text-[#64748B] text-xs uppercase tracking-wide mb-1">Contact</p>
                                <p className="text-[#F8FAFC] font-semibold">
                                  {subscription.contact_email || 'N/A'}
                                </p>
                              </div>
                            </div>
                          </div>

                          <button
                            onClick={() => handleViewDetails(subscription)}
                            className="ml-6 px-6 py-2.5 bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-lg font-semibold transition-colors"
                          >
                            View Details
                          </button>
                          <button
                            onClick={() => handleSubscriptionAction(subscription, 'reminder')}
                            className="ml-3 px-6 py-2.5 bg-[#F59E0B] hover:bg-[#D97706] text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            Send Reminder
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="bg-[#10B981]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Overdue Subscriptions</h3>
                  <p className="text-[#94A3B8]">All subscriptions are up to date</p>
                </div>
              )}
            </div>
          )}

          {/* Revenue Report Tab */}
          {selectedTab === 'revenue' && (
            <div 
              className="bg-[#1E293B] rounded-lg border border-[#334155] p-8"
              data-print-content="revenue-report"
              data-print-date={new Date().toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
              })}
            >
              {revenueLoading ? (
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                  <p className="text-[#94A3B8] mt-4">Loading revenue report...</p>
                </div>
              ) : revenue ? (
                <div className="space-y-8">
                  {/* Header with Print Button */}
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-[#F8FAFC]">Revenue Report</h2>
                    <button
                      onClick={() => window.print()}
                      className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                      </svg>
                      Print Report
                    </button>
                  </div>

                  {/* Summary Section */}
                  <div>
                    <h2 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                      Revenue Summary
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <p className="text-[#64748B] text-xs uppercase tracking-wide mb-2">Total Revenue</p>
                        <p className="text-4xl font-bold text-[#F8FAFC]">
                          {revenue.total_revenue?.toLocaleString() || 0} ETB
                        </p>
                        <p className="text-[#64748B] text-xs mt-2">
                          {revenue.payment_count || 0} payments processed
                        </p>
                      </div>
                      <div>
                        <p className="text-[#64748B] text-xs uppercase tracking-wide mb-2">Average Payment</p>
                        <p className="text-4xl font-bold text-[#F8FAFC]">
                          {revenue.average_payment?.toLocaleString() || 0} ETB
                        </p>
                        <p className="text-[#64748B] text-xs mt-2">
                          Per transaction
                        </p>
                      </div>
                      <div>
                        <p className="text-[#64748B] text-xs uppercase tracking-wide mb-2">Tier Diversity</p>
                        <p className="text-4xl font-bold text-[#F8FAFC]">
                          {revenueByTierArray.length}
                        </p>
                        <p className="text-[#64748B] text-xs mt-2">
                          Active subscription tiers
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Revenue by Tier Section */}
                  <div>
                    <h3 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                      Revenue by Tier
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {revenueByTierArray.length > 0 ? (
                        revenueByTierArray.map((tier: any) => (
                          <div key={tier.tier} className="bg-[#0F172A] rounded-lg p-5 border border-[#334155]">
                            <div className="flex items-center justify-between mb-3">
                              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase text-white ${getTierBadgeColor(tier.tier)}`}>
                                {tier.tier}
                              </span>
                              <span className="text-[#64748B] text-sm font-medium">
                                {((tier.revenue / revenue.total_revenue) * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="space-y-2">
                              <div className="flex justify-between items-center">
                                <span className="text-[#94A3B8] text-sm">Revenue</span>
                                <span className="text-[#F8FAFC] font-semibold">
                                  {tier.revenue.toLocaleString()} ETB
                                </span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-[#94A3B8] text-sm">Subscriptions</span>
                                <span className="text-[#F8FAFC] font-semibold">
                                  {tier.count}
                                </span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-[#94A3B8] text-sm">Average</span>
                                <span className="text-[#F8FAFC] font-semibold">
                                  {tier.average?.toLocaleString() || 0} ETB
                                </span>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="col-span-3">
                          <p className="text-[#94A3B8] text-center py-4">No revenue data available</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Payment Summary Section */}
                  <div>
                    <h3 className="text-xl font-semibold text-[#F8FAFC] mb-6 pb-3 border-b border-[#334155]">
                      Payment Summary
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                        <p className="text-[#94A3B8] text-sm mb-2">Total Payments</p>
                        <p className="text-3xl font-bold text-[#F8FAFC]">
                          {revenue.payment_count || 0}
                        </p>
                      </div>
                      <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                        <p className="text-[#94A3B8] text-sm mb-2">Total Revenue</p>
                        <p className="text-3xl font-bold text-[#10B981]">
                          {revenue.total_revenue?.toLocaleString() || 0} ETB
                        </p>
                      </div>
                      <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                        <p className="text-[#94A3B8] text-sm mb-2">Average per Payment</p>
                        <p className="text-3xl font-bold text-[#3B82F6]">
                          {revenue.average_payment?.toLocaleString() || 0} ETB
                        </p>
                      </div>
                    </div>
                    {revenue.period && (revenue.period.start || revenue.period.end) && (
                      <div className="mt-4 pt-4 border-t border-[#334155]">
                        <p className="text-[#94A3B8] text-sm">
                          Report Period: {revenue.period.start ? new Date(revenue.period.start).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric' 
                          }) : 'All time'} 
                          {revenue.period.end ? ` - ${new Date(revenue.period.end).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric' 
                          })}` : ' - Present'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="bg-[#334155]/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Revenue Data</h3>
                  <p className="text-[#94A3B8]">Revenue data will appear here once payments are processed</p>
                </div>
              )}
            </div>
          )}

          {/* Verify Payment Modal */}
          {showVerifyModal && selectedPayment && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] max-w-md w-full">
                <div className="border-b border-[#334155] p-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">Verify Payment</h2>
                  <p className="text-[#94A3B8] mt-1">
                    {selectedPayment.organization_name} - {selectedPayment.invoice_number}
                  </p>
                </div>

                <div className="p-6 space-y-4">
                  <div>
                    <p className="text-[#94A3B8] text-sm mb-2">Amount</p>
                    <p className="text-2xl font-bold text-[#F8FAFC]">
                      {selectedPayment.amount.toLocaleString()} {selectedPayment.currency}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                      Payment Method
                    </label>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
                    >
                      <option value="bank_transfer">Bank Transfer</option>
                      <option value="wallet">Wallet</option>
                      <option value="cash">Cash</option>
                      <option value="check">Check</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                      Transaction ID *
                    </label>
                    <input
                      type="text"
                      value={transactionId}
                      onChange={(e) => setTransactionId(e.target.value)}
                      placeholder="Enter transaction/reference ID"
                      className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6]"
                    />
                  </div>
                </div>

                <div className="border-t border-[#334155] p-6 flex gap-3">
                  <button
                    onClick={() => {
                      setShowVerifyModal(false);
                      setSelectedPayment(null);
                      setPaymentMethod('bank_transfer');
                      setTransactionId('');
                    }}
                    className="flex-1 px-6 py-2 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] rounded-lg font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleVerifyPayment}
                    disabled={verifyPaymentMutation.isLoading}
                    className="flex-1 px-6 py-2 bg-[#10B981] hover:bg-[#059669] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {verifyPaymentMutation.isLoading ? 'Verifying...' : 'Verify Payment'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Subscription Action Modal */}
          {showActionModal && actionSubscription && actionType && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] max-w-md w-full">
                <div className="border-b border-[#334155] p-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">
                    {actionType === 'suspend' && 'Suspend Subscription'}
                    {actionType === 'resume' && 'Resume Subscription'}
                    {actionType === 'cancel' && 'Cancel Subscription'}
                    {actionType === 'reminder' && 'Send Payment Reminder'}
                  </h2>
                  <p className="text-[#94A3B8] mt-1">{actionSubscription.organization_name}</p>
                </div>

                <div className="p-6 space-y-4">
                  <div className="bg-[#0F172A] rounded-lg p-4 border border-[#334155]">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-[#94A3B8] text-sm">Subscription Fee</span>
                      <span className="text-[#F8FAFC] font-semibold">
                        {actionSubscription.subscription_fee.toLocaleString()} {actionSubscription.currency}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#94A3B8] text-sm">Current Status</span>
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getStatusBadgeColor(actionSubscription.status)}`}>
                        {actionSubscription.status}
                      </span>
                    </div>
                  </div>

                  {actionType === 'reminder' ? (
                    <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-4">
                      <p className="text-[#F8FAFC] text-sm">
                        A payment reminder email will be sent to the organization with payment details and due date information.
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className={`${
                        actionType === 'cancel' ? 'bg-[#EF4444]/10 border-[#EF4444]/30' : 'bg-[#F59E0B]/10 border-[#F59E0B]/30'
                      } border rounded-lg p-4`}>
                        <p className="text-[#F8FAFC] text-sm font-medium mb-2">
                          {actionType === 'suspend' && 'This will temporarily suspend the subscription. The organization will lose access until resumed.'}
                          {actionType === 'resume' && 'This will reactivate the subscription and restore organization access.'}
                          {actionType === 'cancel' && 'This action cannot be undone. The subscription will be permanently cancelled.'}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                          Reason {actionType === 'cancel' ? '(Required)' : '(Optional)'}
                        </label>
                        <textarea
                          value={actionReason}
                          onChange={(e) => setActionReason(e.target.value)}
                          placeholder={`Enter reason for ${actionType}...`}
                          rows={3}
                          className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6] resize-none"
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="border-t border-[#334155] p-6 flex gap-3">
                  <button
                    onClick={() => {
                      setShowActionModal(false);
                      setActionType(null);
                      setActionSubscription(null);
                      setActionReason('');
                    }}
                    className="flex-1 px-6 py-2 bg-[#334155] hover:bg-[#475569] text-[#F8FAFC] rounded-lg font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmSubscriptionAction}
                    disabled={subscriptionActionMutation.isLoading || (actionType === 'cancel' && !actionReason.trim())}
                    className={`flex-1 px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                      actionType === 'cancel'
                        ? 'bg-[#EF4444] hover:bg-[#DC2626] text-white'
                        : actionType === 'reminder'
                        ? 'bg-[#F59E0B] hover:bg-[#D97706] text-white'
                        : 'bg-[#3B82F6] hover:bg-[#2563EB] text-white'
                    }`}
                  >
                    {subscriptionActionMutation.isLoading ? 'Processing...' : 
                      actionType === 'suspend' ? 'Suspend' :
                      actionType === 'resume' ? 'Resume' :
                      actionType === 'cancel' ? 'Cancel Subscription' :
                      'Send Reminder'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          /* Page setup */
          @page {
            margin: 1.5cm;
            size: A4;
          }
          
          /* Reset and hide everything first */
          body, html {
            background: white !important;
            margin: 0 !important;
            padding: 0 !important;
          }
          
          body * {
            visibility: hidden !important;
          }
          
          /* CRITICAL: Hide screen-only sections completely */
          .print\\:hidden,
          .print\\:hidden * {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            overflow: hidden !important;
          }
          
          /* Show ONLY print sections */
          .hidden.print\\:block {
            display: block !important;
            visibility: visible !important;
          }
          
          .hidden.print\\:block * {
            visibility: visible !important;
          }
          
          /* Position receipt container */
          [data-print-content="subscription-receipt"] {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            padding: 20px 40px !important;
            visibility: visible !important;
          }
          
          /* Apply monospace font to all receipt content */
          [data-print-content="subscription-receipt"],
          [data-print-content="subscription-receipt"] * {
            font-family: 'Courier New', Courier, monospace !important;
            background: white !important;
            color: #000 !important;
          }
          
          /* Receipt header - double border box */
          .border-double {
            border-style: double !important;
            border-width: 4px !important;
            border-color: #000 !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
          }
          
          /* Section boxes - solid border */
          .border-2 {
            border-width: 2px !important;
            border-style: solid !important;
            border-color: #000 !important;
            padding: 15px !important;
            margin-bottom: 15px !important;
          }
          
          /* Section headers */
          h3 {
            font-size: 14px !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            margin-bottom: 12px !important;
            padding-bottom: 0 !important;
            border: none !important;
          }
          
          /* Dotted line separators */
          .border-dotted {
            border-style: dotted !important;
            border-color: #333 !important;
            border-width: 1px !important;
          }
          
          /* Text styling */
          .font-bold {
            font-weight: bold !important;
          }
          
          .font-medium {
            font-weight: 500 !important;
          }
          
          .font-semibold {
            font-weight: 600 !important;
          }
          
          .uppercase {
            text-transform: uppercase !important;
          }
          
          .tracking-wider {
            letter-spacing: 0.15em !important;
          }
          
          .tracking-wide {
            letter-spacing: 0.05em !important;
          }
          
          /* Font sizes */
          .text-xs {
            font-size: 10px !important;
          }
          
          .text-sm {
            font-size: 11px !important;
          }
          
          .text-base {
            font-size: 13px !important;
          }
          
          .text-lg {
            font-size: 14px !important;
          }
          
          .text-xl {
            font-size: 16px !important;
          }
          
          .text-2xl {
            font-size: 18px !important;
          }
          
          /* Spacing */
          .space-y-2 > * + * {
            margin-top: 8px !important;
          }
          
          .space-y-3 > * + * {
            margin-top: 10px !important;
          }
          
          .space-y-4 > * + * {
            margin-top: 12px !important;
          }
          
          /* Padding */
          .p-4 {
            padding: 12px !important;
          }
          
          .p-6 {
            padding: 15px !important;
          }
          
          .pb-2 {
            padding-bottom: 8px !important;
          }
          
          .pt-2 {
            padding-top: 8px !important;
          }
          
          .mb-1, .mb-2, .mb-3, .mb-4 {
            margin-bottom: 8px !important;
          }
          
          .mt-1, .mt-2, .mt-3, .mt-4 {
            margin-top: 8px !important;
          }
          
          /* Border top for totals */
          .border-t-2 {
            border-top-width: 2px !important;
            border-top-style: solid !important;
            border-top-color: #000 !important;
          }
          
          .border-t-4 {
            border-top-width: 4px !important;
            border-top-style: double !important;
            border-top-color: #000 !important;
          }
          
          /* Remove all rounded corners */
          * {
            border-radius: 0 !important;
          }
          
          /* Flex layouts */
          .flex {
            display: flex !important;
          }
          
          .justify-between {
            justify-content: space-between !important;
          }
          
          .items-center {
            align-items: center !important;
          }
          
          /* Text alignment */
          .text-center {
            text-align: center !important;
          }
          
          /* Hide no-print elements */
          .no-print {
            display: none !important;
            visibility: hidden !important;
          }
        }
      `}</style>
    </ProtectedRoute>
  );
}
