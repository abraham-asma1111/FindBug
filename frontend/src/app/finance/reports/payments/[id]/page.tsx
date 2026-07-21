'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function PaymentReportDetailPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const params = useParams();
  const paymentId = params.id as string;

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: payment, isLoading, error } = useApiQuery<any>({
    endpoint: `/finance/reports/payments?format=json`,
  });

  const paymentDetail = payment?.data?.find((p: any) => p.payment_id === paymentId);

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Payment Report Detail"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <section className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
              <svg className="animate-spin h-12 w-12 text-[#3B82F6] mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-[#94A3B8]">Loading payment details...</p>
            </section>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (!paymentDetail || error) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Payment Report Detail"
            subtitle="Not Found"
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <section className="bg-[#1E293B] rounded-lg border border-[#DC2626] p-8 text-center">
              <svg className="w-16 h-16 text-[#DC2626] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">Payment Not Found</h3>
              <p className="text-[#94A3B8] mb-4">The payment report you're looking for could not be found.</p>
              <Button variant="primary" size="md" onClick={() => router.push('/finance/reports')}>
                Back to Reports
              </Button>
            </section>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user && (
        <PortalShell
          user={user}
          title="Payment Report Detail"
          subtitle={`Payment ID: ${paymentId}`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <Button
            variant="secondary"
            size="sm"
            onClick={() => router.push('/finance/reports')}
            className="mb-6"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Reports
          </Button>

          <article className="bg-[#1E293B] border border-[#334155] rounded-lg overflow-hidden">
            {/* Header with Amount Summary */}
            <header className="bg-gradient-to-r from-[#0F172A] to-[#1E293B] border-b border-[#334155] px-8 py-6">
              <dl className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <section>
                  <dt className="text-[#64748B] text-sm font-medium mb-2">Total Amount</dt>
                  <dd className="text-[#10B981] text-3xl font-bold">{paymentDetail.total_amount?.toLocaleString()} ETB</dd>
                </section>
                <section>
                  <dt className="text-[#64748B] text-sm font-medium mb-2">Researcher Amount</dt>
                  <dd className="text-[#F8FAFC] text-3xl font-bold">{paymentDetail.researcher_amount?.toLocaleString()} ETB</dd>
                </section>
                <section>
                  <dt className="text-[#64748B] text-sm font-medium mb-2">Commission</dt>
                  <dd className="text-[#F8FAFC] text-3xl font-bold">{paymentDetail.commission_amount?.toLocaleString()} ETB</dd>
                </section>
              </dl>
            </header>

            {/* Main Content */}
            <section className="p-8 space-y-8">
              {/* Payment Information */}
              <section>
                <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Payment Information</h2>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Payment ID</dt>
                    <dd className="text-[#F8FAFC] font-medium">{paymentDetail.payment_id}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Transaction ID</dt>
                    <dd className="text-[#F8FAFC] font-medium">{paymentDetail.transaction_id || 'N/A'}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Status</dt>
                    <dd>
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                        paymentDetail.status === 'completed' || paymentDetail.status === 'approved' || paymentDetail.status === 'paid'
                          ? 'bg-[#10B981]/10 text-[#10B981]'
                          : paymentDetail.status === 'pending'
                          ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                          : 'bg-[#EF4444]/10 text-[#EF4444]'
                      }`}>
                        {paymentDetail.status}
                      </span>
                    </dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Payment Method</dt>
                    <dd className="text-[#F8FAFC] font-medium">{paymentDetail.payment_method || 'N/A'}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Created At</dt>
                    <dd className="text-[#F8FAFC] font-medium">
                      {new Date(paymentDetail.created_at).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Completed At</dt>
                    <dd className="text-[#F8FAFC] font-medium">
                      {paymentDetail.completed_at 
                        ? new Date(paymentDetail.completed_at).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })
                        : 'Not completed'
                      }
                    </dd>
                  </section>
                </dl>
              </section>

              {/* Parties Involved */}
              <section>
                <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Parties Involved</h2>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Researcher</dt>
                    <dd className="text-[#F8FAFC] text-lg font-medium">{paymentDetail.researcher}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Organization</dt>
                    <dd className="text-[#F8FAFC] text-lg font-medium">{paymentDetail.organization}</dd>
                  </section>
                </dl>
              </section>

              {/* Related Report */}
              <section>
                <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Related Report</h2>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Report Title</dt>
                    <dd className="text-[#F8FAFC] font-medium">{paymentDetail.report_title}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Severity</dt>
                    <dd>
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold ${
                        paymentDetail.severity === 'critical'
                          ? 'bg-[#EF4444]/10 text-[#EF4444]'
                          : paymentDetail.severity === 'high'
                          ? 'bg-[#F97316]/10 text-[#F97316]'
                          : paymentDetail.severity === 'medium'
                          ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                          : 'bg-[#3B82F6]/10 text-[#3B82F6]'
                      }`}>
                        {paymentDetail.severity}
                      </span>
                    </dd>
                  </section>
                </dl>
              </section>
            </section>
          </article>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
