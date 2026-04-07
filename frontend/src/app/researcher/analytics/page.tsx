'use client';

import { useState, useMemo } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Spinner from '@/components/ui/Spinner';
import Tabs from '@/components/ui/Tabs';
import PieChart from '@/components/ui/PieChart';
import BarChart from '@/components/ui/BarChart';

interface AnalyticsData {
  researcher_id: string;
  period: string;
  start_date: string;
  end_date: string;
  metrics: {
    total_reports: number;
    valid_reports: number;
    invalid_reports: number;
    success_rate: number;
    earnings: number;
    reputation_score: number;
    rank: number;
  };
  severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  top_vulnerability_types: Array<{
    type: string;
    count: number;
  }>;
  monthly_trend: Array<{
    month: string;
    total_reports: number;
    valid_reports: number;
    earnings: number;
  }>;
}

export default function ResearcherAnalyticsPage() {
  const user = useAuthStore((state) => state.user);
  const [timePeriod, setTimePeriod] = useState('1year');

  const { data: analyticsData, isLoading, error, refetch } = useApiQuery<AnalyticsData>(
    `/analytics/my-performance?time_period=${timePeriod}`,
    { 
      enabled: !!user
    }
  );

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatCurrencyWhole = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.ceil(amount));
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-[#10b981]';
    if (rate >= 60) return 'text-[#f59e0b]';
    return 'text-[#ef4444]';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-[#dc2626] text-white';
      case 'high': return 'bg-[#ea580c] text-white';
      case 'medium': return 'bg-[#d97706] text-white';
      case 'low': return 'bg-[#65a30d] text-white';
      default: return 'bg-[#6b7280] text-white';
    }
  };

  const getSeverityChartColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#d97706';
      case 'low': return '#65a30d';
      default: return '#6b7280';
    }
  };

  const timePeriodOptions = [
    { value: '7days', label: '7 Days' },
    { value: '30days', label: '30 Days' },
    { value: '3months', label: '3 Months' },
    { value: '6months', label: '6 Months' },
    { value: '1year', label: '1 Year' },
  ];

  // Memoize pie chart data to prevent unnecessary re-renders
  const pieChartData = useMemo(() => {
    if (!analyticsData) return [];
    return Object.entries(analyticsData.severity_distribution).map(([severity, count]) => ({
      label: severity.charAt(0).toUpperCase() + severity.slice(1),
      value: count,
      color: getSeverityChartColor(severity)
    }));
  }, [analyticsData]);

  // Memoize bar chart data for monthly trends
  const totalReportsChartData = useMemo(() => {
    if (!analyticsData) return [];
    return analyticsData.monthly_trend.map(month => {
      // Format month label from "2024-04" to "Apr 2024" or use as-is if already formatted
      let label = month.month;
      if (month.month.match(/^\d{4}-\d{2}$/)) {
        const [year, monthNum] = month.month.split('-');
        const date = new Date(parseInt(year), parseInt(monthNum) - 1);
        label = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      }
      
      return {
        label,
        value: Math.floor(month.total_reports),
        color: '#3b82f6' // Blue
      };
    });
  }, [analyticsData]);

  const validReportsChartData = useMemo(() => {
    if (!analyticsData) return [];
    return analyticsData.monthly_trend.map(month => {
      // Format month label
      let label = month.month;
      if (month.month.match(/^\d{4}-\d{2}$/)) {
        const [year, monthNum] = month.month.split('-');
        const date = new Date(parseInt(year), parseInt(monthNum) - 1);
        label = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      }
      
      return {
        label,
        value: Math.floor(month.valid_reports),
        color: '#10b981' // Green
      };
    });
  }, [analyticsData]);

  const earningsChartData = useMemo(() => {
    if (!analyticsData) return [];
    return analyticsData.monthly_trend.map(month => {
      // Format month label
      let label = month.month;
      if (month.month.match(/^\d{4}-\d{2}$/)) {
        const [year, monthNum] = month.month.split('-');
        const date = new Date(parseInt(year), parseInt(monthNum) - 1);
        label = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      }
      
      return {
        label,
        value: month.earnings,
        color: '#ef2330' // Red
      };
    });
  }, [analyticsData]);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Analytics"
          subtitle="Track your performance, earnings trends, and specialization insights."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {/* Time Period Selector */}
          <div className="mb-6 flex justify-end items-center">
            <select
              value={timePeriod}
              onChange={(e) => setTimePeriod(e.target.value)}
              className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
            >
              {timePeriodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              <p className="font-semibold">Error</p>
              <p className="mt-1">{error.message}</p>
            </div>
          )}

          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Spinner size="lg" />
            </div>
          ) : analyticsData ? (
            <div className="space-y-12">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="rounded-2xl bg-[#faf6f1] p-5 text-center">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Total Reports
                  </p>
                  <p className="text-2xl font-bold text-[#2d2a26]">
                    {Math.floor(analyticsData.metrics.total_reports)}
                  </p>
                  <p className="text-xs text-[#6d6760] mt-1">
                    {Math.floor(analyticsData.metrics.valid_reports)} valid, {Math.floor(analyticsData.metrics.invalid_reports)} invalid
                  </p>
                </div>

                <div className="rounded-2xl bg-[#faf6f1] p-5 text-center">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Success Rate
                  </p>
                  <p className={`text-2xl font-bold ${getSuccessRateColor(analyticsData.metrics.success_rate)}`}>
                    {analyticsData.metrics.success_rate}%
                  </p>
                  <p className="text-xs text-[#6d6760] mt-1">
                    Valid reports ratio
                  </p>
                </div>

                <div className="rounded-2xl bg-[#faf6f1] p-5 text-center">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Total Earnings
                  </p>
                  <p className="text-2xl font-bold text-[#2d2a26]">
                    {formatCurrency(analyticsData.metrics.earnings)}
                  </p>
                  <p className="text-xs text-[#6d6760] mt-1">
                    In selected period
                  </p>
                </div>

                <div className="rounded-2xl bg-[#faf6f1] p-5 text-center">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Current Rank
                  </p>
                  <p className="text-2xl font-bold text-[#2d2a26]">
                    #{analyticsData.metrics.rank || 'Unranked'}
                  </p>
                  <p className="text-xs text-[#6d6760] mt-1">
                    {analyticsData.metrics.reputation_score.toFixed(1)} reputation
                  </p>
                </div>
              </div>

              <Tabs
                tabs={[
                  { id: 'overview', label: 'Overview' },
                  { id: 'trends', label: 'Trends' },
                  { id: 'specialization', label: 'Specialization' },
                ]}
                defaultTab="overview"
              >
                {/* Overview Tab */}
                <div data-tab="overview" className="space-y-6">
                  {/* Severity Distribution */}
                  <div className="rounded-2xl bg-[#faf6f1] p-6">
                    <h3 className="text-lg font-bold text-[#2d2a26] mb-6 text-center">Severity Distribution</h3>
                    <div className="flex justify-center">
                      <PieChart
                        data={pieChartData}
                        size={240}
                        showLegend={true}
                      />
                    </div>
                  </div>

                  {/* Top Vulnerability Types */}
                  <div className="rounded-2xl bg-[#faf6f1] p-6">
                    <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Top Vulnerability Types</h3>
                    {analyticsData.top_vulnerability_types.length > 0 ? (
                      <div className="space-y-3">
                        {analyticsData.top_vulnerability_types.map((vuln, index) => (
                          <div key={vuln.type} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center text-sm font-bold">
                                {index + 1}
                              </div>
                              <span className="text-sm font-medium text-[#2d2a26]">{vuln.type}</span>
                            </div>
                            <span className="text-sm font-bold text-[#2d2a26]">{Math.floor(vuln.count)} reports</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-[#6d6760]">No vulnerability data available for this period.</p>
                    )}
                  </div>
                </div>

                {/* Trends Tab */}
                <div data-tab="trends" className="space-y-6">
                  {analyticsData.monthly_trend.length > 0 ? (
                    <>
                      {/* Total Reports Chart */}
                      <div className="rounded-2xl bg-[#faf6f1] p-6">
                        <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Total Reports per Month</h3>
                        <BarChart
                          data={totalReportsChartData}
                          height={250}
                          showValues={true}
                        />
                      </div>

                      {/* Valid Reports Chart */}
                      <div className="rounded-2xl bg-[#faf6f1] p-6">
                        <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Valid Reports per Month</h3>
                        <BarChart
                          data={validReportsChartData}
                          height={250}
                          showValues={true}
                        />
                      </div>

                      {/* Earnings Chart */}
                      <div className="rounded-2xl bg-[#faf6f1] p-6">
                        <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Earnings per Month (ETB)</h3>
                        <BarChart
                          data={earningsChartData}
                          height={250}
                          showValues={true}
                          valueFormatter={formatCurrencyWhole}
                          yAxisInterval={5000}
                        />
                      </div>
                    </>
                  ) : (
                    <div className="rounded-2xl bg-[#faf6f1] p-6">
                      <p className="text-sm text-[#6d6760]">No trend data available for this period.</p>
                    </div>
                  )}
                </div>

                {/* Specialization Tab */}
                <div data-tab="specialization" className="space-y-6">
                  <div className="rounded-2xl bg-[#faf6f1] p-6">
                    <h3 className="text-lg font-bold text-[#2d2a26] mb-4">Your Specializations</h3>
                    {analyticsData.top_vulnerability_types.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {analyticsData.top_vulnerability_types.map((vuln) => {
                          const percentage = analyticsData.metrics.total_reports > 0 
                            ? (vuln.count / analyticsData.metrics.total_reports * 100).toFixed(1)
                            : '0';
                          
                          return (
                            <div key={vuln.type} className="rounded-xl bg-white p-4 border border-[#e6ddd4]">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-semibold text-[#2d2a26]">{vuln.type}</h4>
                                <span className="text-sm font-bold text-[#ef2330]">{percentage}%</span>
                              </div>
                              <div className="w-full bg-[#f3f0eb] rounded-full h-2">
                                <div 
                                  className="bg-[#ef2330] h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${percentage}%` }}
                                ></div>
                              </div>
                              <p className="text-xs text-[#6d6760] mt-2">{vuln.count} reports submitted</p>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-[#6d6760]">No specialization data available. Submit more reports to see your areas of expertise.</p>
                    )}
                  </div>
                </div>
              </Tabs>
            </div>
          ) : (
            <div className="rounded-2xl bg-[#faf6f1] p-8 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                No Analytics Data
              </p>
              <p className="mt-2 text-sm text-[#6d6760]">
                Submit some reports to start seeing your performance analytics
              </p>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
