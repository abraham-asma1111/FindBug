'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function TriageDashboardPage() {
  const user = useAuthStore((state) => state.user);

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch statistics
  const { data: stats } = useApiQuery<any>({
    endpoint: '/triage/statistics',
  });

  // Fetch queue for recent activity
  const { data: queueData } = useApiQuery<any>({
    endpoint: '/triage/queue?limit=5',
  });

  const recentReports = queueData?.reports || [];

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
          hideThemeToggle={true}
        >
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Triage Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Validate and prioritize vulnerability reports.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Queue management and validation overview for triage staff to process incoming security reports.
              </p>
            </div>
          </section>

          {/* Statistics Grid */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                New Reports
              </p>
              <p className="mt-2 text-3xl font-bold text-[#EF4444]">
                {stats?.status_breakdown?.new || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                In Triage
              </p>
              <p className="mt-2 text-3xl font-bold text-[#F59E0B]">
                {stats?.status_breakdown?.triaged || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Valid
              </p>
              <p className="mt-2 text-3xl font-bold text-[#3B82F6]">
                {stats?.status_breakdown?.valid || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Duplicates
              </p>
              <p className="mt-2 text-3xl font-bold text-[#94A3B8]">
                {stats?.status_breakdown?.duplicate || 0}
              </p>
            </div>
          </div>

          {/* Severity Breakdown */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Severity Breakdown</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Critical
                </p>
                <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                  {stats?.severity_breakdown?.critical || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  High
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {stats?.severity_breakdown?.high || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Medium
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                  {stats?.severity_breakdown?.medium || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Low
                </p>
                <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                  {stats?.severity_breakdown?.low || 0}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Info
                </p>
                <p className="mt-2 text-2xl font-bold text-[#94A3B8]">
                  {stats?.severity_breakdown?.info || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F8FAFC]">Recent Reports</h2>
              <Link href="/triage/queue">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>
            <div className="space-y-3">
              {recentReports.length === 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                  <p className="text-[#94A3B8]">No recent reports</p>
                </div>
              ) : (
                recentReports.map((report: any) => (
                  <Link key={report.id} href={`/triage/reports/${report.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:bg-[#334155] transition-colors cursor-pointer">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1">
                            {report.title}
                          </h3>
                          <p className="text-sm text-[#94A3B8]">
                            {report.report_number} • {new Date(report.submitted_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                            report.assigned_severity === 'critical' ? 'bg-[#EF4444] text-white' :
                            report.assigned_severity === 'high' ? 'bg-[#F59E0B] text-white' :
                            'bg-[#3B82F6] text-white'
                          }`}>
                            {report.assigned_severity || report.suggested_severity}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
