'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/components/ui/Toast';

interface Payout {
  id: string;
  researcher_id: string;
  researcher_name: string;
  amount: number;
  payment_method: string;
  status: string;
  requested_at: string;
  processed_at: string | null;
  created_at: string;
}

export default function FinancePayoutsPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);
  
  // Get status from URL params, default to 'pending' (which means requested/awaiting approval)
  const statusFilter = searchParams.get('status') || 'pending';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = `/wallet/payouts?status=${statusFilter}`;

  const { data, isLoading, error } = useApiQuery<any>({ endpoint });

  const approvePayoutMutation = useApiMutation({
    method: 'POST',
    onSuccess: (data, variables) => {
      showToast('Payout approved successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: [endpoint] });
      setProcessingId(null);
    },
    onError: (error: any) => {
      showToast(error?.message || 'Failed to approve payout', 'error');
      setProcessingId(null);
    },
  });

  const payouts: Payout[] = data?.payouts || [];

  // Apply search filter
  const filteredPayouts = payouts.filter((payout: Payout) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payout.researcher_name?.toLowerCase().includes(query) ||
        payout.id?.toLowerCase().includes(query) ||
        payout.payment_method?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleApprovePayout = async (payoutId: string) => {
    if (confirm('Are you sure you want to approve this payout? This will initiate the payment process.')) {
      setProcessingId(payoutId);
      await approvePayoutMutation.mutateAsync({
        endpoint: `/wallet/payouts/${payoutId}/approve`,
        data: {},
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'requested':
      case 'pending':
        return 'bg-[#F59E0B] text-white';
      case 'processing':
        return 'bg-[#3B82F6] text-white';
      case 'completed':
        return 'bg-[#10B981] text-white';
      case 'rejected':
      case 'failed':
        return 'bg-[#DC2626] text-white';
      default:
        return 'bg-[#64748B] text-white';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'requested':
      case 'pending':
        return 'Requested';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'rejected':
        return 'Rejected';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Payouts"
          subtitle={`${filteredPayouts.length} ${statusFilter} payout${filteredPayouts.length !== 1 ? 's' : ''}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Status Filter Tabs */}
          <div className="mb-6 flex gap-2 flex-wrap">
            <Link href="/finance/payouts?status=pending">
              <Button 
                variant={statusFilter === 'pending' ? 'warning' : 'secondary'} 
                size="sm"
              >
                Requested
              </Button>
            </Link>
            <Link href="/finance/payouts?status=processing">
              <Button 
                variant={statusFilter === 'processing' ? 'primary' : 'secondary'} 
                size="sm"
              >
                Processing
              </Button>
            </Link>
            <Link href="/finance/payouts?status=completed">
              <Button 
                variant={statusFilter === 'completed' ? 'success' : 'secondary'} 
                size="sm"
              >
                Completed
              </Button>
            </Link>
          </div>

          {/* Info Banner */}
          <div className="mb-6 bg-[#1E293B] border border-[#3B82F6] rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-[#3B82F6] mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-[#F8FAFC] font-medium">About Researcher Payouts</p>
                <p className="text-[#94A3B8] text-sm mt-1">
                  {statusFilter === 'pending' && 'These are withdrawal requests from researchers. Review and approve to initiate payment processing.'}
                  {statusFilter === 'processing' && 'These payouts are currently being processed through the payment gateway.'}
                  {statusFilter === 'completed' && 'These payouts have been successfully completed and funds have been transferred to researchers.'}
                </p>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by researcher name, payout ID, or payment method..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading payouts...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-[#1E293B] border border-[#DC2626] rounded-lg p-4 mb-6">
              <p className="text-[#DC2626]">Failed to load payouts. Please try again.</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && filteredPayouts.length === 0 && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
              <svg className="w-16 h-16 text-[#64748B] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
                No {statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Payouts
              </h3>
              <p className="text-[#94A3B8]">
                {searchQuery
                  ? 'No payouts match your search criteria.'
                  : `There are no ${statusFilter} payouts at this time.`}
              </p>
            </div>
          )}

          {/* Payouts List */}
          {!isLoading && !error && filteredPayouts.length > 0 && (
            <div className="space-y-4">
              {filteredPayouts.map((payout) => (
                <div
                  key={payout.id}
                  className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 hover:border-[#3B82F6] transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Left Section: Researcher & Details */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-[#F8FAFC]">
                          {payout.researcher_name || 'Unknown Researcher'}
                        </h3>
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getStatusColor(payout.status)}`}>
                          {getStatusLabel(payout.status)}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-[#64748B] mb-1">Payout ID</p>
                          <p className="text-[#F8FAFC] font-mono text-xs">{payout.id}</p>
                        </div>
                        <div>
                          <p className="text-[#64748B] mb-1">Payment Method</p>
                          <p className="text-[#F8FAFC] capitalize">{payout.payment_method?.replace('_', ' ') || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-[#64748B] mb-1">Requested At</p>
                          <p className="text-[#F8FAFC]">
                            {payout.requested_at ? new Date(payout.requested_at).toLocaleString() : 'N/A'}
                          </p>
                        </div>
                        {payout.processed_at && (
                          <div>
                            <p className="text-[#64748B] mb-1">Processed At</p>
                            <p className="text-[#F8FAFC]">
                              {new Date(payout.processed_at).toLocaleString()}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Right Section: Amount & Action */}
                    <div className="flex flex-col items-end gap-4 min-w-[200px]">
                      <div className="text-right">
                        <p className="text-[#64748B] text-sm mb-1">Payout Amount</p>
                        <p className="text-[#10B981] font-bold text-2xl">
                          {payout.amount.toLocaleString()} ETB
                        </p>
                      </div>

                      {statusFilter === 'pending' && (
                        <Button
                          variant="primary"
                          size="md"
                          onClick={() => handleApprovePayout(payout.id)}
                          disabled={processingId === payout.id || approvePayoutMutation.isLoading}
                          className="w-full"
                        >
                          {processingId === payout.id ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Approving...
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Approve Payout
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
