'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function FinanceDashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finance Dashboard"
          subtitle="Payment and payout overview"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Finance Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                Finance Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Manage payments, payouts, and financial operations.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Payment and payout overview for finance staff to process bounty payments and researcher withdrawals.
              </p>
            </div>
          </section>

          <div className="mt-6 rounded-2xl border border-[#e6ddd4] bg-white p-6 text-center">
            <p className="text-sm text-[#6d6760]">
              Finance dashboard content coming soon
            </p>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
