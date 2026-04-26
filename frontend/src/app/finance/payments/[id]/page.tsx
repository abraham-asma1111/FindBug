'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, ChevronLeft, CheckCircle, XCircle, DollarSign, User, FileText, Calendar } from 'lucide-react';
import Link from 'next/link';

interface PaymentDetail {
  id: string;
  amount: number;
  status: string;
  payment_type: string;
  created_at: string;
  processed_at: string | null;
  researcher_id: string;
  researcher_name: string;
  researcher_email: string;
  report_id: string | null;
  report_number: string | null;
  report_title: string | null;
  organization_id: string | null;
  organization_name: string | null;
  notes: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
}

const statusColors: Record<string, string> = {
  pending: 'bg-[#F59E0B] text-white',
  approved: 'bg-[#10B981] text-white',
  rejected: 'bg-[#EF4444] text-white',
  completed: 'bg-[#3B82F6] text-white',
  failed: 'bg-[#EF4444] text-white',
};

export default function PaymentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const paymentId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const [notes, setNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: payment, isLoading, error, refetch } = useApiQuery<PaymentDetail>({
    endpoint: `/payments/${paymentId}`,
  });

  useEffect(() => {
    if (payment) {
      setNotes(payment.notes || '');
    }
  }, [payment]);

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/payments'] });
      alert('Payment approved successfully');
    },
    onError: (error: any) => {
      alert(`Failed to approve payment: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/payments'] });
      alert('Payment rejected');
      setRejectionReason('');
    },
    onError: (error: any) => {
      alert(`Failed to reject payment: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const handleApprove = () => {
    if (!confirm('Are you sure you want to approve this payment?')) return;
    approveMutation.mutate({
      endpoint: `/payments/${paymentId}/approve`,
      notes,
    });
  };

  const handleReject = () => {
    if (!rejectionReason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }
    if (!confirm('Are you sure you want to reject this payment?')) return;
    rejectMutation.mutate({
      endpoint: `/payments/${paymentId}/reject`,
      rejection_reason: rejectionReason,
    });
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Payment Details"
          subtitle="Review and process payment"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/finance/payments" className="text-[#3B82F6] hover:underline text-sm">
              Payments
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">Payment Details</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading payment...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load payment</p>
              </div>
            </div>
          ) : payment ? (
            <div className="space-y-6">
              {/* Payment Header */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                      Payment to {payment.researcher_name}
                    </h2>
                    <div className="flex items-center gap-3 text-sm text-[#94A3B8]">
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        {payment.amount.toLocaleString()} ETB
                      </span>
                      <span>•</span>
                      <span>Created {new Date(payment.created_at).toLocaleDateString()}</span>
                      {payment.organization_name && (
                        <>
                          <span>•</span>
                          <span>Organization: {payment.organization_name}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColors[payment.status] || 'bg-[#94A3B8] text-white'}`}>
                      {payment.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payment Details */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Payment Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Payment Type</p>
                    <p className="text-[#F8FAFC] font-medium">{payment.payment_type}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Amount</p>
                    <p className="text-[#F8FAFC] font-medium text-lg">{payment.amount.toLocaleString()} ETB</p>
                  </div>
                  {payment.report_number && (
                    <div>
                      <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Report</p>
                      <Link href={`/triage/reports/${payment.report_id}`} className="text-[#3B82F6] hover:underline">
                        {payment.report_number}
                      </Link>
                    </div>
                  )}
                  {payment.report_title && (
                    <div>
                      <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Report Title</p>
                      <p className="text-[#F8FAFC] font-medium">{payment.report_title}</p>
                    </div>
                  )}
                </div>

                {/* Researcher Info */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Researcher Information
                  </h4>
                  <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                    <p className="text-[#F8FAFC] font-medium mb-1">{payment.researcher_name}</p>
                    <p className="text-sm text-[#94A3B8]">{payment.researcher_email}</p>
                  </div>
                </div>

                {/* Approval Info */}
                {payment.approved_by && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Approval Information</h4>
                    <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] mb-1">Approved by: {payment.approved_by}</p>
                      <p className="text-sm text-[#94A3B8]">
                        {payment.approved_at ? new Date(payment.approved_at).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                )}

                {/* Rejection Reason */}
                {payment.rejection_reason && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Rejection Reason</h4>
                    <div className="p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg">
                      <p className="text-[#F8FAFC]">{payment.rejection_reason}</p>
                    </div>
                  </div>
                )}

                {/* Notes */}
                {payment.notes && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Notes</h4>
                    <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] whitespace-pre-wrap">{payment.notes}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Form (Only for Pending) */}
              {payment.status === 'pending' && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Process Payment</h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Notes (Optional)
                    </label>
                    <Textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      placeholder="Add any notes about this payment..."
                    />
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={handleApprove}
                      disabled={approveMutation.isLoading}
                      className="gap-2 bg-[#10B981] hover:bg-[#059669]"
                    >
                      <CheckCircle className="w-4 h-4" />
                      {approveMutation.isLoading ? 'Approving...' : 'Approve Payment'}
                    </Button>

                    <Button
                      onClick={() => {
                        const reason = prompt('Enter rejection reason:');
                        if (reason) {
                          setRejectionReason(reason);
                          setTimeout(() => handleReject(), 100);
                        }
                      }}
                      disabled={rejectMutation.isLoading}
                      variant="outline"
                      className="gap-2 border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white"
                    >
                      <XCircle className="w-4 h-4" />
                      {rejectMutation.isLoading ? 'Rejecting...' : 'Reject Payment'}
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
                      <p className="text-[#F8FAFC] font-medium">Payment Created</p>
                      <p className="text-sm text-[#94A3B8]">{new Date(payment.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  {payment.approved_at && (
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#10B981]"></div>
                      <div>
                        <p className="text-[#F8FAFC] font-medium">Payment Approved</p>
                        <p className="text-sm text-[#94A3B8]">{new Date(payment.approved_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                  {payment.processed_at && (
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#10B981]"></div>
                      <div>
                        <p className="text-[#F8FAFC] font-medium">Payment Processed</p>
                        <p className="text-sm text-[#94A3B8]">{new Date(payment.processed_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Back Button */}
              <div className="flex gap-3">
                <Link href="/finance/payments">
                  <Button variant="outline" className="gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Payments
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
