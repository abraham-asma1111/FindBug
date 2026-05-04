'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

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

export default function FinanceSubscriptionsPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedTier, setSelectedTier] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<Subscription | null>(null);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Build query params
  const queryParams = new URLSearchParams();
  if (selectedTier) queryParams.append('tier', selectedTier);
  if (selectedStatus) queryParams.append('status', selectedStatus);
  if (searchQuery) queryParams.append('search', searchQuery);

  // Fetch subscriptions
  const { data: subscriptionsData, isLoading, refetch } = useApiQuery<any>({
    endpoint: `/subscriptions/all?${queryParams.toString()}`,
  });

  // Fetch subscription details when modal opens
  const { data: detailsData, isLoading: detailsLoading } = useApiQuery<SubscriptionDetails>({
    endpoint: selectedSubscription ? `/subscriptions/${selectedSubscription.subscription_id}/details` : undefined,
    enabled: !!selectedSubscription,
  });

  const subscriptions = subscriptionsData?.subscriptions || [];
  const total = subscriptionsData?.total || 0;

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

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Subscription Management"
          subtitle="Manage organization subscriptions and billing"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Filters */}
          <div className="mb-6 bg-[#1E293B] rounded-xl border border-[#334155] p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
              <p className="text-[#94A3B8] text-sm mb-2">Total Subscriptions</p>
              <p className="text-3xl font-bold text-[#F8FAFC]">{total}</p>
            </div>
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
              <p className="text-[#94A3B8] text-sm mb-2">Active</p>
              <p className="text-3xl font-bold text-[#10B981]">
                {subscriptions.filter((s: Subscription) => s.status === 'ACTIVE').length}
              </p>
            </div>
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
              <p className="text-[#94A3B8] text-sm mb-2">Pending</p>
              <p className="text-3xl font-bold text-[#F59E0B]">
                {subscriptions.filter((s: Subscription) => s.status === 'PENDING').length}
              </p>
            </div>
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
              <p className="text-[#94A3B8] text-sm mb-2">Suspended</p>
              <p className="text-3xl font-bold text-[#EF4444]">
                {subscriptions.filter((s: Subscription) => s.status === 'SUSPENDED').length}
              </p>
            </div>
          </div>

          {/* Subscriptions List */}
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
              <p className="text-[#94A3B8] mt-4">Loading subscriptions...</p>
            </div>
          ) : subscriptions.length > 0 ? (
            <div className="space-y-4">
              {subscriptions.map((subscription: Subscription) => (
                <div
                  key={subscription.subscription_id}
                  className="bg-[#1E293B] rounded-xl border border-[#334155] p-6 hover:border-[#3B82F6] transition-colors cursor-pointer"
                  onClick={() => handleViewDetails(subscription)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-[#F8FAFC]">
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

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-[#94A3B8]">Subscription Fee</p>
                          <p className="text-[#F8FAFC] font-medium">
                            {subscription.subscription_fee.toLocaleString()} {subscription.currency}
                          </p>
                        </div>
                        <div>
                          <p className="text-[#94A3B8]">Start Date</p>
                          <p className="text-[#F8FAFC] font-medium">
                            {new Date(subscription.start_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-[#94A3B8]">Next Billing</p>
                          <p className="text-[#F8FAFC] font-medium">
                            {new Date(subscription.next_billing_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-[#94A3B8]">Created</p>
                          <p className="text-[#F8FAFC] font-medium">
                            {new Date(subscription.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>

                    <button className="ml-4 text-[#3B82F6] hover:text-[#2563EB]">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
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
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">No Subscriptions Found</h3>
              <p className="text-[#94A3B8]">
                {selectedTier || selectedStatus || searchQuery
                  ? 'Try adjusting your filters'
                  : 'No subscriptions have been created yet'}
              </p>
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
                  <button
                    onClick={handleCloseModal}
                    className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* Modal Content */}
                {detailsLoading ? (
                  <div className="p-12 text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#334155] border-t-[#3B82F6]"></div>
                    <p className="text-[#94A3B8] mt-4">Loading details...</p>
                  </div>
                ) : detailsData ? (
                  <div className="p-6 space-y-6">
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
                            {new Date(detailsData.subscription.start_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-[#94A3B8] text-sm">Next Billing Date</p>
                          <p className="text-[#F8FAFC] font-medium mt-1">
                            {new Date(detailsData.subscription.next_billing_date).toLocaleDateString()}
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
                                        {new Date(payment.due_date).toLocaleDateString()}
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-[#94A3B8]">
                                        {payment.status === 'paid' ? 'Paid At' : 'Created'}
                                      </p>
                                      <p className="text-[#F8FAFC]">
                                        {payment.paid_at
                                          ? new Date(payment.paid_at).toLocaleDateString()
                                          : new Date(payment.created_at).toLocaleDateString()}
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
                ) : null}
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
