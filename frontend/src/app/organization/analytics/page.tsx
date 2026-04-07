'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems, formatCompactNumber } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Select from '@/components/ui/Select';
import StatCard from '@/components/dashboard/StatCard';
import SectionCard from '@/components/dashboard/SectionCard';

const severityColors: Record<string, string> = {
  critical: 'bg-[#9d1f1f]',
  high: 'bg-[#d6561c]',
  medium: 'bg-[#d89b16]',
  low: 'bg-[#2d78a8]',
  unassigned: 'bg-[#8b8177]',
};

const statusColors: Record<string, string> = {
  new: 'bg-[#2d78a8]',
  triaged: 'bg-[#d89b16]',
  valid: 'bg-[#24613a]',
  invalid: 'bg-[#b42318]',
  duplicate: 'bg-[#8b8177]',
  resolved: 'bg-[#5f5851]',
};

export default function OrganizationAnalyticsPage() {
  const user = useAuthStore((state) => state.user);
  const [timePeriod, setTimePeriod] = useState('6months');
  const [selectedProgram, setSelectedProgram] = useState('');

  // Fetch programs for filter
  const { data: programs } = useApiQuery('/programs/my-programs', {
    enabled: !!user,
  });

  // Fetch vulnerability trends
  const { data: trends, isLoading } = useApiQuery(
    `/analytics/vulnerability-trends?time_period=${timePeriod}${selectedProgram ? `&program_id=${selectedProgram}` : ''}`,
    { enabled: !!user }
  );

  // Fetch program effectiveness
  const { data: effectiveness } = useApiQuery(
    `/analytics/program-effectiveness${selectedProgram ? `?program_id=${selectedProgram}` : ''}`,
    { enabled: !!user }
  );

  const severityData = trends?.severity_distribution || {};
  const statusData = trends?.status_distribution || {};
  const topVulnTypes = trends?.top_vulnerability_types || [];
  const metrics = trends?.metrics || {};
  const timeSeries = trends?.time_series || [];

  const totalSeverity = Object.values(severityData).reduce((sum: number, val: any) => sum + (val || 0), 0);
  const totalStatus = Object.values(statusData).reduce((sum: number, val: any) => sum + (val || 0), 0);

  const maxTimeSeriesCount = timeSeries.reduce((max: number, entry: any) => Math.max(max, entry.count || 0), 1);

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Analytics"
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
                Analytics Dashboard
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                Track program performance and vulnerability trends.
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#5f5851] sm:text-base">
                Analyze vulnerability patterns, program effectiveness, and security metrics across your bug bounty programs.
              </p>
            </div>
          </section>

          {/* Filters */}
          <div className="mt-6">
            <Card>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
                    Time Period
                  </label>
                  <Select value={timePeriod} onChange={(e) => setTimePeriod(e.target.value)}>
                    <option value="7days">Last 7 Days</option>
                    <option value="30days">Last 30 Days</option>
                    <option value="3months">Last 3 Months</option>
                    <option value="6months">Last 6 Months</option>
                    <option value="1year">Last Year</option>
                  </Select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
                    Program
                  </label>
                  <Select value={selectedProgram} onChange={(e) => setSelectedProgram(e.target.value)}>
                    <option value="">All Programs</option>
                    {programs?.map((program: any) => (
                      <option key={program.id} value={program.id}>
                        {program.name}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>
            </Card>
          </div>

          {/* Key Metrics */}
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total Vulnerabilities"
              value={isLoading ? '...' : formatCompactNumber(trends?.total_vulnerabilities || 0)}
              helper={`In selected period`}
            />
            <StatCard
              label="Avg Time to Triage"
              value={isLoading ? '...' : `${metrics.avg_time_to_triage_hours || 0}h`}
              helper="From submission to triage"
            />
            <StatCard
              label="Avg Time to Resolve"
              value={isLoading ? '...' : `${metrics.avg_time_to_resolve_days || 0}d`}
              helper="From submission to resolution"
            />
            <StatCard
              label="Duplicate Rate"
              value={isLoading ? '...' : `${metrics.duplicate_rate || 0}%`}
              helper="Percentage of duplicates"
            />
          </div>

          {/* Vulnerability Trends Over Time */}
          <div className="mt-6">
            <SectionCard
              title="Vulnerability Submissions Over Time"
              description="Track the volume of vulnerability reports submitted over the selected period."
              headerAlign="center"
            >
              {isLoading ? (
                <div className="h-64 animate-pulse rounded-xl bg-[#f3ede6]" />
              ) : timeSeries.length > 0 ? (
                <div className="flex items-end justify-between gap-2 h-64">
                  {timeSeries.map((entry: any, index: number) => {
                    const height = maxTimeSeriesCount > 0 ? (entry.count / maxTimeSeriesCount) * 100 : 0;
                    return (
                      <div key={index} className="flex flex-1 flex-col items-center gap-2">
                        <div className="flex-1 w-full flex items-end">
                          <div
                            className="w-full rounded-t-lg bg-gradient-to-t from-[#2d78a8] to-[#6bb3d8] transition-all"
                            style={{ height: `${height}%` }}
                            title={`${entry.count} reports on ${entry.period}`}
                          />
                        </div>
                        <p className="text-xs text-[#8b8177] dark:text-slate-400 transform -rotate-45 origin-top-left">
                          {entry.period ? new Date(entry.period).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '-'}
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-[#6d6760] dark:text-slate-300 text-center py-8">
                  No data available for the selected period
                </p>
              )}
            </SectionCard>
          </div>

          {/* Distribution Charts */}
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            {/* Severity Distribution */}
            <Card className="bg-white dark:bg-slate-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-4">
                Severity Distribution
              </h3>
              <div className="space-y-4">
                {Object.entries(severityData).map(([severity, count]: [string, any]) => {
                  const percentage = totalSeverity > 0 ? (count / totalSeverity) * 100 : 0;
                  return (
                    <div key={severity}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium capitalize text-[#2d2a26] dark:text-slate-100">
                          {severity}
                        </span>
                        <span className="text-sm font-semibold text-[#6d6760] dark:text-slate-300">
                          {count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-3 rounded-full bg-[#f3ede6] dark:bg-slate-600 overflow-hidden">
                        <div
                          className={`h-full ${severityColors[severity] || 'bg-[#8b8177]'} transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Status Distribution */}
            <Card className="bg-white dark:bg-slate-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-4">
                Status Distribution
              </h3>
              <div className="space-y-4">
                {Object.entries(statusData).map(([status, count]: [string, any]) => {
                  const percentage = totalStatus > 0 ? (count / totalStatus) * 100 : 0;
                  return (
                    <div key={status}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium capitalize text-[#2d2a26] dark:text-slate-100">
                          {status}
                        </span>
                        <span className="text-sm font-semibold text-[#6d6760] dark:text-slate-300">
                          {count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-3 rounded-full bg-[#f3ede6] dark:bg-slate-600 overflow-hidden">
                        <div
                          className={`h-full ${statusColors[status] || 'bg-[#8b8177]'} transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>

          {/* Top Vulnerability Types */}
          <div className="mt-6">
            <Card className="bg-white dark:bg-slate-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-4">
                Top Vulnerability Types
              </h3>
              <div className="space-y-3">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="h-12 animate-pulse rounded-xl bg-[#f3ede6] dark:bg-slate-600" />
                  ))
                ) : topVulnTypes.length > 0 ? (
                  topVulnTypes.map((vuln: any, index: number) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-xl border border-[#e6ddd4] dark:border-slate-600 bg-[#faf6f1] dark:bg-slate-600 px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#2d2a26] dark:bg-slate-500 text-sm font-bold text-white">
                          {index + 1}
                        </span>
                        <p className="font-medium text-[#2d2a26] dark:text-slate-100">{vuln.type}</p>
                      </div>
                      <p className="text-sm font-semibold text-[#6d6760] dark:text-slate-300">
                        {vuln.count} reports
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-[#6d6760] dark:text-slate-300 text-center py-8">
                    No vulnerability types data available
                  </p>
                )}
              </div>
            </Card>
          </div>

          {/* Program Effectiveness */}
          {effectiveness && (
            <div className="mt-6">
              <SectionCard
                title="Program Effectiveness"
                description="Compare performance metrics across your programs."
                headerAlign="center"
              >
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-[#e6ddd4] dark:border-slate-600">
                        <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-slate-100">PROGRAM</th>
                        <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-slate-100">REPORTS</th>
                        <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-slate-100">AVG SEVERITY</th>
                        <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-slate-100">RESOLUTION TIME</th>
                        <th className="pb-3 font-semibold text-[#2d2a26] dark:text-slate-100">RESEARCHERS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {effectiveness.programs?.map((prog: any) => (
                        <tr key={prog.program_id} className="border-b border-[#e6ddd4] dark:border-slate-600 last:border-0">
                          <td className="py-3 pr-4 font-medium text-[#2d2a26] dark:text-slate-100">
                            {prog.program_name}
                          </td>
                          <td className="py-3 pr-4 text-[#6d6760] dark:text-slate-300">
                            {prog.total_reports}
                          </td>
                          <td className="py-3 pr-4">
                            <span className="capitalize text-[#6d6760] dark:text-slate-300">
                              {prog.avg_severity || '-'}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-[#6d6760] dark:text-slate-300">
                            {prog.avg_resolution_time ? `${prog.avg_resolution_time}d` : '-'}
                          </td>
                          <td className="py-3 text-[#6d6760] dark:text-slate-300">
                            {prog.active_researchers || 0}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </SectionCard>
            </div>
          )}
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
