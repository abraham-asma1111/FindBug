'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCurrency, formatDateTime, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface OrganizationReport {
  id?: string;
  report_number?: string;
  title: string;
  status?: string;
  assigned_severity?: string | null;
  submitted_at?: string | null;
}

interface OrganizationDashboardData {
  programs: {
    total: number;
    active: number;
    top_programs: Array<{
      program_id: string;
      program_name: string;
      report_count: number;
    }>;
  };
  reports: {
    total: number;
    by_status: Record<string, number>;
    by_severity: Record<string, number>;
  };
  bounties: {
    total_paid: number;
    total_pending: number;
    total_commission: number;
    total_cost: number;
  };
  recent_reports: OrganizationReport[];
  monthly_trend: Array<{
    month: string;
    reports: number;
    spending: number;
  }>;
}

export default function OrganizationDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [data, setData] = useState<OrganizationDashboardData | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/dashboard/organization');
        if (!cancelled) {
          setData(response.data);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load organization dashboard.');
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
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Organization Overview"
          subtitle="Monitor program activity, report flow, and bounty spend from the backend dashboards already exposed for organization users."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Programs" value={isLoading ? '...' : String(data?.programs.total ?? 0)} helper="Total programs owned" />
          <StatCard label="Active Programs" value={isLoading ? '...' : String(data?.programs.active ?? 0)} helper="Public programs currently running" />
          <StatCard label="Reports" value={isLoading ? '...' : String(data?.reports.total ?? 0)} helper="Reports across all owned programs" />
          <StatCard
            label="Total Spend"
            value={isLoading ? '...' : formatCurrency(data?.bounties.total_cost)}
            helper={`Pending ${formatCurrency(data?.bounties.total_pending)}`}
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
          <SectionCard title="Report Status" description="Current report distribution across your programs.">
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(data?.reports.by_status ?? {}).map(([status, count]) => (
                <div key={status} className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">{status}</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{count}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Severity Mix" description="Assigned severity totals from submitted reports.">
            <div className="space-y-3">
              {Object.entries(data?.reports.by_severity ?? {}).map(([severity, count]) => (
                <div key={severity} className="rounded-2xl bg-[#faf6f1] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold capitalize text-[#2d2a26]">{severity}</p>
                    <p className="text-sm font-semibold text-[#2d2a26]">{count}</p>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <SectionCard title="Top Programs" description="Programs generating the highest report volume.">
            <div className="space-y-3">
              {data?.programs.top_programs?.length ? (
                data.programs.top_programs.map((program) => (
                  <div key={program.program_id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">{program.program_name}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[#8b8177]">Program performance</p>
                      </div>
                      <p className="font-semibold text-[#2d2a26]">{program.report_count} reports</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading top programs...' : 'No program performance data available yet.'}
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard title="Recent Reports" description="Latest reports entering the organization queue.">
            <div className="space-y-3">
              {data?.recent_reports?.length ? (
                data.recent_reports.map((report) => (
                  <div key={report.id || report.report_number || report.title} className="rounded-2xl bg-[#faf6f1] p-4">
                    <p className="text-sm font-semibold text-[#2d2a26]">
                      {report.report_number ? `${report.report_number} · ` : ''}
                      {report.title}
                    </p>
                    <p className="mt-2 text-sm text-[#6d6760]">{formatDateTime(report.submitted_at)}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {report.status ? (
                        <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                          {report.status}
                        </span>
                      ) : null}
                      {report.assigned_severity ? (
                        <span className="rounded-full bg-[#fde9e7] px-3 py-1 text-xs font-semibold text-[#9d1f1f]">
                          {report.assigned_severity}
                        </span>
                      ) : null}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading recent reports...' : 'No recent reports available.'}
                </p>
              )}
            </div>
          </SectionCard>
        </div>

        <div className="mt-6">
          <SectionCard title="Monthly Spend Trend" description="Report intake and spending trend for the last six months.">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {data?.monthly_trend?.length ? (
                data.monthly_trend.map((entry) => (
                  <div key={entry.month} className="rounded-2xl bg-[#faf6f1] p-4">
                    <p className="text-sm font-semibold text-[#2d2a26]">{entry.month}</p>
                    <p className="mt-2 text-sm text-[#6d6760]">{entry.reports} reports</p>
                    <p className="mt-1 font-semibold text-[#2d2a26]">{formatCurrency(entry.spending)}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading monthly trend...' : 'No monthly trend data available yet.'}
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
