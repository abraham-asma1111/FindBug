'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatDateTime, getPortalNavItems, getRoleLabel } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface StaffReport {
  id?: string;
  report_number?: string;
  title: string;
  status?: string;
  suggested_severity?: string | null;
  submitted_at?: string | null;
  triaged_at?: string | null;
}

interface StaffDashboardData {
  queue: {
    new_reports: number;
    triaged_reports: number;
    total_pending: number;
  };
  priority: {
    critical: number;
    high: number;
    unacknowledged: number;
  };
  status_breakdown: Record<string, number>;
  recent_activity: StaffReport[];
  oldest_pending: StaffReport[];
  daily_stats: Array<{
    date: string;
    submitted: number;
    triaged: number;
  }>;
}

export default function StaffDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [data, setData] = useState<StaffDashboardData | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/dashboard/staff');
        if (!cancelled) {
          setData(response.data);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load triage and finance operations dashboard.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'finance_officer', 'admin', 'staff']}>
      {user ? (
        <PortalShell
          user={user}
          title={`${getRoleLabel(user.role)} Operations`}
          subtitle="Shared operations surface for triage specialists and finance officers. The current backend dashboard is triage-heavy, so finance-specific workflow pages are the next slice after this foundation."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Pending Queue" value={isLoading ? '...' : String(data?.queue.total_pending ?? 0)} helper="New plus triaged reports" />
          <StatCard label="Critical Priority" value={isLoading ? '...' : String(data?.priority.critical ?? 0)} helper="Critical suggested severity" />
          <StatCard label="High Priority" value={isLoading ? '...' : String(data?.priority.high ?? 0)} helper="High suggested severity" />
          <StatCard label="Unacknowledged" value={isLoading ? '...' : String(data?.priority.unacknowledged ?? 0)} helper="Open for more than 24 hours" />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <SectionCard title="Status Breakdown" description="Operational distribution of report states.">
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(data?.status_breakdown ?? {}).map(([status, count]) => (
                <div key={status} className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">{status}</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{count}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Daily Throughput" description="Last seven days of submitted versus triaged volume.">
            <div className="space-y-3">
              {data?.daily_stats?.length ? (
                data.daily_stats.map((entry) => (
                  <div key={entry.date} className="rounded-2xl bg-[#faf6f1] p-4">
                    <div className="flex items-center justify-between gap-4">
                      <p className="text-sm font-semibold text-[#2d2a26]">{entry.date}</p>
                      <div className="text-right text-sm text-[#6d6760]">
                        <p>{entry.submitted} submitted</p>
                        <p>{entry.triaged} triaged</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading daily throughput...' : 'No daily stats available.'}
                </p>
              )}
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <SectionCard title="Recent Activity" description="Reports triaged most recently.">
            <div className="space-y-3">
              {data?.recent_activity?.length ? (
                data.recent_activity.map((report) => (
                  <div key={report.id || report.report_number || report.title} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-4">
                    <p className="text-sm font-semibold text-[#2d2a26]">
                      {report.report_number ? `${report.report_number} · ` : ''}
                      {report.title}
                    </p>
                    <p className="mt-2 text-sm text-[#6d6760]">
                      Triaged {formatDateTime(report.triaged_at)}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading recent activity...' : 'No recent triage activity available.'}
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard title="Oldest Pending Reports" description="Items likely needing immediate operational attention.">
            <div className="space-y-3">
              {data?.oldest_pending?.length ? (
                data.oldest_pending.map((report) => (
                  <div key={report.id || report.report_number || report.title} className="rounded-3xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-4">
                    <p className="text-sm font-semibold text-[#2d2a26]">
                      {report.report_number ? `${report.report_number} · ` : ''}
                      {report.title}
                    </p>
                    <p className="mt-2 text-sm text-[#6d6760]">Submitted {formatDateTime(report.submitted_at)}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {report.status ? (
                        <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                          {report.status}
                        </span>
                      ) : null}
                      {report.suggested_severity ? (
                        <span className="rounded-full bg-[#fde9e7] px-3 py-1 text-xs font-semibold text-[#9d1f1f]">
                          {report.suggested_severity}
                        </span>
                      ) : null}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading pending reports...' : 'No pending reports available.'}
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
