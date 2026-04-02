'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import { formatCurrency } from '@/lib/portal';

export default function OrganizationDashboardPage() {
  const user = useAuthStore((state) => state.user);

  // Fetch dashboard data
  const { data: dashboardData, isLoading } = useApiQuery('/dashboard/organization', {
    enabled: !!user,
  });

  const stats = dashboardData || {
    total_programs: 0,
    active_programs: 0,
    total_reports: 0,
    pending_reports: 0,
    resolved_reports: 0,
    total_researchers: 0,
    total_bounties_paid: 0,
    pending_bounties: 0,
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Organization Dashboard"
          subtitle={`Welcome back, ${user.organization?.company_name || 'Organization'}`}
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                Organization Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Manage programs, reports, and researcher engagement.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Welcome back, {user.organization?.company_name || 'Organization'}. Track your bug bounty programs, review vulnerability reports, and monitor platform activity.
              </p>
            </div>
          </section>

          <div className="mt-6 space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Programs */}
              <Card className="bg-gradient-to-br from-[#edf5fb] to-[#faf6f1]">
                <div className="space-y-2">
                  <p className="text-sm text-[#6d6760]">Active Programs</p>
                  <p className="text-3xl font-bold text-[#2d2a26]">
                    {isLoading ? '...' : stats.active_programs}
                  </p>
                  <p className="text-xs text-[#8b8177]">
                    {stats.total_programs} total programs
                  </p>
                </div>
              </Card>

              {/* Reports */}
              <Card className="bg-gradient-to-br from-[#fff4e6] to-[#faf6f1]">
                <div className="space-y-2">
                  <p className="text-sm text-[#6d6760]">Pending Reports</p>
                  <p className="text-3xl font-bold text-[#2d2a26]">
                    {isLoading ? '...' : stats.pending_reports}
                  </p>
                  <p className="text-xs text-[#8b8177]">
                    {stats.total_reports} total reports
                  </p>
                </div>
              </Card>

              {/* Researchers */}
              <Card className="bg-gradient-to-br from-[#e6f7ed] to-[#faf6f1]">
                <div className="space-y-2">
                  <p className="text-sm text-[#6d6760]">Active Researchers</p>
                  <p className="text-3xl font-bold text-[#2d2a26]">
                    {isLoading ? '...' : stats.total_researchers}
                  </p>
                  <p className="text-xs text-[#8b8177]">
                    Participating in programs
                  </p>
                </div>
              </Card>

              {/* Bounties */}
              <Card className="bg-gradient-to-br from-[#f3e8ff] to-[#faf6f1]">
                <div className="space-y-2">
                  <p className="text-sm text-[#6d6760]">Total Bounties Paid</p>
                  <p className="text-3xl font-bold text-[#2d2a26]">
                    {isLoading ? '...' : formatCurrency(stats.total_bounties_paid)}
                  </p>
                  <p className="text-xs text-[#8b8177]">
                    {formatCurrency(stats.pending_bounties)} pending
                  </p>
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a
                  href="/organization/programs"
                  className="block p-4 rounded-xl border border-[#e6ddd4] hover:border-[#d4c5b3] transition-colors"
                >
                  <p className="font-semibold text-[#2d2a26] mb-1">Manage Programs</p>
                  <p className="text-sm text-[#6d6760]">Create and manage bug bounty programs</p>
                </a>

                <a
                  href="/organization/reports"
                  className="block p-4 rounded-xl border border-[#e6ddd4] hover:border-[#d4c5b3] transition-colors"
                >
                  <p className="font-semibold text-[#2d2a26] mb-1">Review Reports</p>
                  <p className="text-sm text-[#6d6760]">Review and validate vulnerability reports</p>
                </a>

                <a
                  href="/organization/analytics"
                  className="block p-4 rounded-xl border border-[#e6ddd4] hover:border-[#d4c5b3] transition-colors"
                >
                  <p className="font-semibold text-[#2d2a26] mb-1">View Analytics</p>
                  <p className="text-sm text-[#6d6760]">Track program performance and metrics</p>
                </a>
              </div>
            </Card>

            {/* Recent Activity */}
            <Card>
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Recent Activity</h3>
              <div className="space-y-3">
                <p className="text-sm text-[#6d6760] text-center py-8">
                  No recent activity to display
                </p>
              </div>
            </Card>
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
