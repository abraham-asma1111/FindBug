'use client';

import { useEffect, useMemo } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import BountyTrendChart from '@/components/ui/BountyTrendChart';
import PieChart from '@/components/ui/PieChart';
import BarChart from '@/components/ui/BarChart';

export default function FinanceDashboardPage() {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch data from Finance Analytics APIs
  const { data: kpisData, isLoading: kpisLoading } = useApiQuery<any>({ endpoint: '/finance/analytics/executive-kpis' });
  const { data: programData, isLoading: programLoading } = useApiQuery<any>({ endpoint: '/finance/analytics/program-economics' });
  const { data: topProgramsData, isLoading: topProgramsLoading } = useApiQuery<any>({ endpoint: '/finance/analytics/top-programs-by-reports?limit=5' });
  const { data: bountyData, isLoading: bountyLoading } = useApiQuery<any>({ endpoint: '/finance/analytics/bounty-economics' });
  const { data: dashboardData, isLoading: dashboardLoading } = useApiQuery<any>({ endpoint: '/dashboard' });
  const { data: triageSeverityData, isLoading: triageSeverityLoading } = useApiQuery<any>({ endpoint: '/triage/valid-reports-by-severity' });
  const { data: recentPaymentsData, isLoading: recentPaymentsLoading } = useApiQuery<any>({ endpoint: '/finance/analytics/recent-payments?limit=10' });

  // Extract KPIs from Finance Analytics
  const platformRevenue = kpisData?.total_revenue || 0;
  const netProfit = kpisData?.net_profit || 0;
  const totalPaid = kpisData?.total_payouts || 0;
  const pendingPayoutsAmount = kpisData?.pending_payouts || 0;
  const cashBalance = kpisData?.cash_balance || 0;
  const revenueGrowth = kpisData?.revenue_growth || 0;
  const activePrograms = kpisData?.active_programs || 0;

  // Get programs and researchers data
  const programs = programData?.programs || [];
  const topPrograms = topProgramsData?.programs || [];
  const recentPayments = recentPaymentsData?.payments || [];
  
  // Get dashboard data for reports and users
  const users = dashboardData?.users || {};
  const reports = dashboardData?.reports || {};

  // Debug logging
  useEffect(() => {
    if (kpisData) {
      console.log('📊 KPIs Data:', kpisData);
      console.log('💰 Platform Revenue:', platformRevenue);
      console.log('💵 Total Paid:', totalPaid);
      console.log('⏳ Pending Payouts:', pendingPayoutsAmount);
    }
    if (dashboardData) {
      console.log('📊 Dashboard Data:', dashboardData);
      console.log('📋 Recent Reports:', dashboardData.recent_reports);
      console.log('📋 Reports Object:', dashboardData.reports);
    }
  }, [kpisData, platformRevenue, totalPaid, pendingPayoutsAmount, dashboardData]);

  // Helper function to format growth indicator
  const formatGrowthText = (value: number, type: 'revenue' | 'pending' | 'paid' | 'reports' | 'researchers') => {
    if (type === 'pending') {
      return 'Awaiting processing';
    }
    if (type === 'reports') {
      const newCount = reports.by_status?.new || 0;
      const triagedCount = reports.by_status?.triaged || 0;
      return `${newCount} new, ${triagedCount} triaged`;
    }
    if (type === 'researchers') {
      const activeCount = users.active_30d || 0;
      return `${activeCount} active this month`;
    }
    // For revenue and paid, show growth if available
    if (value !== 0 && !isNaN(value)) {
      const isPositive = value >= 0;
      return (
        <>
          {isPositive ? '↑' : '↓'} {Math.abs(value).toFixed(1)}% from last month
        </>
      );
    }
    return 'No change from last month';
  };

  // Build a full 12-month scaffold (all months = 0), then fill in real data
  const chartData = useMemo(() => {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const scaffold = months.map(m => ({ date: m, amount: 0, commission: 0 }));
    if (bountyData?.monthly_trend) {
      bountyData.monthly_trend.forEach((trend: any) => {
        const label: string = trend.month_label || trend.month || '';
        // month_label may be like "2026-05" or "May" — match the short name
        const shortMonth = label.length > 3
          ? new Date(label + '-01').toLocaleString('en-US', { month: 'short' })
          : label;
        const idx = months.findIndex(m => m === shortMonth);
        if (idx !== -1) {
          scaffold[idx].amount = trend.total_bounties || 0;
          scaffold[idx].commission = trend.total_commission || 0;
        }
      });
    }
    return scaffold;
  }, [bountyData]);

  // Format severity data for Pie Chart (from bounty economics)
  const severityChartData = useMemo(() => {
    if (!bountyData?.average_bounty_by_severity) return [];
    const colorMap: Record<string, string> = {
      'critical': '#EF4444',
      'high': '#F59E0B',
      'medium': '#FBBF24',
      'low': '#10B981',
    };
    
    return bountyData.average_bounty_by_severity.map((item: any) => ({
      label: item.severity.charAt(0).toUpperCase() + item.severity.slice(1),
      value: Math.round(item.total),
      color: colorMap[item.severity.toLowerCase()] || '#94A3B8',
    }));
  }, [bountyData]);

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
            {/* Platform Revenue */}
            <div className="bg-[#1E293B] rounded-lg p-7 border border-[#334155] shadow-sm min-h-[140px] flex flex-col justify-start">
              <p className="text-lg font-semibold text-[#94A3B8] mb-2">Platform Revenue</p>
              <p className="text-3xl font-extrabold text-[#F8FAFC] mb-1">ETB {platformRevenue.toLocaleString()}</p>
              <p className="text-xs font-medium text-[#10B981]">{formatGrowthText(revenueGrowth, 'revenue')}</p>
            </div>

            {/* Pending Payouts */}
            <div className="bg-[#1E293B] rounded-lg p-7 border border-[#334155] shadow-sm min-h-[140px] flex flex-col justify-start">
              <p className="text-lg font-semibold text-[#94A3B8] mb-2">Pending Payouts</p>
              <p className="text-3xl font-extrabold text-[#F8FAFC] mb-1">ETB {pendingPayoutsAmount.toLocaleString()}</p>
              <p className="text-xs font-medium text-[#94A3B8]">{formatGrowthText(0, 'pending')}</p>
            </div>

            {/* Total Paid Out */}
            <div className="bg-[#1E293B] rounded-lg p-7 border border-[#334155] shadow-sm min-h-[140px] flex flex-col justify-start">
              <p className="text-lg font-semibold text-[#94A3B8] mb-2">Total Paid Out</p>
              <p className="text-3xl font-extrabold text-[#F8FAFC] mb-1">ETB {totalPaid.toLocaleString()}</p>
              <p className="text-xs font-medium text-[#10B981]">{formatGrowthText(revenueGrowth, 'paid')}</p>
            </div>

            {/* Open Reports */}
            <div className="bg-[#1E293B] rounded-lg p-7 border border-[#334155] shadow-sm min-h-[140px] flex flex-col justify-start">
              <p className="text-lg font-semibold text-[#94A3B8] mb-2">Open Reports</p>
              <p className="text-3xl font-extrabold text-[#F8FAFC] mb-1">{reports.total || 0}</p>
              <p className="text-xs font-medium text-[#94A3B8]">{formatGrowthText(0, 'reports')}</p>
            </div>

            {/* Active Researchers */}
            <div className="bg-[#1E293B] rounded-lg p-7 border border-[#334155] shadow-sm min-h-[140px] flex flex-col justify-start">
              <p className="text-lg font-semibold text-[#94A3B8] mb-2">Active Researchers</p>
              <p className="text-3xl font-extrabold text-[#F8FAFC] mb-1">{users.researchers || 0}</p>
              <p className="text-xs font-medium text-[#10B981]">{formatGrowthText(0, 'researchers')}</p>
            </div>
          </div>

          {/* Charts Row - Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">
            {/* Bounty Payment Trend Chart */}
            <div className="lg:col-span-5 bg-[#0F172A] rounded-xl p-5 border border-[#1E3A5F] shadow-lg" style={{ boxShadow: '0 0 32px rgba(6,182,212,0.06)' }}>
              <div className="flex items-center justify-between mb-1">
                <div>
                  <h2 className="text-base font-semibold text-[#F8FAFC]">Bounty Payment Trend</h2>
                  <p className="text-xs text-[#475569] mt-0.5">Last 12 Months</p>
                </div>
                <select className="px-2 py-1 bg-[#1E293B] border border-[#334155] rounded text-xs text-[#94A3B8] focus:outline-none focus:ring-1 focus:ring-[#3B82F6]">
                  <option>Last 12 Months</option>
                  <option>Last 6 Months</option>
                  <option>Last 3 Months</option>
                </select>
              </div>
              {bountyLoading ? (
                <div className="h-64 flex items-center justify-center">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-8 h-8 border-2 border-[#10B981] border-t-transparent rounded-full animate-spin" />
                    <p className="text-xs text-[#64748B]">Loading trend data…</p>
                  </div>
                </div>
              ) : (
                <BountyTrendChart data={chartData} height={270} />
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

            {/* Top Programs by Reports */}
            <div className="lg:col-span-3 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="flex items-center justify-between p-4 border-b border-[#334155]">
                <h2 className="text-sm font-semibold text-[#F8FAFC]">Top Programs by Reports</h2>
                <Link href="/finance/reports">
                  <Button variant="ghost" size="xs">View all</Button>
                </Link>
              </div>
              <div className="divide-y divide-[#334155]">
                {topProgramsLoading ? (
                  <div className="py-8 text-center text-[#64748B] text-xs">Loading...</div>
                ) : topPrograms.length > 0 ? (
                  topPrograms.map((program: any, index: number) => (
                    <div key={program.program_id || index} className="flex items-center justify-between p-3 hover:bg-[#0F172A]/50 transition-colors">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <span className="w-5 h-5 rounded-full bg-[#3B82F6]/20 text-[#3B82F6] text-xs font-bold flex items-center justify-center flex-shrink-0">{index + 1}</span>
                        <span className="text-sm text-[#F8FAFC] truncate">{program.program_name}</span>
                      </div>
                      <span className="text-sm font-bold text-[#3B82F6] ml-3 flex-shrink-0">{program.report_count} reports</span>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-[#64748B] text-xs">No programs with reports yet</div>
                )}
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
              {recentPaymentsLoading ? (
                <div className="py-8 text-center text-[#64748B] text-sm">Loading...</div>
              ) : recentPayments.length === 0 ? (
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
                      {recentPayments.map((payment: any) => {
                        const severityColor: Record<string, string> = {
                          critical: 'bg-[#EF4444] text-white',
                          high:     'bg-[#F59E0B] text-white',
                          medium:   'bg-[#FBBF24] text-white',
                          low:      'bg-[#10B981] text-white',
                        };
                        const statusColor: Record<string, string> = {
                          completed:  'bg-[#10B981] text-white',
                          approved:   'bg-[#3B82F6] text-white',
                          processing: 'bg-[#F59E0B] text-white',
                          pending:    'bg-[#94A3B8] text-white',
                        };
                        const displayDate = payment.completed_at || payment.created_at;
                        return (
                          <tr key={payment.payment_id} className="border-b border-[#334155]/50 hover:bg-[#334155]/20 transition-colors">
                            <td className="py-2.5 px-2">
                              <div className="flex items-center gap-2">
                                <div className="w-7 h-7 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white text-xs font-bold">
                                  {(payment.researcher_name || 'R')[0].toUpperCase()}
                                </div>
                                <span className="text-xs text-[#F8FAFC] font-medium">{payment.researcher_name || 'Unknown'}</span>
                              </div>
                            </td>
                            <td className="py-2.5 px-2 text-xs text-[#94A3B8] max-w-[120px] truncate" title={payment.report_title}>
                              {payment.report_number ? `#${payment.report_number}` : payment.report_title}
                            </td>
                            <td className="py-2.5 px-2 text-xs text-[#94A3B8] max-w-[100px] truncate" title={payment.program_name}>
                              {payment.program_name}
                            </td>
                            <td className="py-2.5 px-2">
                              {payment.severity ? (
                                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${severityColor[payment.severity.toLowerCase()] || 'bg-[#64748B] text-white'}`}>
                                  {payment.severity}
                                </span>
                              ) : <span className="text-xs text-[#64748B]">—</span>}
                            </td>
                            <td className="py-2.5 px-2 text-right text-xs font-bold text-[#10B981]">
                              ETB {payment.researcher_amount.toLocaleString()}
                            </td>
                            <td className="py-2.5 px-2 text-center">
                              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${statusColor[payment.status] || 'bg-[#64748B] text-white'}`}>
                                {payment.status}
                              </span>
                            </td>
                            <td className="py-2.5 px-2 text-right text-xs text-[#94A3B8]">
                              {displayDate ? new Date(displayDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="flex items-center justify-between p-4 border-b border-[#334155]">
                <h2 className="text-sm font-semibold text-[#F8FAFC]">Recent Reports</h2>
                <Button variant="ghost" size="xs">View all</Button>
              </div>
              {dashboardLoading ? (
                <div className="py-4 text-center text-[#64748B] text-xs">Loading...</div>
              ) : (
                <div className="divide-y divide-[#334155]">
                {dashboardData?.recent_reports && dashboardData.recent_reports.length > 0 ? (
                  dashboardData.recent_reports.slice(0, 5).map((report: any, index: number) => (
                    <div key={index} className="flex items-start justify-between gap-3 p-3 hover:bg-[#0F172A]/50 transition-colors">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-[#F8FAFC] leading-tight">{report.title}</p>
                        <p className="text-xs text-[#94A3B8] mt-1 leading-tight">{report.program_name || 'Unknown Program'}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase flex-shrink-0 ${
                        report.assigned_severity === 'critical' ? 'bg-[#EF4444] text-white' :
                        report.assigned_severity === 'high' ? 'bg-[#F59E0B] text-white' :
                        report.assigned_severity === 'medium' ? 'bg-[#FBBF24] text-white' :
                        'bg-[#10B981] text-white'
                      }`}>
                        {report.assigned_severity || 'N/A'}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-[#64748B] text-xs">No recent reports</div>
                )}
              </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/finance/payments" className="group">
              <div className="relative bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-2xl p-6 hover:border-[#3B82F6] hover:shadow-xl hover:shadow-[#3B82F6]/20 transition-all duration-300 cursor-pointer overflow-hidden">
                {/* Animated background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#3B82F6]/0 to-[#3B82F6]/0 group-hover:from-[#3B82F6]/5 group-hover:to-[#2563EB]/10 transition-all duration-300" />
                
                <div className="relative flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-[#F8FAFC] mb-1 group-hover:text-[#3B82F6] transition-colors">All Payments</h3>
                    <p className="text-sm text-[#94A3B8] leading-relaxed mb-3">View and manage all payment transactions</p>
                    <div className="flex items-center gap-2 text-[#3B82F6] font-semibold text-sm group-hover:gap-3 transition-all">
                      <span>View payments</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/finance/payouts?status=requested" className="group">
              <div className="relative bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-2xl p-6 hover:border-[#F59E0B] hover:shadow-xl hover:shadow-[#F59E0B]/20 transition-all duration-300 cursor-pointer overflow-hidden">
                {/* Animated background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#F59E0B]/0 to-[#F59E0B]/0 group-hover:from-[#F59E0B]/5 group-hover:to-[#D97706]/10 transition-all duration-300" />
                
                <div className="relative flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#F59E0B] to-[#D97706] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-[#F8FAFC] mb-1 group-hover:text-[#F59E0B] transition-colors">Pending Payouts</h3>
                    <p className="text-sm text-[#94A3B8] leading-relaxed mb-3">Review and approve payout requests</p>
                    <div className="flex items-center gap-2 text-[#F59E0B] font-semibold text-sm group-hover:gap-3 transition-all">
                      <span>Review now</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/finance/reports" className="group">
              <div className="relative bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-[#334155] rounded-2xl p-6 hover:border-[#10B981] hover:shadow-xl hover:shadow-[#10B981]/20 transition-all duration-300 cursor-pointer overflow-hidden">
                {/* Animated background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#10B981]/0 to-[#10B981]/0 group-hover:from-[#10B981]/5 group-hover:to-[#059669]/10 transition-all duration-300" />
                
                <div className="relative flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#10B981] to-[#059669] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-[#F8FAFC] mb-1 group-hover:text-[#10B981] transition-colors">Financial Reports</h3>
                    <p className="text-sm text-[#94A3B8] leading-relaxed mb-3">Generate and download reports</p>
                    <div className="flex items-center gap-2 text-[#10B981] font-semibold text-sm group-hover:gap-3 transition-all">
                      <span>View reports</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
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
