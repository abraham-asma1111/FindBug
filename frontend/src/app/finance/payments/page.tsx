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

interface BountyPayment {
  payment_id: string;
  transaction_id: string;
  status: string;
  report: {
    id: string;
    report_number: string;
    title: string;
    severity: string;
  };
  researcher: {
    id: string;
    username: string;
  };
  organization: {
    id: string;
    name: string;
  };
  researcher_amount: number;
  commission_amount: number;
  total_amount: number;
  approved_at: string;
  created_at: string;
}

export default function FinancePaymentsPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);
  
  // Get status from URL params, default to 'approved'
  const statusFilter = searchParams.get('status') || 'approved';

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const endpoint = `/bounty-payments?status_filter=${statusFilter}`;

  const { data, isLoading, error } = useApiQuery<any>({ endpoint });

  const processPaymentMutation = useApiMutation({
    method: 'POST',
    onSuccess: (data, variables) => {
      showToast('Payment processed successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: [endpoint] });
      setProcessingId(null);
    },
    onError: (error: any) => {
      showToast(error?.message || 'Failed to process payment', 'error');
      setProcessingId(null);
    },
  });

  const bountyPayments: BountyPayment[] = data?.bounty_payments || [];

  // Apply search filter
  const filteredPayments = bountyPayments.filter((payment: BountyPayment) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        payment.report?.report_number?.toLowerCase().includes(query) ||
        payment.report?.title?.toLowerCase().includes(query) ||
        payment.researcher?.username?.toLowerCase().includes(query) ||
        payment.organization?.name?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleProcessPayment = async (paymentId: string) => {
    if (confirm('Are you sure you want to process this payment? This will transfer funds to the researcher.')) {
      setProcessingId(paymentId);
      await processPaymentMutation.mutateAsync({
        endpoint: `/bounty-payments/process/${paymentId}`,
        data: {},
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-[#DC2626] text-white';
      case 'high':
        return 'bg-[#F59E0B] text-white';
      case 'medium':
        return 'bg-[#3B82F6] text-white';
      case 'low':
        return 'bg-[#10B981] text-white';
      default:
        return 'bg-[#64748B] text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'bg-[#F59E0B] text-white';
      case 'completed':
        return 'bg-[#10B981] text-white';
      case 'pending':
        return 'bg-[#3B82F6] text-white';
      case 'rejected':
        return 'bg-[#DC2626] text-white';
      default:
        return 'bg-[#64748B] text-white';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'Awaiting Processing';
      case 'completed':
        return 'Processed';
      case 'pending':
        return 'Pending Approval';
      case 'rejected':
        return 'Rejected';
      default:
        return status;
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Bounty Payment Processing"
          subtitle={`${filteredPayments.length} ${statusFilter} bounty payment${filteredPayments.length !== 1 ? 's' : ''}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Status Filter Tabs */}
          <div className="mb-6 flex gap-2 flex-wrap">
            <Link href="/finance/payments?status=approved">
              <Button 
                variant={statusFilter === 'approved' ? 'warning' : 'secondary'} 
                size="sm"
              >
                Awaiting Processing
              </Button>
            </Link>
            <Link href="/finance/payments?status=completed">
              <Button 
                variant={statusFilter === 'completed' ? 'success' : 'secondary'} 
                size="sm"
              >
                Processed
              </Button>
            </Link>
            <Link href="/finance/payments?status=pending">
              <Button 
                variant={statusFilter === 'pending' ? 'primary' : 'secondary'} 
                size="sm"
              >
                Pending Approval
              </Button>
            </Link>
            <Link href="/finance/payments?status=rejected">
              <Button 
                variant={statusFilter === 'rejected' ? 'danger' : 'secondary'} 
                size="sm"
              >
                Rejected
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
                <p className="text-[#F8FAFC] font-medium">About Bounty Payment Processing</p>
                <p className="text-[#94A3B8] text-sm mt-1">
                  {statusFilter === 'approved' && 'These bounty payments have been approved by organizations and are ready to be processed. Click "Process Payment" to transfer funds to researchers.'}
                  {statusFilter === 'completed' && 'These bounty payments have been successfully processed and funds have been transferred to researchers.'}
                  {statusFilter === 'pending' && 'These bounty payments are waiting for organization approval.'}
                  {statusFilter === 'rejected' && 'These bounty payments were rejected by organizations.'}
                </p>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by report number, researcher, organization..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-[#1E293B] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading approved bounty payments...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-[#1E293B] border border-[#DC2626] rounded-lg p-4 mb-6">
              <p className="text-[#DC2626]">Failed to load bounty payments. Please try again.</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && filteredPayments.length === 0 && (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
              <svg className="w-16 h-16 text-[#64748B] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
                No {statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Bounty Payments
              </h3>
              <p className="text-[#94A3B8]">
                {searchQuery
                  ? 'No payments match your search criteria.'
                  : `There are no ${statusFilter} bounty payments at this time.`}
              </p>
            </div>
          )}

          {/* Bounty Payments List */}
          {!isLoading && !error && filteredPayments.length > 0 && (
            <div className="space-y-4">
              {filteredPayments.map((payment) => (
                <div
                  key={payment.payment_id}
                  className="bg-[#1E293B] border border-[#334155] rounded-lg p-6 hover:border-[#3B82F6] transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Left Section: Report & Details */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-[#F8FAFC]">
                          {payment.report?.report_number || 'N/A'}
                        </h3>
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getSeverityColor(payment.report?.severity)}`}>
                          {payment.report?.severity || 'N/A'}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getStatusColor(payment.status)}`}>
                          {getStatusLabel(payment.status)}
                        </span>
                      </div>
                      
                      <p className="text-[#94A3B8] mb-4 line-clamp-1">
                        {payment.report?.title || 'No title'}
                      </p>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-[#64748B] mb-1">Researcher</p>
                          <p className="text-[#F8FAFC] font-medium">{payment.researcher?.username || 'Unknown'}</p>
                        </div>
                        <div>
                          <p className="text-[#64748B] mb-1">Organization</p>
                          <p className="text-[#F8FAFC] font-medium">{payment.organization?.name || 'Unknown'}</p>
                        </div>
                        <div>
                          <p className="text-[#64748B] mb-1">Approved At</p>
                          <p className="text-[#F8FAFC]">
                            {payment.approved_at ? new Date(payment.approved_at).toLocaleDateString() : 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-[#64748B] mb-1">Transaction ID</p>
                          <p className="text-[#F8FAFC] font-mono text-xs">{payment.transaction_id}</p>
                        </div>
                      </div>
                    </div>

                    {/* Right Section: Payment Amounts & Action */}
                    <div className="flex flex-col items-end gap-4 min-w-[240px]">
                      <div className="text-right space-y-2 w-full">
                        <div className="flex justify-between items-center">
                          <span className="text-[#64748B] text-sm">Researcher Amount:</span>
                          <span className="text-[#10B981] font-bold text-lg">
                            {payment.researcher_amount.toLocaleString()} ETB
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-[#64748B] text-sm">Platform Commission:</span>
                          <span className="text-[#3B82F6] font-semibold">
                            {payment.commission_amount.toLocaleString()} ETB
                          </span>
                        </div>
                        <div className="border-t border-[#334155] pt-2 flex justify-between items-center">
                          <span className="text-[#94A3B8] text-sm">Total:</span>
                          <span className="text-[#F8FAFC] font-bold text-lg">
                            {payment.total_amount.toLocaleString()} ETB
                          </span>
                        </div>
                      </div>

                      {statusFilter === 'approved' && (
                        <Button
                          variant="primary"
                          size="md"
                          onClick={() => handleProcessPayment(payment.payment_id)}
                          disabled={processingId === payment.payment_id || processPaymentMutation.isLoading}
                          className="w-full"
                        >
                          {processingId === payment.payment_id ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Processing...
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Process Payment
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
