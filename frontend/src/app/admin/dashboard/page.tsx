'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface AdminDashboardData {
  users: {
    total: number;
    researchers: number;
    organizations: number;
    active_30d: number;
    new_30d: number;
  };
  programs: {
    total: number;
    active: number;
    new_30d: number;
  };
  reports: {
    total: number;
    by_status: Record<string, number>;
    new_30d: number;
  };
  financials: {
    total_paid: number;
    total_pending: number;
    platform_revenue: number;
    commission_rate: number;
  };
  top_performers: {
    researchers: Array<{
      id: string;
      username: string;
      reputation: number;
      rank: number;
    }>;
    organizations: Array<{
      id: string;
      name: string;
      program_count: number;
    }>;
  };
  health: {
    pending_triage: number;
    overdue_payouts: number;
  };
  monthly_growth: Array<{
    month: string;
    new_users: number;
    new_reports: number;
    new_programs: number;
    revenue: number;
  }>;
}

interface StaffStatistics {
  total_staff: number;
  active_staff: number;
  by_department: Record<string, number>;
  avg_triage_time_hours: number;
  total_reports_triaged: number;
}

export default function AdminDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [dashboard, setDashboard] = useState<AdminDashboardData | null>(null);
  const [staffStats, setStaffStats] = useState<StaffStatistics | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadAdminData = async () => {
      try {
        setIsLoading(true);
        const [dashboardResponse, staffResponse] = await Promise.all([
          api.get('/dashboard/admin'),
          api.get('/admin/staff/statistics'),
        ]);

        if (!cancelled) {
          setDashboard(dashboardResponse.data);
          setStaffStats(staffResponse.data);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load admin dashboard.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadAdminData();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Platform Overview"
          subtitle="Cross-role admin surface for user growth, financial health, operations visibility, and staff provisioning."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                Admin Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Platform oversight and operational control.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Cross-role admin surface for user growth, financial health, operations visibility, and staff provisioning.
              </p>
            </div>
          </section>

          {error ? (
            <div className="mt-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Users" value={isLoading ? '...' : String(dashboard?.users.total ?? 0)} helper={`${dashboard?.users.active_30d ?? 0} active in 30d`} />
          <StatCard label="Programs" value={isLoading ? '...' : String(dashboard?.programs.total ?? 0)} helper={`${dashboard?.programs.active ?? 0} currently active`} />
          <StatCard label="Reports" value={isLoading ? '...' : String(dashboard?.reports.total ?? 0)} helper={`${dashboard?.reports.new_30d ?? 0} new in 30d`} />
          <StatCard
            label="Platform Revenue"
            value={isLoading ? '...' : formatCurrency(dashboard?.financials.platform_revenue)}
            helper={`Pending ${formatCurrency(dashboard?.financials.total_pending)}`}
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <SectionCard title="User Mix" description="Platform-wide user distribution from the admin dashboard service.">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Researchers</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.users.researchers ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Organizations</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.users.organizations ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">New in 30d</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.users.new_30d ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Active in 30d</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.users.active_30d ?? 0}</p>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Platform Health" description="Immediate operational risks the admin role should see first.">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl bg-[#fff2f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#9d1f1f]">Pending Triage</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.health.pending_triage ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-[#fff6e9] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8a5b16]">Overdue Payouts</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{dashboard?.health.overdue_payouts ?? 0}</p>
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <SectionCard title="Report Status" description="Global report distribution across the platform.">
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(dashboard?.reports.by_status ?? {}).map(([status, count]) => (
                <div key={status} className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">{status}</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{count}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Staff Operations" description="Admin-only staff metrics from `/admin/staff/statistics`.">
            <div className="space-y-3">
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-[#6d6760]">Total staff</span>
                  <span className="font-semibold text-[#2d2a26]">{staffStats?.total_staff ?? 0}</span>
                </div>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-[#6d6760]">Active staff</span>
                  <span className="font-semibold text-[#2d2a26]">{staffStats?.active_staff ?? 0}</span>
                </div>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-[#6d6760]">Avg triage time</span>
                  <span className="font-semibold text-[#2d2a26]">{staffStats?.avg_triage_time_hours ?? 0}h</span>
                </div>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-[#6d6760]">Reports triaged</span>
                  <span className="font-semibold text-[#2d2a26]">{staffStats?.total_reports_triaged ?? 0}</span>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <SectionCard title="Top Performers" description="Researchers and organizations surfaced by the admin dashboard.">
            <div className="space-y-4">
              <div>
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Researchers</p>
                <div className="space-y-3">
                  {dashboard?.top_performers.researchers?.map((researcher) => (
                    <div key={researcher.id} className="rounded-2xl bg-[#faf6f1] p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">{researcher.username}</p>
                          <p className="mt-1 text-xs text-[#8b8177]">Rank #{researcher.rank || '-'}</p>
                        </div>
                        <p className="font-semibold text-[#2d2a26]">{researcher.reputation.toFixed(1)}</p>
                      </div>
                    </div>
                  )) || <p className="text-sm text-[#6d6760]">No researcher data available.</p>}
                </div>
              </div>

              <div>
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Organizations</p>
                <div className="space-y-3">
                  {dashboard?.top_performers.organizations?.map((organization) => (
                    <div key={organization.id} className="rounded-2xl bg-[#faf6f1] p-4">
                      <div className="flex items-center justify-between gap-4">
                        <p className="text-sm font-semibold text-[#2d2a26]">{organization.name}</p>
                        <p className="font-semibold text-[#2d2a26]">{organization.program_count} programs</p>
                      </div>
                    </div>
                  )) || <p className="text-sm text-[#6d6760]">No organization data available.</p>}
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Monthly Growth" description="User, report, program, and revenue growth over the last six months.">
            <div className="space-y-3">
              {dashboard?.monthly_growth?.length ? (
                dashboard.monthly_growth.map((entry) => (
                  <div key={entry.month} className="rounded-2xl bg-[#faf6f1] p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">{entry.month}</p>
                        <p className="mt-1 text-xs text-[#8b8177]">
                          {entry.new_users} users · {entry.new_reports} reports · {entry.new_programs} programs
                        </p>
                      </div>
                      <p className="font-semibold text-[#2d2a26]">{formatCurrency(entry.revenue)}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading growth metrics...' : 'No growth data available yet.'}
                </p>
              )}
            </div>
          </SectionCard>
        </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
