'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, ChevronLeft, CheckCircle, XCircle, DollarSign, User, CreditCard, Calendar } from 'lucide-react';
import Link from 'next/link';

interface PayoutDetail {
  id: string;
  amount: number;
  status: string;
  requested_at: string;
  processed_at: string | null;
  completed_at: string | null;
  researcher_id: string;
  researcher_name: string;
  researcher_email: string;
  payment_method: string;
  payment_details: any;
  notes: string | null;
  processed_by: string | null;
  failure_reason: string | null;
}

const statusColors: Record<string, string> = {
  requested: 'bg-[#F59E0B] text-white',
  processing: 'bg-[#3B82F6] text-white',
  completed: 'bg-[#10B981] text-white',
  failed: 'bg-[#EF4444] text-white',
  cancelled: 'bg-[#94A3B8] text-white',
};

export default function PayoutDetailPage() {
  const params = useParams();
  const payoutId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const [notes, setNotes] = useState('');

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: payout, isLoading, error, refetch } = useApiQuery<PayoutDetail>({
    endpoint: `/wallet/payouts/${payoutId}`,
  });

  useEffect(() => {
    if (payout) {
      setNotes(payout.notes || '');
    }
  }, [payout]);

  const processMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/wallet/payouts'] });
      alert('Payout processing started');
    },
    onError: (error: any) => {
      alert(`Failed to process payout: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const completeMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/wallet/payouts'] });
      alert('Payout marked as completed');
    },
    onError: (error: any) => {
      alert(`Failed to complete payout: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const failMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/wallet/payouts'] });
      alert('Payout marked as failed');
    },
    onError: (error: any) => {
      alert(`Failed to mark payout as failed: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const handleProcess = () => {
    if (!confirm('Start processing this payout?')) return;
    processMutation.mutate({
      endpoint: `/wallet/payouts/${payoutId}/process`,
      notes,
    });
  };

  const handleComplete = () => {
    if (!confirm('Mark this payout as completed?')) return;
    completeMutation.mutate({
      endpoint: `/wallet/payouts/${payoutId}/complete`,
      notes,
    });
  };

  const handleFail = () => {
    const reason = prompt('Enter failure reason:');
    if (!reason) return;
    failMutation.mutate({
      endpoint: `/wallet/payouts/${payoutId}/fail`,
      failure_reason: reason,
    });
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payout Details"
          subtitle="Review and process payout"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/finance/payouts" className="text-[#3B82F6] hover:underline text-sm">
              Payouts
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">Payout Details</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading payout...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load payout</p>
              </div>
            </div>
          ) : payout ? (
            <div className="space-y-6">
              {/* Payout Header */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                      Payout to {payout.researcher_name}
                    </h2>
                    <div className="flex items-center gap-3 text-sm text-[#94A3B8]">
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        {payout.amount.toLocaleString()} ETB
                      </span>
                      <span>•</span>
                      <span>Requested {new Date(payout.requested_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{payout.payment_method}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColors[payout.status] || 'bg-[#94A3B8] text-white'}`}>
                      {payout.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payout Details */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <CreditCard className="w-5 h-5" />
                  Payout Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Amount</p>
                    <p className="text-[#F8FAFC] font-medium text-lg">{payout.amount.toLocaleString()} ETB</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Payment Method</p>
                    <p className="text-[#F8FAFC] font-medium">{payout.payment_method}</p>
                  </div>
                </div>

                {/* Researcher Info */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Researcher Information
                  </h4>
                  <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                    <p className="text-[#F8FAFC] font-medium mb-1">{payout.researcher_name}</p>
                    <p className="text-sm text-[#94A3B8]">{payout.researcher_email}</p>
                  </div>
                </div>

                {/* Payment Details */}
                {payout.payment_details && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Payment Details</h4>
                    <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <pre className="text-sm text-[#F8FAFC] whitespace-pre-wrap">
                        {JSON.stringify(payout.payment_details, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Processing Info */}
                {payout.processed_by && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Processing Information</h4>
                    <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] mb-1">Processed by: {payout.processed_by}</p>
                      <p className="text-sm text-[#94A3B8]">
                        {payout.processed_at ? new Date(payout.processed_at).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                )}

                {/* Failure Reason */}
                {payout.failure_reason && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Failure Reason</h4>
                    <div className="p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg">
                      <p className="text-[#F8FAFC]">{payout.failure_reason}</p>
                    </div>
                  </div>
                )}

                {/* Notes */}
                {payout.notes && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Notes</h4>
                    <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] whitespace-pre-wrap">{payout.notes}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Form */}
              {(payout.status === 'requested' || payout.status === 'processing') && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Process Payout</h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Notes (Optional)
                    </label>
                    <Textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      placeholder="Add any notes about this payout..."
                    />
                  </div>

                  <div className="flex gap-3">
                    {payout.status === 'requested' && (
                      <Button
                        onClick={handleProcess}
                        disabled={processMutation.isLoading}
                        className="gap-2 bg-[#3B82F6] hover:bg-[#2563EB]"
                      >
                        <CheckCircle className="w-4 h-4" />
                        {processMutation.isLoading ? 'Processing...' : 'Start Processing'}
                      </Button>
                    )}

                    {payout.status === 'processing' && (
                      <Button
                        onClick={handleComplete}
                        disabled={completeMutation.isLoading}
                        className="gap-2 bg-[#10B981] hover:bg-[#059669]"
                      >
                        <CheckCircle className="w-4 h-4" />
                        {completeMutation.isLoading ? 'Completing...' : 'Mark as Completed'}
                      </Button>
                    )}

                    <Button
                      onClick={handleFail}
                      disabled={failMutation.isLoading}
                      variant="outline"
                      className="gap-2 border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white"
                    >
                      <XCircle className="w-4 h-4" />
                      {failMutation.isLoading ? 'Failing...' : 'Mark as Failed'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Timeline */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Timeline
                </h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#3B82F6]"></div>
                    <div>
                      <p className="text-[#F8FAFC] font-medium">Payout Requested</p>
                      <p className="text-sm text-[#94A3B8]">{new Date(payout.requested_at).toLocaleString()}</p>
                    </div>
                  </div>
                  {payout.processed_at && (
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#3B82F6]"></div>
                      <div>
                        <p className="text-[#F8FAFC] font-medium">Processing Started</p>
                        <p className="text-sm text-[#94A3B8]">{new Date(payout.processed_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                  {payout.completed_at && (
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#10B981]"></div>
                      <div>
                        <p className="text-[#F8FAFC] font-medium">Payout Completed</p>
                        <p className="text-sm text-[#94A3B8]">{new Date(payout.completed_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Back Button */}
              <div className="flex gap-3">
                <Link href="/finance/payouts">
                  <Button variant="outline" className="gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Payouts
                  </Button>
                </Link>
              </div>
            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
