'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function PayoutReportDetailPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const params = useParams();
  const payoutId = params.id as string;

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: payout, isLoading, error } = useApiQuery<any>({
    endpoint: `/finance/reports/payouts?format=json`,
  });

  const payoutDetail = payout?.data?.find((p: any) => p.payout_id === payoutId);

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Payout Report Detail"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <section className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
              <svg className="animate-spin h-12 w-12 text-[#3B82F6] mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-[#94A3B8]">Loading payout details...</p>
            </section>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (!payoutDetail || error) {
    return (
      <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
        {user && (
          <PortalShell
            user={user}
            title="Payout Report Detail"
            subtitle="Not Found"
            navItems={getPortalNavItems(user.role)}
            hideThemeToggle={true}
          >
            <section className="bg-[#1E293B] rounded-lg border border-[#DC2626] p-8 text-center">
              <svg className="w-16 h-16 text-[#DC2626] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">Payout Not Found</h3>
              <p className="text-[#94A3B8] mb-4">The payout report you're looking for could not be found.</p>
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
          title="Payout Report Detail"
          subtitle={`Payout ID: ${payoutId}`}
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
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <section>
                  <dt className="text-[#64748B] text-sm font-medium mb-2">Payout Amount</dt>
                  <dd className="text-[#10B981] text-3xl font-bold">{payoutDetail.amount?.toLocaleString()} ETB</dd>
                </section>
                <section>
                  <dt className="text-[#64748B] text-sm font-medium mb-2">Status</dt>
                  <dd>
                    <span className={`inline-flex px-4 py-2 rounded-full text-lg font-semibold ${
                      payoutDetail.status === 'completed' || payoutDetail.status === 'approved' || payoutDetail.status === 'paid'
                        ? 'bg-[#10B981]/10 text-[#10B981]'
                        : payoutDetail.status === 'pending'
                        ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                        : 'bg-[#EF4444]/10 text-[#EF4444]'
                    }`}>
                      {payoutDetail.status}
                    </span>
                  </dd>
                </section>
              </dl>
            </header>

            {/* Main Content */}
            <section className="p-8 space-y-8">
              {/* Payout Information */}
              <section>
                <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Payout Information</h2>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Payout ID</dt>
                    <dd className="text-[#F8FAFC] font-medium">{payoutDetail.payout_id}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Payment Method</dt>
                    <dd className="text-[#F8FAFC] font-medium">{payoutDetail.payment_method || 'N/A'}</dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Created At</dt>
                    <dd className="text-[#F8FAFC] font-medium">
                      {new Date(payoutDetail.created_at).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </dd>
                  </section>
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Processed At</dt>
                    <dd className="text-[#F8FAFC] font-medium">
                      {payoutDetail.processed_at 
                        ? new Date(payoutDetail.processed_at).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })
                        : 'Not processed yet'
                      }
                    </dd>
                  </section>
                </dl>
              </section>

              {/* Researcher Information */}
              <section>
                <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Researcher Information</h2>
                <dl className="grid grid-cols-1 gap-6">
                  <section>
                    <dt className="text-[#64748B] text-sm mb-1.5">Researcher Name</dt>
                    <dd className="text-[#F8FAFC] text-lg font-medium">{payoutDetail.researcher}</dd>
                  </section>
                </dl>
              </section>

              {/* Additional Details */}
              {payoutDetail.notes && (
                <section>
                  <h2 className="text-lg font-semibold text-[#F8FAFC] mb-6 pb-2 border-b border-[#334155]">Additional Notes</h2>
                  <p className="text-[#E2E8F0] leading-relaxed">{payoutDetail.notes}</p>
                </section>
              )}
            </section>
          </article>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
