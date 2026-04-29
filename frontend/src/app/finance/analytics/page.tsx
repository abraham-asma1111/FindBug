'use client';

import { useEffect, useMemo, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import LineChart from '@/components/ui/LineChart';
import BarChart from '@/components/ui/BarChart';
import Button from '@/components/ui/Button';

export default function FinanceAnalyticsPage() {
  const user = useAuthStore((state) => state.user);
  const [dateRange, setDateRange] = useState('May 1 - May 31, 2024');
  const [selectedProgram, setSelectedProgram] = useState('All Programs');
  const [selectedCurrency, setSelectedCurrency] = useState('USD - US Dollar');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: analyticsData, isLoading } = useApiQuery<any>({
    endpoint: '/payments/analytics?range=30d',
  });

  const stats = analyticsData?.stats || {};
  const paymentTrends = analyticsData?.payment_trends || [];
  const topOrganizations = analyticsData?.top_organizations || [];
  const severityDistribution = analyticsData?.severity_distribution || [];

  // Format chart data
  const spendingChartData = useMemo(() => {
    return paymentTrends.map((trend: any) => ({
      date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      amount: trend.amount,
    }));
  }, [paymentTrends]);

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

  // Calculate KPIs from real data
  const totalSpend = stats.total_amount || 0;
  const totalPaid = stats.total_amount || 0;
  const totalCommission = stats.total_commission || 0;
  const avgPayment = stats.avg_payment || 0;
  
  // Calculate outstanding payouts (this would come from wallet/payout data)
  const outstandingPayouts = 0; // TODO: Get from wallet service
  const budgetRemaining = 0; // TODO: Get from organization budget data
  const burnRate = totalSpend; // Monthly burn rate = total spend in period

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finance Analytics"
          subtitle="Comprehensive insights into your financial performance"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Header with Filters */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <h2 className="text-xl font-bold text-[#F8FAFC]">Finance Analytics</h2>
                <Button variant="ghost" size="xs" className="w-5 h-5 p-0 rounded-full">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </Button>
              </div>
              <p className="text-sm text-[#94A3B8]">Deep insights into your financial performance across programs and time.</p>
            </div>
            <Button variant="secondary" size="sm" className="gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export
            </Button>
          </div>

          {/* Filters Row */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-[#94A3B8] uppercase">Date Range</label>
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-sm text-[#F8FAFC] hover:border-[#475569] transition"
              >
                <option>May 1 - May 31, 2024</option>
                <option>Last 30 Days</option>
                <option>Last 90 Days</option>
                <option>Last 6 Months</option>
                <option>Last Year</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-[#94A3B8] uppercase">Programs</label>
              <select 
                value={selectedProgram}
                onChange={(e) => setSelectedProgram(e.target.value)}
                className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-sm text-[#F8FAFC] hover:border-[#475569] transition"
              >
                <option>All Programs</option>
                <option>Web Application Program</option>
                <option>Mobile Security Program</option>
                <option>API Security Program</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-[#94A3B8] uppercase">Currency</label>
              <select 
                value={selectedCurrency}
                onChange={(e) => setSelectedCurrency(e.target.value)}
                className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-sm text-[#F8FAFC] hover:border-[#475569] transition"
              >
                <option>USD - US Dollar</option>
                <option>ETB - Ethiopian Birr</option>
              </select>
            </div>
          </div>

          {/* KPI Cards - Compact */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-5">
            {/* Total Spend */}
            <div className="bg-[#1E293B] rounded-lg p-3 border border-[#334155] hover:border-[#475569] transition">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-[#3B82F6]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Total Spend</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${totalSpend.toLocaleString()}.00</p>
              <p className="text-xs text-[#10B981] font-medium">↑ 12.5% <span className="text-[#64748B]">vs Apr 1 - Apr 30</span></p>
            </div>

            {/* Total Paid */}
            <div className="bg-[#1E293B] rounded-lg p-3 border border-[#334155] hover:border-[#475569] transition">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-[#10B981]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Total Paid</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${totalPaid.toLocaleString()}.00</p>
              <p className="text-xs text-[#10B981] font-medium">↑ 10.3% <span className="text-[#64748B]">vs Apr 1 - Apr 30</span></p>
            </div>

            {/* Outstanding Payouts */}
            <div className="bg-[#1E293B] rounded-lg p-3 border border-[#334155] hover:border-[#475569] transition">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-[#F59E0B]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Outstanding Payouts</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${outstandingPayouts.toLocaleString()}.00</p>
              <p className="text-xs text-[#F59E0B] font-medium">↑ 8.2% <span className="text-[#64748B]">vs Apr 1 - Apr 30</span></p>
            </div>

            {/* Budget Remaining */}
            <div className="bg-[#1E293B] rounded-lg p-3 border border-[#334155] hover:border-[#475569] transition">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-[#3B82F6]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Budget Remaining</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${budgetRemaining.toLocaleString()}.00</p>
              <p className="text-xs text-[#10B981] font-medium">↑ 8.6% <span className="text-[#64748B]">vs Apr 1 - Apr 30</span></p>
            </div>

            {/* Burn Rate (Monthly) */}
            <div className="bg-[#1E293B] rounded-lg p-3 border border-[#334155] hover:border-[#475569] transition">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-[#8B5CF6]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Burn Rate (Monthly)</p>
              <p className="text-xl font-bold text-[#F8FAFC] mb-0.5">${burnRate.toLocaleString()}.00</p>
              <p className="text-xs text-[#EF4444] font-medium">↑ 15.7% <span className="text-[#64748B]">vs Apr 1 - Apr 30</span></p>
            </div>
          </div>

          {/* Main Content Grid - Table + Side Panel */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-5">
            {/* Left - Spending by Program Table */}
            <div className="lg:col-span-8 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="p-4 border-b border-[#334155] flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-[#F8FAFC]">Spending by Program</h3>
                  <p className="text-xs text-[#64748B] mt-0.5">Click on any metric row to see more details.</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#94A3B8]">View by:</span>
                  <div className="flex items-center gap-1 bg-[#0F172A] rounded-lg p-1">
                    <Button variant="secondary" size="xs">Program</Button>
                    <Button variant="ghost" size="xs">Severity</Button>
                    <Button variant="ghost" size="xs">Researcher</Button>
                  </div>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#334155]">
                      <th className="text-left py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Program</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Total Spend</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Total Paid</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Outstanding Payouts</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Reports</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Avg. Payout</th>
                      <th className="text-right py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Budget</th>
                      <th className="text-center py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Severity</th>
                      <th className="text-center py-2.5 px-4 text-xs font-bold text-[#94A3B8] uppercase tracking-wide whitespace-nowrap">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={9} className="py-8 text-center text-[#64748B] text-sm">Loading...</td>
                      </tr>
                    ) : (
                      [
                        { name: 'Web Application Program', spend: 48750, paid: 44250, outstanding: 4500, reports: 320, avg: 152.34, budget: 60000, severity: 'High', trend: 'up' },
                        { name: 'Mobile Security Program', spend: 18450, paid: 16850, outstanding: 1600, reports: 180, avg: 102.50, budget: 30000, severity: 'Medium', trend: 'up' },
                        { name: 'API Security Program', spend: 8750, paid: 8750, outstanding: 0, reports: 95, avg: 92.11, budget: 18000, severity: 'Low', trend: 'down' },
                        { name: 'Infrastructure Program', spend: 2350, paid: 2150, outstanding: 200, reports: 28, avg: 83.93, budget: 10000, severity: 'Low', trend: 'neutral' },
                        { name: 'Other Programs', spend: 650, paid: 450, outstanding: 200, reports: 7, avg: 92.86, budget: 5000, severity: 'Low', trend: 'neutral' },
                      ].map((program, index) => (
                        <tr key={index} className="border-b border-[#334155]/50 hover:bg-[#0F172A]/50 transition-colors cursor-pointer">
                          <td className="py-2.5 px-4 text-sm text-[#F8FAFC] font-medium">{program.name}</td>
                          <td className="py-2.5 px-4 text-right text-sm font-bold text-[#F8FAFC]">${program.spend.toLocaleString()}.00</td>
                          <td className="py-2.5 px-4 text-right text-sm text-[#94A3B8]">${program.paid.toLocaleString()}.00</td>
                          <td className="py-2.5 px-4 text-right text-sm text-[#94A3B8]">${program.outstanding.toLocaleString()}.00</td>
                          <td className="py-2.5 px-4 text-right text-sm text-[#94A3B8]">{program.reports}</td>
                          <td className="py-2.5 px-4 text-right text-sm text-[#94A3B8]">${program.avg}</td>
                          <td className="py-2.5 px-4 text-right text-sm text-[#94A3B8]">${program.budget.toLocaleString()}.00</td>
                          <td className="py-2.5 px-4 text-center">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                              program.severity === 'High' ? 'bg-[#EF4444]/10 text-[#EF4444]' :
                              program.severity === 'Medium' ? 'bg-[#F59E0B]/10 text-[#F59E0B]' :
                              'bg-[#10B981]/10 text-[#10B981]'
                            }`}>
                              {program.severity}
                            </span>
                          </td>
                          <td className="py-2.5 px-4 text-center">
                            <div className="flex items-center justify-center">
                              {program.trend === 'up' ? (
                                <svg className="w-12 h-6 text-[#10B981]" viewBox="0 0 48 24" fill="none">
                                  <path d="M0 20 L12 16 L24 12 L36 6 L48 2" stroke="currentColor" strokeWidth="2" fill="none"/>
                                </svg>
                              ) : program.trend === 'down' ? (
                                <svg className="w-12 h-6 text-[#EF4444]" viewBox="0 0 48 24" fill="none">
                                  <path d="M0 2 L12 6 L24 12 L36 16 L48 20" stroke="currentColor" strokeWidth="2" fill="none"/>
                                </svg>
                              ) : (
                                <svg className="w-12 h-6 text-[#64748B]" viewBox="0 0 48 24" fill="none">
                                  <path d="M0 12 L48 12" stroke="currentColor" strokeWidth="2" fill="none"/>
                                </svg>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div className="p-3 border-t border-[#334155] flex items-center justify-between">
                <p className="text-xs text-[#64748B]">Showing 1 to 5 of 5 programs</p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="xs" className="w-7 h-7 p-0">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </Button>
                  <Button variant="secondary" size="xs" className="w-7 h-7 p-0">1</Button>
                  <Button variant="outline" size="xs" className="w-7 h-7 p-0">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                  <select className="ml-2 px-2 py-1 bg-[#0F172A] border border-[#334155] rounded text-xs text-[#F8FAFC]">
                    <option>10 / page</option>
                    <option>25 / page</option>
                    <option>50 / page</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Right - Web Application Program Detail Card */}
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="p-4 border-b border-[#334155] flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-[#F8FAFC]">Web Application Program</h3>
                  <p className="text-xs text-[#64748B] mt-0.5">Detailed metrics and transactions</p>
                </div>
                <Button variant="ghost" size="xs" className="p-0">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </Button>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-[#334155]">
                    <span className="text-xs font-semibold text-[#94A3B8] uppercase">Total Transactions</span>
                    <span className="text-sm font-bold text-[#F8FAFC]">187</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#64748B]">Total Amount</span>
                    <span className="text-xs font-bold text-[#3B82F6]">$48,750.00</span>
                  </div>
                  
                  {[
                    { id: 'TXN-87452', type: 'Payout', amount: 750, status: 'Paid', date: 'May 31, 2024' },
                    { id: 'TXN-87451', type: 'Payout', amount: 500, status: 'Paid', date: 'May 30, 2024' },
                    { id: 'TXN-87449', type: 'Payout', amount: 1000, status: 'Paid', date: 'May 29, 2024' },
                    { id: 'TXN-87449', type: 'Platform Fee', amount: 125, status: 'Paid', date: 'May 29, 2024' },
                    { id: 'TXN-87448', type: 'Payout', amount: 300, status: 'Paid', date: 'May 28, 2024' },
                  ].map((txn, index) => (
                    <div key={index} className="py-2.5 border-t border-[#334155]">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-[#F8FAFC]">{txn.id}</span>
                        <span className="text-xs font-bold text-[#F8FAFC]">${txn.amount.toLocaleString()}.00</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-[#64748B]">{txn.type}</span>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-[#10B981]/10 text-[#10B981]">
                            {txn.status}
                          </span>
                          <span className="text-xs text-[#64748B]">{txn.date}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="ghost" size="xs" className="gap-1">
                  View all transactions
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </div>
            </div>
          </div>

          {/* Bottom Section - Charts and Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-5">
            {/* Spending Over Time Chart */}
            <div className="lg:col-span-5 bg-[#1E293B] rounded-lg border border-[#334155] p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-[#F8FAFC]">Spending Over Time</h3>
                <select className="px-2 py-1 bg-[#0F172A] border border-[#334155] rounded text-xs text-[#F8FAFC]">
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                </select>
              </div>
              <div className="mb-2">
                <span className="text-xs text-[#64748B]">Total Spend (USD)</span>
              </div>
              {isLoading || spendingChartData.length === 0 ? (
                <div className="h-40 flex items-center justify-center text-[#64748B]">
                  <p className="text-sm">{isLoading ? 'Loading...' : 'No data'}</p>
                </div>
              ) : (
                <LineChart
                  data={spendingChartData}
                  xKey="date"
                  lines={[{ key: 'amount', color: '#8B5CF6', name: 'Total Spend' }]}
                  height={160}
                />
              )}
            </div>

            {/* Spending by Severity Chart */}
            <div className="lg:col-span-4 bg-[#1E293B] rounded-lg border border-[#334155] p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-[#F8FAFC]">Spending by Severity</h3>
                <select className="px-2 py-1 bg-[#0F172A] border border-[#334155] rounded text-xs text-[#F8FAFC]">
                  <option>All Time</option>
                  <option>This Month</option>
                  <option>Last Month</option>
                </select>
              </div>
              <div className="mb-2">
                <span className="text-xs text-[#64748B]">Amount (USD)</span>
              </div>
              {isLoading || severityChartData.length === 0 ? (
                <div className="h-40 flex items-center justify-center text-[#64748B]">
                  <p className="text-sm">{isLoading ? 'Loading...' : 'No data'}</p>
                </div>
              ) : (
                <BarChart
                  data={severityChartData}
                  height={160}
                />
              )}
            </div>

            {/* Expense Breakdown */}
            <div className="lg:col-span-3 bg-[#1E293B] rounded-lg border border-[#334155]">
              <div className="p-4 border-b border-[#334155]">
                <h3 className="text-sm font-bold text-[#F8FAFC]">Expense Breakdown</h3>
              </div>
              <div className="divide-y divide-[#334155]">
                {[
                  { category: 'Bounty Payouts', amount: 72450, percent: 91.8, trend: '↑ 12.1%', up: true },
                  { category: 'Platform Fees', amount: 6500, percent: 8.2, trend: '↑ 15.2%', up: true },
                  { category: 'Payment Processing Fees', amount: 1250, percent: 1.6, trend: '↑ 8.7%', up: true },
                  { category: 'Refunds', amount: 500, percent: 0.6, trend: '↓ 12.4%', up: false },
                  { category: 'Other Charges', amount: 250, percent: 0.3, trend: '↓ 5.1%', up: false },
                ].map((expense, index) => (
                  <div key={index} className="p-3 hover:bg-[#0F172A]/50 transition-colors">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs font-medium text-[#F8FAFC]">{expense.category}</span>
                      <span className="text-xs font-bold text-[#F8FAFC]">${expense.amount.toLocaleString()}.00</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#64748B]">{expense.percent}% of Total</span>
                      <span className={`text-xs font-medium ${expense.up ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                        {expense.trend}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t border-[#334155]">
                <Button variant="ghost" size="xs" className="w-full gap-1">
                  View full breakdown
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </div>
            </div>
          </div>

          {/* Financial Insights & Alerts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-gradient-to-br from-[#EF4444]/10 to-[#DC2626]/5 border border-[#EF4444]/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-[#EF4444] rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold text-[#F8FAFC] mb-1">Budget Alert</p>
                  <p className="text-xs text-[#94A3B8] leading-relaxed">Web Application Program has used 81% of its budget.</p>
                  <Button variant="warning" size="xs" className="gap-1">
                    View program
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#D97706]/5 border border-[#F59E0B]/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-[#F59E0B] rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold text-[#F8FAFC] mb-1">High Burn Rate</p>
                  <p className="text-xs text-[#94A3B8] leading-relaxed">API Security Program burn rate is 4.5% higher than last month.</p>
                  <Button variant="ghost" size="xs" className="gap-1">
                    View report
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#2563EB]/5 border border-[#3B82F6]/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-[#3B82F6] rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold text-[#F8FAFC] mb-1">Cost Efficiency</p>
                  <p className="text-xs text-[#94A3B8] leading-relaxed">Average payout per report decreased by 4.5% this month.</p>
                  <Button variant="ghost" size="xs" className="gap-1">
                    View details
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#10B981]/10 to-[#059669]/5 border border-[#10B981]/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-[#10B981] rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold text-[#F8FAFC] mb-1">Top Performer</p>
                  <p className="text-xs text-[#94A3B8] leading-relaxed">API Security Program has the highest ROI this month.</p>
                  <Button variant="ghost" size="xs" className="gap-1">
                    View analytics
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
