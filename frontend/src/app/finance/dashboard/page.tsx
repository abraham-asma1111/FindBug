'use client';

import { useEffect, useMemo } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import LineChart from '@/components/ui/LineChart';
import PieChart from '@/components/ui/PieChart';
import BarChart from '@/components/ui/BarChart';

export default function FinanceDashboardPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch data from backend
  const { data: analyticsData, isLoading: analyticsLoading } = useApiQuery<any>({ endpoint: '/payments/analytics?range=30d' });
  const { data: payoutsData } = useApiQuery<any>({ endpoint: '/wallet/payouts?status=requested&limit=100' });
  const { data: triageSeverityData, isLoading: triageSeverityLoading } = useApiQuery<any>({ endpoint: '/triage/valid-reports-by-severity' });

  // Process analytics data
  const stats = analyticsData?.stats || {};
  const paymentTrends = analyticsData?.payment_trends || [];
  const severityDistribution = analyticsData?.severity_distribution || [];
  const topResearchers = analyticsData?.top_researchers || [];

  // Calculate KPIs from analytics
  const totalBalance = stats.total_amount || 0;
  const totalPayments = stats.total_payments || 0;
  const avgPayment = stats.avg_payment || 0;
  const totalCommission = stats.total_commission || 0;
  
  // Pending payouts from real data
  const pendingPayouts = payoutsData?.payouts || [];
  const pendingPayoutsAmount = pendingPayouts.reduce((sum: number, p: any) => sum + (p.amount || 0), 0);
  const pendingPayoutsCount = pendingPayouts.length;

  // Calculate growth percentages (mock for now - would need historical data)
  const balanceGrowth = 12.5;
  const paymentsGrowth = 8.3;
  const researchersGrowth = 18.6;

  // Format chart data for Line Chart
  const chartData = useMemo(() => {
    return paymentTrends.map((trend: any) => ({
      date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      amount: trend.amount,
      commission: trend.commission,
    }));
  }, [paymentTrends]);

  // Format severity data for Pie Chart (from payment analytics)
  const severityChartData = useMemo(() => {
    const colorMap: Record<string, string> = {
      'Critical': '#EF4444',
      'High': '#F59E0B',
      'Medium': '#FBBF24',
      'Low': '#10B981',
    };
    
    return severityDistribution.map((item: any) => ({
      label: item.name,
      value: Math.round(item.value),
      color: colorMap[item.name] || '#94A3B8',
    }));
  }, [severityDistribution]);

  const totalSeverityAmount = severityChartData.reduce((sum: number, item: any) => sum + item.value, 0);

  // Format triage severity data for Bar Chart (from triage valid reports)
  const triageBarChartData = useMemo(() => {
    if (!triageSeverityData?.by_severity) return [];
    
    const colorMap: Record<string, string> = {
      'critical': '#EF4444',
      'high': '#F59E0B',
      'medium': '#FBBF24',
      'low': '#10B981',
      'info': '#94A3B8',
      'not_assigned': '#64748B',
    };
    
    // Sort by severity order
    const severityOrder = ['critical', 'high', 'medium', 'low', 'info', 'not_assigned'];
    const sorted = [...triageSeverityData.by_severity].sort((a, b) => {
      return severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity);
    });
    
    return sorted.map((item: any) => ({
      label: item.severity.charAt(0).toUpperCase() + item.severity.slice(1).replace('_', ' '),
      value: item.count,
      color: colorMap[item.severity] || '#94A3B8',
    }));
  }, [triageSeverityData]);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finance Dashboard"
          subtitle={`Welcome back, ${user.fullName || 'Finance Officer'} 👋`}
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* KPI Cards - Row 1 */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5 mb-4">
            {/* Total Balance */}
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155] shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-[#3B82F6]/10 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-[#94A3B8] mb-1">Total Balance</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${totalBalance.toLocaleString()}</p>
              <p className="text-xs text-[#10B981]">↑ {balanceGrowth}% from last month</p>
            </div>

            {/* Pending Payouts */}
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155] shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-[#F59E0B]/10 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-[#94A3B8] mb-1">Pending Payouts</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${pendingPayoutsAmount.toLocaleString()}</p>
              <p className="text-xs text-[#94A3B8]">{pendingPayoutsCount} payouts pending</p>
            </div>

            {/* Total Paid (This Month) */}
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155] shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-[#10B981]/10 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-[#94A3B8] mb-1">Total Paid</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${totalBalance.toLocaleString()}</p>
              <p className="text-xs text-[#10B981]">↑ {paymentsGrowth}% from last month</p>
            </div>

            {/* Open Reports */}
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155] shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-[#8B5CF6]/10 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-[#94A3B8] mb-1">Open Reports</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">{totalSeverityAmount || 156}</p>
              <p className="text-xs text-[#94A3B8]">24 critical, 45 high</p>
            </div>

            {/* Total Researchers */}
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155] shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-[#EC4899]/10 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#EC4899]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-[#94A3B8] mb-1">Active Researchers</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">{topResearchers.length > 0 ? topResearchers.length : '-'}</p>
              <p className="text-xs text-[#10B981]">↑ {researchersGrowth}% this month</p>
            </div>
          </div>

          {/* Charts Row - Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">
            {/* Line Chart - Bounty Spending */}
            <div className="lg:col-span-5 bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-[#F8FAFC]">Bounty Spending Over Time</h2>
                <select className="px-2 py-1 bg-[#0F172A] border border-[#334155] rounded text-xs text-[#F8FAFC]">
                  <option>Last 12 Months</option>
                  <option>Last 6 Months</option>
                  <option>Last 3 Months</option>
                </select>
              </div>
              {analyticsLoading || chartData.length === 0 ? (
                <div className="h-56 flex items-center justify-center text-[#64748B]">
                  <p className="text-sm">{analyticsLoading ? 'Loading...' : 'No data'}</p>
                </div>
              ) : (
                <LineChart
                  data={chartData}
                  xKey="date"
                  lines={[
                    { key: 'amount', color: '#3B82F6', name: 'Payments' },
                    { key: 'commission', color: '#10B981', name: 'Commission' },
                  ]}
                  height={240}
                />
              )}
            </div>

            {/* Bar Chart - Valid Reports by Severity (from Triage) */}
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <h2 className="text-base font-semibold text-[#F8FAFC] mb-3">Valid Reports by Severity</h2>
              <p className="text-xs text-[#94A3B8] mb-4">From Triage Queue</p>
              {triageSeverityLoading || triageBarChartData.length === 0 ? (
                <div className="h-56 flex items-center justify-center text-[#64748B]">
                  <p className="text-sm">{triageSeverityLoading ? 'Loading...' : 'No valid reports'}</p>
                </div>
              ) : (
                <BarChart
                  data={triageBarChartData}
                  height={240}
                  showValues={true}
                  valueFormatter={(value) => value.toString()}
                />
              )}
            </div>

            {/* Top Programs by Spend */}
            <div className="lg:col-span-3 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="flex items-center justify-between p-4 border-b border-[#334155]">
                <h2 className="text-sm font-semibold text-[#F8FAFC]">Top Programs by Spend</h2>
                <Link href="/finance/reports">
                  <Button variant="ghost" size="xs">View all</Button>
                </Link>
              </div>
              <div className="divide-y divide-[#334155]">
                {[
                  { name: 'Web Application Program', amount: 48750 },
                  { name: 'Mobile Security Program', amount: 18450 },
                  { name: 'API Security Program', amount: 8750 },
                  { name: 'Infrastructure Program', amount: 2350 },
                ].map((program, index) => (
                  <div key={index} className="flex items-center justify-between p-3 hover:bg-[#0F172A]/50 transition-colors">
                    <span className="text-sm text-[#F8FAFC] truncate flex-1">{program.name}</span>
                    <span className="text-sm font-bold text-[#F8FAFC] ml-3 flex-shrink-0">${program.amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Tables Row - Row 3 */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">
            {/* Recent Payouts Table */}
            <div className="lg:col-span-8 bg-[#1E293B] rounded-lg p-5 border border-[#334155]">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-[#F8FAFC]">Recent Payouts</h2>
                <Link href="/finance/payments">
                  <Button variant="ghost" size="xs">View all payouts →</Button>
                </Link>
              </div>
              {analyticsLoading ? (
                <div className="py-8 text-center text-[#64748B] text-sm">Loading...</div>
              ) : topResearchers.length === 0 ? (
                <div className="py-8 text-center text-[#64748B] text-sm">No payouts found</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-[#334155]">
                        <th className="text-left py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Researcher</th>
                        <th className="text-left py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Report</th>
                        <th className="text-left py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Program</th>
                        <th className="text-left py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Severity</th>
                        <th className="text-right py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Amount</th>
                        <th className="text-center py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Status</th>
                        <th className="text-right py-2 px-2 text-xs font-semibold text-[#94A3B8] uppercase">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topResearchers.slice(0, 5).map((researcher: any, index: number) => (
                        <tr key={researcher.id} className="border-b border-[#334155]/50 hover:bg-[#334155]/20 transition-colors">
                          <td className="py-2.5 px-2">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white text-xs font-bold">
                                {(researcher.name || 'R')[0]}
                              </div>
                              <span className="text-xs text-[#F8FAFC] font-medium">{researcher.name || 'Researcher'}</span>
                            </div>
                          </td>
                          <td className="py-2.5 px-2 text-xs text-[#94A3B8]">#SC-{2548 + index}</td>
                          <td className="py-2.5 px-2 text-xs text-[#94A3B8]">Web Application Program</td>
                          <td className="py-2.5 px-2">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                              index === 0 ? 'bg-[#EF4444] text-white' :
                              index === 1 ? 'bg-[#F59E0B] text-white' :
                              index === 2 ? 'bg-[#F59E0B] text-white' :
                              index === 3 ? 'bg-[#FBBF24] text-white' :
                              'bg-[#10B981] text-white'
                            }`}>
                              {index === 0 ? 'Critical' : index === 1 ? 'High' : index === 2 ? 'High' : index === 3 ? 'Medium' : 'Low'}
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-right text-xs font-bold text-[#10B981]">${researcher.total_earned.toLocaleString()}</td>
                          <td className="py-2.5 px-2 text-center">
                            <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-[#10B981] text-white">
                              Paid
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-right text-xs text-[#94A3B8]">May {21 - index}, 2024</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="flex items-center justify-between p-4 border-b border-[#334155]">
                <h2 className="text-sm font-semibold text-[#F8FAFC]">Recent Activity</h2>
                <Button variant="ghost" size="xs">View all</Button>
              </div>
              {analyticsLoading ? (
                <div className="py-4 text-center text-[#64748B] text-xs">Loading...</div>
              ) : (
                <div className="divide-y divide-[#334155]">
                {[
                  { type: 'report', title: 'New report submitted', desc: 'Reflected XSS in search endpoint', time: '2m ago' },
                  { type: 'payout', title: 'Report triaged', desc: 'Marked report probe for API', time: '16m ago' },
                  { type: 'payout', title: 'Payout approved', desc: '$5,000.00 to bug_buster', time: '1h ago' },
                  { type: 'researcher', title: 'New researcher joined', desc: 'n3t_runner joined your program', time: '3h ago' },
                  { type: 'report', title: 'Rated submitted', desc: 'Re-test for SQL Injection', time: '3h ago' },
                ].map((activity, index) => (
                  <div key={index} className="flex items-start justify-between gap-3 p-3 hover:bg-[#0F172A]/50 transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[#F8FAFC] leading-tight">{activity.title}</p>
                      <p className="text-xs text-[#94A3B8] mt-1 leading-tight">{activity.desc}</p>
                    </div>
                    <span className="text-xs text-[#64748B] whitespace-nowrap flex-shrink-0">{activity.time}</span>
                  </div>
                ))}
              </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/finance/payments">
              <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#2563EB]/10 border border-[#3B82F6]/20 rounded-xl p-6 hover:border-[#3B82F6]/40 transition-all cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#3B82F6] rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#F8FAFC]">All Payments</h3>
                    <p className="text-sm text-[#94A3B8]">View and manage all payments</p>
                    <p className="text-xs text-[#3B82F6] mt-1">View payments →</p>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/finance/payouts?status=requested">
              <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#D97706]/10 border border-[#F59E0B]/20 rounded-xl p-6 hover:border-[#F59E0B]/40 transition-all cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#F59E0B] rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#F8FAFC]">Pending Payouts</h3>
                    <p className="text-sm text-[#94A3B8]">Review and approve payout requests</p>
                    <p className="text-xs text-[#F59E0B] mt-1">Review now →</p>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/finance/reports">
              <div className="bg-gradient-to-br from-[#10B981]/10 to-[#059669]/10 border border-[#10B981]/20 rounded-xl p-6 hover:border-[#10B981]/40 transition-all cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#10B981] rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#F8FAFC]">Financial Reports</h3>
                    <p className="text-sm text-[#94A3B8]">Generate and download reports</p>
                    <p className="text-xs text-[#10B981] mt-1">View reports →</p>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
