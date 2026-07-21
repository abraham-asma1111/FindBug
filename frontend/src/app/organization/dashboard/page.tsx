'use client';

import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems, formatCurrency, formatCompactNumber } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import SectionCard from '@/components/dashboard/SectionCard';
import PieChart from '@/components/ui/PieChart';

const severityColors: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-[#2d2a26]',
  low: 'bg-[#2d78a8] text-white',
};

const statusColors: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  triaged: 'bg-[#faf1e1] text-[#9a6412]',
  valid: 'bg-[#eef7ef] text-[#24613a]',
  resolved: 'bg-[#f3ede6] text-[#5f5851]',
};

export default function OrganizationDashboardPage() {
  const user = useAuthStore((state) => state.user);

  const { data, isLoading, isError, error } = useApiQuery('/dashboard/organization', {
    enabled: !!user,
  });

  // Show error state if API call failed
  if (isError && error) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="Organization Dashboard"
            subtitle=""
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
            hideTitle
            hideSubtitle
          >
            <div className="rounded-xl border border-red-200 bg-red-50 p-6">
              <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Dashboard</h3>
              <p className="text-red-700">{error.message}</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 rounded-full bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  const programs = data?.programs || { total: 0, active: 0, top_programs: [] };
  const reports = data?.reports || { total: 0, by_status: {}, by_severity: {} };
  const bounties = data?.bounties || { total_paid: 0, total_pending: 0, total_commission: 0, total_cost: 0 };
  const recentReports = data?.recent_reports || [];
  const monthlyTrend = data?.monthly_trend || [];

  const pendingReports = (reports.by_status?.new || 0) + (reports.by_status?.triaged || 0);

  // Generate 12 months data with month names
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const twelveMonthsData = monthNames.map((name, index) => {
    const monthData = monthlyTrend.find((entry: any) => {
      if (!entry.month) return false;
      const entryMonth = parseInt(entry.month.split('-')[1]) - 1;
      return entryMonth === index;
    });
    return {
      month: name,
      reports: monthData?.reports || 0,
      spending: monthData?.spending || 0
    };
  });

  const maxMonthlyReports = twelveMonthsData.reduce((max: number, entry: any) => Math.max(max, entry.reports || 0), 1);

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Organization Dashboard"
          subtitle=""
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                  Organization Dashboard
                </p>
                <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                  Manage programs, reports, and researcher engagement.
                </h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-[#5f5851] sm:text-base">
                  Welcome back, {user.organization?.company_name || 'Organization'}. Track your bug bounty programs, review vulnerability reports, and monitor platform activity.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <div className="rounded-[28px] bg-[#2d2a26] p-5 text-white shadow-[0_18px_40px_rgba(45,42,38,0.2)]">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/70">Pending Review</p>
                  <p className="mt-3 text-3xl font-semibold">
                    {isLoading ? '...' : formatCompactNumber(pendingReports)}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-white/78">
                    Reports awaiting triage or validation from your team.
                  </p>
                </div>
                <div className="rounded-[28px] border border-[#ddd4cb] bg-white/80 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8b8177]">Total Spent</p>
                  <p className="mt-3 text-3xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : formatCurrency(bounties.total_cost)}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                    Bounties plus platform commission paid to date.
                  </p>
                </div>
                <div className="rounded-[28px] border border-[#ddd4cb] bg-white/80 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8b8177]">Active Programs</p>
                  <p className="mt-3 text-3xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : programs.active}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                    {programs.total} total programs created.
                  </p>
                </div>
              </div>

              {/* Action Buttons - Horizontally aligned below the cards */}
              <div className="sm:col-span-3 xl:col-span-1 flex flex-wrap gap-2 justify-center xl:justify-start mt-3">
                <Link
                  href="/organization/programs"
                  className="inline-flex justify-center rounded-full bg-[#2d2a26] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1f1c19]"
                >
                  Manage Programs
                </Link>
                <Link
                  href="/organization/reports"
                  className="inline-flex justify-center rounded-full border border-[#c9beb1] bg-white/80 px-5 py-3 text-sm font-semibold text-[#2d2a26] transition hover:border-[#bcae9e] hover:bg-white"
                >
                  Review Reports
                </Link>
              </div>
            </div>
          </section>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total Programs"
              value={isLoading ? '...' : formatCompactNumber(programs.total)}
              helper={`${programs.active} active programs`}
            />
            <StatCard
              label="Total Reports"
              value={isLoading ? '...' : formatCompactNumber(reports.total)}
              helper={`${pendingReports} pending review`}
            />
            <StatCard
              label="Bounties Paid"
              value={isLoading ? '...' : formatCurrency(bounties.total_paid)}
              helper={`${formatCurrency(bounties.total_pending)} pending`}
            />
            <StatCard
              label="Platform Fees"
              value={isLoading ? '...' : formatCurrency(bounties.total_commission)}
              helper="30% commission on bounties"
            />
          </div>

          <div className="mt-6">
            <SectionCard
              title="Recent Reports"
              description="Latest vulnerability reports submitted across all your programs."
              headerAlign="center"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-[#e6ddd4]">
                      <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">DATE</th>
                      <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">REPORT</th>
                      <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PROGRAM</th>
                      <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">SEVERITY</th>
                      <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
                      <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={`loading-${i}`} className="border-b border-[#efe7de]">
                          <td className="py-4" colSpan={6}>
                            <div className="h-8 animate-pulse rounded-xl bg-[#f3ede6]" />
                          </td>
                        </tr>
                      ))
                    ) : recentReports.length > 0 ? (
                      recentReports.map((report: any) => (
                        <tr key={report.id} className="border-b border-[#e6ddd4] last:border-0">
                          <td className="py-3 pr-4 text-[#6d6760]">
                            {report.submitted_at
                              ? new Date(report.submitted_at).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                })
                              : '-'}
                          </td>
                          <td className="py-3 pr-4">
                            <p className="font-medium text-[#2d2a26]">{report.title}</p>
                            <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[#8b8177]">
                              {report.report_number}
                            </p>
                          </td>
                          <td className="py-3 pr-4 text-[#6d6760]">
                            {report.program?.name || report.program_name || report.programName || '-'}
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                severityColors[report.assigned_severity?.toLowerCase()] || 'bg-[#f3ede6] text-[#5f5851]'
                              }`}
                            >
                              {report.assigned_severity || 'Unscored'}
                            </span>
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                statusColors[report.status?.toLowerCase()] || 'bg-[#f3ede6] text-[#5f5851]'
                              }`}
                            >
                              {report.status || 'Unknown'}
                            </span>
                          </td>
                          <td className="py-3">
                            <Link
                              href={`/organization/reports?id=${report.id}`}
                              className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                            >
                              View
                            </Link>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-10 text-center">
                          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                            No reports yet
                          </p>
                          <p className="mt-2 text-sm text-[#6d6760]">
                            Reports will appear here once researchers start submitting.
                          </p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <Card className="bg-white dark:bg-[#111111] dark:bg-[#111111] border-[#e6ddd4] dark:border-gray-700">
              <div className="mb-6">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-white">Monthly Trend</h3>
                  <div className="flex items-center justify-center gap-2 mt-1">
                    <p className="text-xs text-slate-500 dark:text-slate-400">{new Date().getFullYear()}</p>
                    <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                      {twelveMonthsData.some(d => d.reports > 0) ? '↗ +12.5%' : '0%'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                {isLoading ? (
                  <div className="h-64 animate-pulse rounded-xl bg-[#f3ede6] dark:bg-slate-700" />
                ) : twelveMonthsData.length > 0 ? (
                  <div className="space-y-6">
                    {/* Chart Area */}
                    <div className="relative h-64 bg-slate-50 dark:bg-[#111111]/40 rounded-xl p-4 border border-slate-200 dark:border-gray-700">
                      {/* Grid Lines */}
                      <div className="absolute inset-0 flex flex-col justify-between p-4 pointer-events-none">
                        {[...Array(5)].map((_, i) => (
                          <div key={i} className="border-t border-slate-200 dark:border-gray-700/50" />
                        ))}
                      </div>
                      
                      {/* Bars */}
                      <div className="relative h-full flex items-end justify-between gap-2 px-2">
                        {twelveMonthsData.map((entry: any) => {
                          const height = maxMonthlyReports > 0 ? (entry.reports / maxMonthlyReports) * 100 : 0;
                          const isHighest = entry.reports === maxMonthlyReports && entry.reports > 0;
                          return (
                            <div key={entry.month} className="flex-1 flex flex-col items-center gap-2 group relative">
                              {/* Value on hover */}
                              <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-12 left-1/2 transform -translate-x-1/2 bg-slate-800 dark:bg-slate-700 px-3 py-2 rounded-lg text-xs text-white whitespace-nowrap shadow-xl z-10 pointer-events-none">
                                <div className="font-semibold">{entry.reports} reports</div>
                                <div className="text-slate-300">{formatCurrency(entry.spending)}</div>
                                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-slate-800 dark:bg-slate-700"></div>
                              </div>
                              
                              {/* Bar */}
                              <div className="relative w-full flex items-end justify-center" style={{ height: '100%' }}>
                                <div
                                  className={`w-full rounded-t-lg transition-all duration-300 group-hover:scale-105 cursor-pointer relative overflow-hidden shadow-lg ${
                                    isHighest 
                                      ? 'bg-gradient-to-t from-emerald-600 via-emerald-500 to-emerald-400 dark:from-emerald-700 dark:via-emerald-600 dark:to-emerald-500' 
                                      : 'bg-gradient-to-t from-blue-600 via-blue-500 to-blue-400 dark:from-blue-700 dark:via-blue-600 dark:to-blue-500'
                                  }`}
                                  style={{ 
                                    height: entry.reports > 0 ? `${height}%` : '4px',
                                    minHeight: entry.reports > 0 ? '20px' : '4px'
                                  }}
                                >
                                  {/* Shine effect */}
                                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                                </div>
                              </div>
                              
                              {/* Month Label */}
                              <p className="text-[10px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mt-1">
                                {entry.month}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    
                    {/* Stats Row */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-slate-50 dark:bg-[#111111]/40 rounded-lg p-4 border border-slate-200 dark:border-gray-700">
                        <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Total Reports</p>
                        <p className="text-2xl font-bold text-slate-900 dark:text-white">
                          {twelveMonthsData.reduce((sum: number, entry: any) => sum + (entry.reports || 0), 0)}
                        </p>
                      </div>
                      <div className="bg-slate-50 dark:bg-[#111111]/40 rounded-lg p-4 border border-slate-200 dark:border-gray-700">
                        <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Total Spent</p>
                        <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                          {formatCurrency(twelveMonthsData.reduce((sum: number, entry: any) => sum + (entry.spending || 0), 0))}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center">
                    <p className="text-sm text-slate-500 dark:text-slate-400">No trend data available</p>
                  </div>
                )}
              </div>
            </Card>

            <Card className="bg-white dark:bg-[#111111] dark:bg-[#111111] border-[#e6ddd4] dark:border-gray-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-6 text-center">Top Programs</h3>
              <div className="space-y-2.5">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <div key={`loading-prog-${i}`} className="h-14 animate-pulse rounded-xl bg-[#f3ede6] dark:bg-slate-700" />
                  ))
                ) : programs.top_programs?.length > 0 ? (
                  programs.top_programs.map((prog: any, index: number) => (
                    <div
                      key={prog.program_id}
                      className="flex items-center justify-between rounded-xl border border-[#e6ddd4] bg-[#faf6f1] dark:bg-slate-700 dark:border-slate-600 px-4 py-3.5 hover:border-[#d4c5b3] dark:hover:border-slate-500 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-[#d4a574] to-[#e6c896] dark:from-[#c9a66b] dark:to-[#d4a574] text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <p className="font-semibold text-[#2d2a26] dark:text-slate-100">{prog.program_name}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-[#2d2a26] dark:text-slate-100">{prog.report_count}</span>
                        <span className="text-xs text-[#8b8177] dark:text-slate-400">reports</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-[#6d6760] dark:text-slate-400 text-center py-12">No programs yet</p>
                )}
              </div>
            </Card>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <Card className="bg-white dark:bg-[#111111] dark:bg-[#111111] border-[#e6ddd4] dark:border-gray-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-6 text-center">Reports by Status</h3>
              {isLoading ? (
                <div className="h-64 animate-pulse rounded-xl bg-[#f3ede6] dark:bg-slate-700" />
              ) : (
                <PieChart
                  data={[
                    { label: 'New', value: reports.by_status?.new || 0, color: '#3b82f6' },
                    { label: 'Triaged', value: reports.by_status?.triaged || 0, color: '#f59e0b' },
                    { label: 'Valid', value: reports.by_status?.valid || 0, color: '#10b981' },
                    { label: 'Resolved', value: reports.by_status?.resolved || 0, color: '#8b5cf6' },
                  ]}
                  size={240}
                  showLegend={true}
                />
              )}
            </Card>

            <Card className="bg-white dark:bg-[#111111] dark:bg-[#111111] border-[#e6ddd4] dark:border-gray-700">
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100 mb-6 text-center">Reports by Severity</h3>
              {isLoading ? (
                <div className="h-64 animate-pulse rounded-xl bg-[#f3ede6] dark:bg-slate-700" />
              ) : (
                <div className="space-y-4">
                  {/* Bar Chart */}
                  <div className="relative h-64 bg-slate-50 dark:bg-[#111111]/40 rounded-xl p-4 border border-slate-200 dark:border-gray-700">
                    {/* Grid Lines */}
                    <div className="absolute inset-0 flex flex-col justify-between p-4 pointer-events-none">
                      {[...Array(5)].map((_, i) => (
                        <div key={i} className="border-t border-slate-200 dark:border-gray-700/50" />
                      ))}
                    </div>
                    
                    {/* Bars */}
                    <div className="relative h-full flex items-end justify-between gap-3 px-2">
                      {['critical', 'high', 'medium', 'low'].map((severity) => {
                        const count = reports.by_severity?.[severity] || 0;
                        const total = reports.total || 1;
                        const maxCount = Math.max(
                          reports.by_severity?.critical || 0,
                          reports.by_severity?.high || 0,
                          reports.by_severity?.medium || 0,
                          reports.by_severity?.low || 0,
                          1
                        );
                        const height = (count / maxCount) * 100;
                        
                        const severityColorMap: Record<string, string> = {
                          critical: 'bg-gradient-to-t from-red-600 via-red-500 to-red-400 dark:from-red-700 dark:via-red-600 dark:to-red-500',
                          high: 'bg-gradient-to-t from-orange-600 via-orange-500 to-orange-400 dark:from-orange-700 dark:via-orange-600 dark:to-orange-500',
                          medium: 'bg-gradient-to-t from-yellow-600 via-yellow-500 to-yellow-400 dark:from-yellow-700 dark:via-yellow-600 dark:to-yellow-500',
                          low: 'bg-gradient-to-t from-blue-600 via-blue-500 to-blue-400 dark:from-blue-700 dark:via-blue-600 dark:to-blue-500',
                        };
                        
                        return (
                          <div key={severity} className="flex-1 flex flex-col items-center gap-2 group relative">
                            {/* Value on hover */}
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-12 left-1/2 transform -translate-x-1/2 bg-slate-800 dark:bg-slate-700 px-3 py-2 rounded-lg text-xs text-white whitespace-nowrap shadow-xl z-10 pointer-events-none">
                              <div className="font-semibold">{count} reports</div>
                              <div className="text-slate-300">{((count / total) * 100).toFixed(1)}%</div>
                              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-slate-800 dark:bg-slate-700"></div>
                            </div>
                            
                            {/* Bar */}
                            <div className="relative w-full flex items-end justify-center" style={{ height: '100%' }}>
                              <div
                                className={`w-full rounded-t-lg transition-all duration-300 group-hover:scale-105 cursor-pointer relative overflow-hidden shadow-lg ${severityColorMap[severity]}`}
                                style={{ 
                                  height: count > 0 ? `${height}%` : '4px',
                                  minHeight: count > 0 ? '20px' : '4px'
                                }}
                              >
                                {/* Shine effect */}
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                              </div>
                            </div>
                            
                            {/* Severity Label */}
                            <p className="text-[10px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mt-1 capitalize">
                              {severity}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
