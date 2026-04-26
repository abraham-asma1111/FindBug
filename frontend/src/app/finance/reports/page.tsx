'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function FinanceReportsPage() {
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
          title="Financial Reports"
          subtitle="View financial analytics and reports"
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
                Financial Reports
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Revenue & Analytics
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Comprehensive financial reports and analytics for platform operations.
              </p>
            </div>
          </section>

          {/* Financial Summary */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Revenue
              </p>
              <p className="mt-2 text-3xl font-bold text-[#10B981]">
                {stats?.total_revenue?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Payouts
              </p>
              <p className="mt-2 text-3xl font-bold text-[#EF4444]">
                {stats?.total_payouts?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Commission Earned
              </p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">
                {stats?.commission_earned?.toLocaleString() || 0} ETB
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Active Subscriptions
              </p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">
                {stats?.active_subscriptions || 0}
              </p>
            </div>
          </div>

          {/* Report Actions */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Generate Reports</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="font-semibold text-[#F8FAFC] mb-2">Payment Report</h3>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Export detailed payment transactions and history
                </p>
                <Button 
                  variant="primary" 
                  size="sm"
                  className="bg-[#EF2330] hover:bg-[#DC2026]"
                >
                  Export CSV
                </Button>
              </div>
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="font-semibold text-[#F8FAFC] mb-2">Payout Report</h3>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Export researcher payout transactions
                </p>
                <Button 
                  variant="primary" 
                  size="sm"
                  className="bg-[#EF2330] hover:bg-[#DC2026]"
                >
                  Export CSV
                </Button>
              </div>
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="font-semibold text-[#F8FAFC] mb-2">Revenue Report</h3>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Export revenue and commission breakdown
                </p>
                <Button 
                  variant="primary" 
                  size="sm"
                  className="bg-[#EF2330] hover:bg-[#DC2026]"
                >
                  Export CSV
                </Button>
              </div>
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="font-semibold text-[#F8FAFC] mb-2">Subscription Report</h3>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Export organization subscription data
                </p>
                <Button 
                  variant="primary" 
                  size="sm"
                  className="bg-[#EF2330] hover:bg-[#DC2026]"
                >
                  Export CSV
                </Button>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
