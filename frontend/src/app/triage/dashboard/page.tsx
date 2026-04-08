'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function TriageDashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Triage Dashboard"
          subtitle="Queue management and validation overview"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Triage Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                Triage Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Validate and prioritize vulnerability reports.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Queue management and validation overview for triage staff to process incoming security reports.
              </p>
            </div>
          </section>

          <div className="mt-6 rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 text-center">
            <p className="text-sm text-[#6d6760]">
              Triage dashboard content coming soon
            </p>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
