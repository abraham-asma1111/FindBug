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

const BOUNTY_STATUS_OPTIONS = [
  { value: 'approved',  label: 'Awaiting Processing' },
  { value: 'completed', label: 'Processed' },
  { value: 'pending',   label: 'Pending Approval' },
  { value: 'rejected',  label: 'Rejected' },
];

const PAYOUT_STATUS_OPTIONS = [
  { value: 'pending',    label: 'Requested' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed',  label: 'Completed' },
];

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-[#DC2626]',
  high:     'bg-[#F59E0B]',
  medium:   'bg-[#3B82F6]',
  low:      'bg-[#10B981]',
};

const STATUS_STYLES: Record<string, string> = {
  approved:   'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30',
  completed:  'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30',
  processing: 'bg-[#3B82F6]/20 text-[#3B82F6] border border-[#3B82F6]/30',
  pending:    'bg-[#94A3B8]/20 text-[#94A3B8] border border-[#94A3B8]/30',
  requested:  'bg-[#94A3B8]/20 text-[#94A3B8] border border-[#94A3B8]/30',
  rejected:   'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30',
  failed:     'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30',
};

const STATUS_LABELS: Record<string, string> = {
  approved:   'Awaiting Processing',
  completed:  'Processed',
  pending:    'Pending',
  requested:  'Requested',
  processing: 'Processing',
  rejected:   'Rejected',
  failed:     'Failed',
};

export default function FinancePaymentsPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const activeTab = (searchParams.get('tab') || 'bounty-payments') as 'bounty-payments' | 'payouts';
  const statusFilter = searchParams.get('status') || (activeTab === 'bounty-payments' ? 'approved' : 'pending');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const bountyEndpoint = `/bounty-payments?status_filter=${statusFilter}`;
  const { data: bountyData, isLoading: bountyLoading } = useApiQuery<any>({
    endpoint: bountyEndpoint,
    enabled: activeTab === 'bounty-payments',
  });

  const payoutEndpoint = `/wallet/payouts?status=${statusFilter}`;
  const { data: payoutData, isLoading: payoutLoading } = useApiQuery<any>({
    endpoint: payoutEndpoint,
    enabled: activeTab === 'payouts',
  });

  const processPaymentMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      showToast('Payment processed successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: [bountyEndpoint] });
      setProcessingId(null);
    },
    onError: (error: any) => {
      showToast(error?.message || 'Failed to process payment', 'error');
      setProcessingId(null);
    },
  });

  const approvePayoutMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      showToast('Payout approved successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: [payoutEndpoint] });
      setProcessingId(null);
    },
    onError: (error: any) => {
      showToast(error?.message || 'Failed to approve payout', 'error');
      setProcessingId(null);
    },
  });

  const bountyPayments: BountyPayment[] = bountyData?.bounty_payments || [];
  const payouts: Payout[] = payoutData?.payouts || [];

  const filteredBountyPayments = bountyPayments.filter((p) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.report?.report_number?.toLowerCase().includes(q) ||
      p.report?.title?.toLowerCase().includes(q) ||
      p.researcher?.username?.toLowerCase().includes(q) ||
      p.organization?.name?.toLowerCase().includes(q)
    );
  });

  const filteredPayouts = payouts.filter((p) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.researcher_name?.toLowerCase().includes(q) ||
      p.id?.toLowerCase().includes(q) ||
      p.payment_method?.toLowerCase().includes(q)
    );
  });

  const handleProcessPayment = async (paymentId: string) => {
    if (!confirm('Process this payment? This will transfer funds to the researcher.')) return;
    setProcessingId(paymentId);
    await processPaymentMutation.mutateAsync({ endpoint: `/bounty-payments/process/${paymentId}`, data: {} });
  };

  const handleApprovePayout = async (payoutId: string) => {
    if (!confirm('Approve this payout? This will initiate the payment process.')) return;
    setProcessingId(payoutId);
    await approvePayoutMutation.mutateAsync({ endpoint: `/wallet/payouts/${payoutId}/approve`, data: {} });
  };

  const makeTabHref = (tab: string) =>
    `/finance/payments?tab=${tab}&status=${tab === 'bounty-payments' ? 'approved' : 'pending'}`;

  const makeStatusHref = (status: string) =>
    `/finance/payments?tab=${activeTab}&status=${status}`;

  const isLoading = activeTab === 'bounty-payments' ? bountyLoading : payoutLoading;
  const filteredItems = activeTab === 'bounty-payments' ? filteredBountyPayments : filteredPayouts;
  const statusOptions = activeTab === 'bounty-payments' ? BOUNTY_STATUS_OPTIONS : PAYOUT_STATUS_OPTIONS;

  const totalCommission = activeTab === 'bounty-payments' 
    ? filteredBountyPayments.reduce((sum, p) => sum + (p.commission_amount || 0), 0)
    : 0;

  const totalPayout = activeTab === 'payouts'
    ? filteredPayouts.reduce((sum, p) => sum + (p.amount || 0), 0)
    : 0;

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payments"
          subtitle="Bounty payment processing and payouts"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Hero */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 sm:p-8 shadow-sm">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Finance Operations
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Payments & Payouts
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Process bounty payments and manage researcher withdrawal requests.
              </p>
            </div>
          </section>

          {/* Tab + Controls Row */}
          <div className="mt-4 bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">

            {/* Tabs */}
            <div className="flex border-b border-[#334155]">
              <Link href={makeTabHref('bounty-payments')} className="flex-1">
                <button className={`w-full py-3.5 text-sm font-semibold transition-colors ${
                  activeTab === 'bounty-payments'
                    ? 'bg-[#0F172A]/40 text-[#F8FAFC] border-b-2 border-[#3B82F6]'
                    : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#0F172A]/20'
                }`}>
                  Bounty Payments
                </button>
              </Link>
              <Link href={makeTabHref('payouts')} className="flex-1">
                <button className={`w-full py-3.5 text-sm font-semibold transition-colors ${
                  activeTab === 'payouts'
                    ? 'bg-[#0F172A]/40 text-[#F8FAFC] border-b-2 border-[#3B82F6]'
                    : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#0F172A]/20'
                }`}>
                  Payouts
                </button>
              </Link>
            </div>

            {/* Filter + Search Row */}
            <div className="flex flex-col xl:flex-row items-center justify-between gap-4 p-4">
              {/* Status Dropdown */}
              <div className="flex items-center gap-3 bg-[#0F172A] p-2 rounded-lg border border-[#334155]">
                <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider pl-2">Status:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => router.push(makeStatusHref(e.target.value))}
                  className="rounded-md border border-[#334155] bg-[#1E293B] px-3 py-1.5 text-sm font-medium text-[#F8FAFC] focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6] focus:outline-none transition-all cursor-pointer min-w-[180px]"
                >
                  {statusOptions.map(({ value, label }) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Search */}
              <div className="relative w-full xl:w-72">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-[#64748B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder={activeTab === 'bounty-payments' ? 'Search payments...' : 'Search payouts...'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-[#334155] rounded-lg bg-[#0F172A] text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] focus:border-[#3B82F6] text-sm transition-colors"
                />
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="mt-3">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                <p className="text-[#94A3B8]">Loading {activeTab === 'bounty-payments' ? 'payments' : 'payouts'}…</p>
              </div>
            ) : filteredItems.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
                <svg className="w-12 h-12 text-[#475569] mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-[#64748B] text-sm">
                  {searchQuery ? 'No items match your search.' : `No ${statusFilter} ${activeTab === 'bounty-payments' ? 'payments' : 'payouts'} found.`}
                </p>
              </div>

            ) : activeTab === 'bounty-payments' ? (
              // ── Bounty Payments List ─────────────────────────────────────────
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden divide-y divide-[#334155]">
                {filteredBountyPayments.map((payment, idx) => (
                  <div key={payment.payment_id} className={`p-5 sm:p-6 hover:bg-[#0F172A]/30 transition-colors ${idx % 2 === 1 ? 'bg-[#0F172A]/20' : ''}`}>
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                      {/* Left: info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1.5">
                          {payment.report?.report_number && (
                            <span className="text-xs font-mono text-[#64748B]">#{payment.report.report_number}</span>
                          )}
                          {payment.report?.severity && (
                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${SEVERITY_COLORS[payment.report.severity.toLowerCase()] || 'bg-[#64748B]'} text-white`}>
                              {payment.report.severity}
                            </span>
                          )}
                          <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${STATUS_STYLES[payment.status] || 'bg-[#94A3B8]/20 text-[#94A3B8]'}`}>
                            {STATUS_LABELS[payment.status] || payment.status}
                          </span>
                        </div>
                        <p className="font-semibold text-[#F8FAFC] truncate mb-1">
                          {payment.report?.title || 'No title'}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-[#64748B] flex-wrap">
                          <span>👤 {payment.researcher?.username || 'Unknown'}</span>
                          <span>🏢 {payment.organization?.name || 'Unknown'}</span>
                          {payment.approved_at && (
                            <span>🗓 {new Date(payment.approved_at).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>

                      {/* Right: amounts + action */}
                      <div className="flex flex-row lg:flex-col items-center lg:items-end gap-4 lg:gap-2 shrink-0">
                        <div className="text-right">
                          <div className="flex items-center gap-4 text-sm mb-1">
                            <span className="text-[#64748B]">Researcher</span>
                            <span className="font-bold text-[#10B981]">{payment.researcher_amount?.toLocaleString()} ETB</span>
                          </div>
                          <div className="flex items-center gap-4 text-sm mb-1">
                            <span className="text-[#64748B]">Commission</span>
                            <span className="font-semibold text-[#3B82F6]">{payment.commission_amount?.toLocaleString()} ETB</span>
                          </div>
                          <div className="flex items-center gap-4 text-sm pt-1 border-t border-[#334155]">
                            <span className="text-[#94A3B8]">Total</span>
                            <span className="font-bold text-[#F8FAFC]">{payment.total_amount?.toLocaleString()} ETB</span>
                          </div>
                        </div>

                        {statusFilter === 'approved' && (
                          <button
                            onClick={() => handleProcessPayment(payment.payment_id)}
                            disabled={processingId === payment.payment_id}
                            className="px-4 py-2 text-sm font-semibold rounded-lg bg-[#3B82F6] hover:bg-[#2563EB] text-white disabled:opacity-40 transition-colors flex items-center gap-2"
                          >
                            {processingId === payment.payment_id ? (
                              <><svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> Processing…</>
                            ) : (
                              <><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg> Process</>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

            ) : (
              // ── Payouts List ─────────────────────────────────────────────────
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden divide-y divide-[#334155]">
                {filteredPayouts.map((payout, idx) => (
                  <div key={payout.id} className={`p-5 sm:p-6 hover:bg-[#0F172A]/30 transition-colors ${idx % 2 === 1 ? 'bg-[#0F172A]/20' : ''}`}>
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                      {/* Left: info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1.5">
                          <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${STATUS_STYLES[payout.status] || 'bg-[#94A3B8]/20 text-[#94A3B8]'}`}>
                            {STATUS_LABELS[payout.status] || payout.status}
                          </span>
                        </div>
                        <p className="font-semibold text-[#F8FAFC] mb-1">{payout.researcher_name || 'Unknown Researcher'}</p>
                        <div className="flex items-center gap-3 text-xs text-[#64748B] flex-wrap">
                          <span>💳 {payout.payment_method?.replace('_', ' ') || 'N/A'}</span>
                          {payout.requested_at && <span>🗓 {new Date(payout.requested_at).toLocaleDateString()}</span>}
                          <span className="font-mono">{payout.id.slice(0, 12)}…</span>
                        </div>
                      </div>

                      {/* Right: amount + action */}
                      <div className="flex items-center gap-4 shrink-0">
                        <div className="text-right">
                          <p className="text-xs text-[#64748B]">Amount</p>
                          <p className="text-xl font-bold text-[#10B981]">{payout.amount?.toLocaleString()} ETB</p>
                        </div>

                        {statusFilter === 'pending' && (
                          <button
                            onClick={() => handleApprovePayout(payout.id)}
                            disabled={processingId === payout.id}
                            className="px-4 py-2 text-sm font-semibold rounded-lg bg-[#10B981] hover:bg-[#059669] text-white disabled:opacity-40 transition-colors flex items-center gap-2"
                          >
                            {processingId === payout.id ? (
                              <><svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> Approving…</>
                            ) : (
                              <><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg> Approve</>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <p className="text-xs text-[#64748B]">
              Showing {filteredItems.length} {activeTab === 'bounty-payments' ? 'payment' : 'payout'}{filteredItems.length !== 1 ? 's' : ''}
              {statusFilter !== 'all' ? ` · status: ${statusFilter}` : ''}
            </p>
            {filteredItems.length > 0 && (
              <p className="text-sm font-semibold text-[#F8FAFC] bg-[#1E293B] border border-[#334155] px-3 py-1.5 rounded-md">
                {activeTab === 'bounty-payments' ? (
                  <>Total Commission: <span className="text-[#3B82F6]">{totalCommission.toLocaleString()} ETB</span></>
                ) : (
                  <>Total Payout: <span className="text-[#10B981]">{totalPayout.toLocaleString()} ETB</span></>
                )}
              </p>
            )}
          </div>

        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
