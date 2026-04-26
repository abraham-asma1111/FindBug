'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';

export default function FinanceAnalyticsPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: stats } = useApiQuery<any>({
    endpoint: '/finance/statistics',
  });

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Analytics"
          subtitle="Financial analytics and insights"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Finance Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero Section */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Financial Analytics
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Platform Financial Insights
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Real-time analytics and trends for platform financial operations.
              </p>
            </div>
          </section>

          {/* Key Metrics */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Monthly Revenue
              </p>
              <p className="mt-2 text-3xl font-bold text-[#10B981]">
                {stats?.monthly_revenue?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Monthly Payouts
              </p>
              <p className="mt-2 text-3xl font-bold text-[#EF4444]">
                {stats?.monthly_payouts?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Avg Payment Time
              </p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">
                {stats?.avg_payment_time || 0} days
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Avg Payout Time
              </p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">
                {stats?.avg_payout_time || 0} days
              </p>
            </div>
          </div>

          {/* Payment Status Breakdown */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payment Status</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Pending
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {stats?.payment_status?.pending || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Approved
                </p>
                <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                  {stats?.payment_status?.approved || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Completed
                </p>
                <p className="mt-2 text-2xl font-bold text-[#10B981]">
                  {stats?.payment_status?.completed || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Rejected
                </p>
                <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                  {stats?.payment_status?.rejected || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Payout Status Breakdown */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Payout Status</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Requested
                </p>
                <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                  {stats?.payout_status?.requested || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Processing
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {stats?.payout_status?.processing || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Completed
                </p>
                <p className="mt-2 text-2xl font-bold text-[#10B981]">
                  {stats?.payout_status?.completed || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Rejected
                </p>
                <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                  {stats?.payout_status?.rejected || 0}
                </p>
              </div>
            </div>
          </div>

          {/* KYC Status */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">KYC Verification</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Pending
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {stats?.kyc_status?.pending || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Approved
                </p>
                <p className="mt-2 text-2xl font-bold text-[#10B981]">
                  {stats?.kyc_status?.approved || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Rejected
                </p>
                <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                  {stats?.kyc_status?.rejected || 0}
                </p>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
