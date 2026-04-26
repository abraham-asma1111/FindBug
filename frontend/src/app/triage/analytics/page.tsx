'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';


interface TriageStats {
  total_reports: number;
  pending_triage: number;
  triaged_today: number;
  avg_triage_time_hours: number;
  status_breakdown: {
    new: number;
    triaged: number;
    valid: number;
    invalid: number;
    duplicate: number;
    resolved: number;
  };
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  recent_activity: Array<{
    date: string;
    triaged_count: number;
    avg_time_hours: number;
  }>;
  triage_performance: {
    total_triaged_this_week: number;
    total_triaged_last_week: number;
    avg_response_time_hours: number;
    accuracy_rate: number;
  };
  top_researchers: Array<{
    researcher_id: string;
    email: string;
    total_reports: number;
    valid_reports: number;
  }>;
  top_programs: Array<{
    program_id: string;
    name: string;
    pending_count: number;
    total_reports: number;
  }>;
}

export default function TriageAnalyticsPage() {
  const user = useAuthStore((state) => state.user);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: stats, isLoading, error, refetch } = useApiQuery<TriageStats>({
    endpoint: '/triage/statistics',
  });

  const handleRefresh = async () => {
    await refetch();
    setLastUpdated(new Date());
  };

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Triage Analytics"
          subtitle="Comprehensive queue performance and validation metrics"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Refresh Button */}
          <div className="mb-6 flex justify-end items-center gap-3">
            <p className="text-xs text-[#94A3B8]">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
            <Button
              onClick={handleRefresh}
              variant="outline"
              size="sm"
              disabled={isLoading}
            >
              Refresh
            </Button>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading analytics...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#EF4444]">Failed to load analytics</p>
            </div>
          ) : stats && stats.total_reports !== undefined ? (
            <div className="space-y-6">
              {/* Status Overview Cards - Enhanced with gradients and icons */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {/* New Reports */}
                <div className="relative overflow-hidden bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] hover:border-[#EF4444] transition-all group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#EF4444]/10 rounded-full blur-3xl group-hover:bg-[#EF4444]/20 transition-all"></div>
                  <div className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs font-bold text-[#EF4444] uppercase tracking-wider">New Reports</span>
                    </div>
                    <p className="text-5xl font-bold text-[#EF4444] mb-2">
                      {stats.status_breakdown?.new || 0}
                    </p>
                    <p className="text-sm text-[#94A3B8]">Awaiting initial review</p>
                  </div>
                </div>

                {/* In Triage */}
                <div className="relative overflow-hidden bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] hover:border-[#F59E0B] transition-all group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#F59E0B]/10 rounded-full blur-3xl group-hover:bg-[#F59E0B]/20 transition-all"></div>
                  <div className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs font-bold text-[#F59E0B] uppercase tracking-wider">In Triage</span>
                    </div>
                    <p className="text-5xl font-bold text-[#F59E0B] mb-2">
                      {stats.status_breakdown?.triaged || 0}
                    </p>
                    <p className="text-sm text-[#94A3B8]">Currently being reviewed</p>
                  </div>
                </div>

                {/* Valid */}
                <div className="relative overflow-hidden bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] hover:border-[#06B6D4] transition-all group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#06B6D4]/10 rounded-full blur-3xl group-hover:bg-[#06B6D4]/20 transition-all"></div>
                  <div className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs font-bold text-[#06B6D4] uppercase tracking-wider">Valid</span>
                    </div>
                    <p className="text-5xl font-bold text-[#06B6D4] mb-2">
                      {stats.status_breakdown?.valid || 0}
                    </p>
                    <p className="text-sm text-[#94A3B8]">Confirmed vulnerabilities</p>
                  </div>
                </div>

                {/* Duplicates */}
                <div className="relative overflow-hidden bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] hover:border-[#A855F7] transition-all group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-[#A855F7]/10 rounded-full blur-3xl group-hover:bg-[#A855F7]/20 transition-all"></div>
                  <div className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 bg-[#A855F7]/10 rounded-lg">
                        <svg className="w-6 h-6 text-[#A855F7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <span className="text-xs font-bold text-[#A855F7] uppercase tracking-wider">Duplicates</span>
                    </div>
                    <p className="text-5xl font-bold text-[#A855F7] mb-2">
                      {stats.status_breakdown?.duplicate || 0}
                    </p>
                    <p className="text-sm text-[#94A3B8]">Duplicate submissions</p>
                  </div>
                </div>
              </div>

              {/* Severity Breakdown - Enhanced Bar Chart */}
              <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] p-6">
                <h3 className="text-lg font-bold text-[#F8FAFC] mb-6">
                  Severity Breakdown
                </h3>
                <div className="space-y-4">
                  {/* Critical */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#EF4444]"></div>
                        <span className="text-sm font-semibold text-[#F8FAFC]">Critical</span>
                      </div>
                      <span className="text-sm font-bold text-[#EF4444]">{stats.severity_breakdown?.critical || 0}</span>
                    </div>
                    <div className="relative h-3 bg-[#0F172A] rounded-full overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#EF4444] to-[#DC2626] rounded-full transition-all duration-500"
                        style={{ 
                          width: `${stats.total_reports > 0 ? ((stats.severity_breakdown?.critical || 0) / stats.total_reports) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* High */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#F59E0B]"></div>
                        <span className="text-sm font-semibold text-[#F8FAFC]">High</span>
                      </div>
                      <span className="text-sm font-bold text-[#F59E0B]">{stats.severity_breakdown?.high || 0}</span>
                    </div>
                    <div className="relative h-3 bg-[#0F172A] rounded-full overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#F59E0B] to-[#D97706] rounded-full transition-all duration-500"
                        style={{ 
                          width: `${stats.total_reports > 0 ? ((stats.severity_breakdown?.high || 0) / stats.total_reports) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Medium */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#06B6D4]"></div>
                        <span className="text-sm font-semibold text-[#F8FAFC]">Medium</span>
                      </div>
                      <span className="text-sm font-bold text-[#06B6D4]">{stats.severity_breakdown?.medium || 0}</span>
                    </div>
                    <div className="relative h-3 bg-[#0F172A] rounded-full overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#06B6D4] to-[#0891B2] rounded-full transition-all duration-500"
                        style={{ 
                          width: `${stats.total_reports > 0 ? ((stats.severity_breakdown?.medium || 0) / stats.total_reports) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Low */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#10B981]"></div>
                        <span className="text-sm font-semibold text-[#F8FAFC]">Low</span>
                      </div>
                      <span className="text-sm font-bold text-[#10B981]">{stats.severity_breakdown?.low || 0}</span>
                    </div>
                    <div className="relative h-3 bg-[#0F172A] rounded-full overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#10B981] to-[#059669] rounded-full transition-all duration-500"
                        style={{ 
                          width: `${stats.total_reports > 0 ? ((stats.severity_breakdown?.low || 0) / stats.total_reports) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Info */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#94A3B8]"></div>
                        <span className="text-sm font-semibold text-[#F8FAFC]">Info</span>
                      </div>
                      <span className="text-sm font-bold text-[#94A3B8]">{stats.severity_breakdown?.info || 0}</span>
                    </div>
                    <div className="relative h-3 bg-[#0F172A] rounded-full overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#94A3B8] to-[#64748B] rounded-full transition-all duration-500"
                        style={{ 
                          width: `${stats.total_reports > 0 ? ((stats.severity_breakdown?.info || 0) / stats.total_reports) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Main Charts Row - Line Chart + Donut Chart */}
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Triage Trends Line Chart - Dynamic Monthly Data */}
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-bold text-[#F8FAFC] mb-6">Monthly Triage Trends</h3>
                  
                  {/* Chart Area */}
                  <div className="relative h-80">
                    {(() => {
                      // Group recent_activity by month and calculate totals
                      const monthlyData: { [key: string]: number } = {};
                      
                      // Process the data
                      if (stats.recent_activity && Array.isArray(stats.recent_activity) && stats.recent_activity.length > 0) {
                        stats.recent_activity.forEach(activity => {
                          try {
                            const date = new Date(activity.date);
                            // Create month key with year to avoid conflicts
                            const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                            const monthLabel = date.toLocaleDateString('en-US', { month: 'short' });
                            
                            if (!monthlyData[monthYear]) {
                              monthlyData[monthYear] = 0;
                            }
                            monthlyData[monthYear] += activity.triaged_count || 0;
                          } catch (e) {
                            console.error('Error processing activity date:', activity, e);
                          }
                        });
                      }
                      
                      // Get last 6 months of data
                      const months: string[] = [];
                      const monthKeys: string[] = [];
                      const values: number[] = [];
                      const currentDate = new Date();
                      
                      for (let i = 5; i >= 0; i--) {
                        const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
                        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                        const monthLabel = date.toLocaleDateString('en-US', { month: 'short' });
                        
                        months.push(monthLabel);
                        monthKeys.push(monthKey);
                        values.push(monthlyData[monthKey] || 0);
                      }
                      
                      const maxValue = Math.max(...values, 10); // Minimum 10 for scale
                      const yAxisSteps = 5;
                      const stepValue = Math.ceil(maxValue / yAxisSteps);
                      const yAxisMax = stepValue * yAxisSteps;
                      
                      // Debug log
                      console.log('Chart Data:', { monthlyData, months, values, maxValue, yAxisMax });
                      
                      return (
                        <>
                          {/* Y-axis labels */}
                          <div className="absolute left-0 top-0 bottom-8 flex flex-col justify-between text-xs text-[#94A3B8] w-12 text-right pr-2">
                            {Array.from({ length: yAxisSteps + 1 }, (_, i) => (
                              <span key={i}>{yAxisMax - (i * stepValue)}</span>
                            ))}
                          </div>
                          
                          {/* Chart container */}
                          <div className="absolute left-14 right-0 top-0 bottom-8">
                            {/* Grid lines */}
                            <div className="absolute inset-0 flex flex-col justify-between">
                              {Array.from({ length: yAxisSteps + 1 }, (_, i) => (
                                <div key={i} className="w-full border-t border-[#334155]/30"></div>
                              ))}
                            </div>
                            
                            {/* SVG Chart */}
                            {values.length > 0 ? (
                              <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                                <defs>
                                  <linearGradient id="triageTrendGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.4" />
                                    <stop offset="100%" stopColor="#06B6D4" stopOpacity="0" />
                                  </linearGradient>
                                </defs>
                                
                                {/* Generate path from actual data */}
                                <>
                                  {/* Main trend line */}
                                  <path
                                    d={values.map((value, index) => {
                                      const x = (index / Math.max(values.length - 1, 1)) * 100;
                                      const y = 100 - ((value / yAxisMax) * 100);
                                      return `${index === 0 ? 'M' : 'L'} ${x},${y}`;
                                    }).join(' ')}
                                    fill="none"
                                    stroke="#06B6D4"
                                    strokeWidth="3"
                                    vectorEffect="non-scaling-stroke"
                                  />
                                  
                                  {/* Fill area under line */}
                                  <path
                                    d={`${values.map((value, index) => {
                                      const x = (index / Math.max(values.length - 1, 1)) * 100;
                                      const y = 100 - ((value / yAxisMax) * 100);
                                      return `${index === 0 ? 'M' : 'L'} ${x},${y}`;
                                    }).join(' ')} L 100,100 L 0,100 Z`}
                                    fill="url(#triageTrendGradient)"
                                  />
                                  
                                  {/* Data points with tooltips */}
                                  {values.map((value, index) => {
                                    const x = (index / Math.max(values.length - 1, 1)) * 100;
                                    const y = 100 - ((value / yAxisMax) * 100);
                                    return (
                                      <g key={index}>
                                        <circle
                                          cx={`${x}%`}
                                          cy={`${y}%`}
                                          r="5"
                                          fill="#06B6D4"
                                          stroke="#1E293B"
                                          strokeWidth="2"
                                          className="hover:r-7 transition-all cursor-pointer"
                                        />
                                        <title>{`${months[index]}: ${value} reports`}</title>
                                      </g>
                                    );
                                  })}
                                </>
                              </svg>
                            ) : (
                              <div className="absolute inset-0 flex items-center justify-center">
                                <p className="text-sm text-[#94A3B8]">No triage data available</p>
                              </div>
                            )}
                          </div>
                          
                          {/* X-axis labels */}
                          <div className="absolute left-14 right-0 bottom-0 flex justify-between text-xs text-[#94A3B8]">
                            {months.map((month, index) => (
                              <span key={index} className="text-center">
                                {month}
                              </span>
                            ))}
                          </div>
                        </>
                      );
                    })()}
                  </div>
                  
                  {/* Summary Stats */}
                  <div className="mt-6 grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-[#0F172A] rounded-lg">
                      <p className="text-xs text-[#94A3B8] mb-1">This Month</p>
                      <p className="text-lg font-bold text-[#06B6D4]">
                        {(() => {
                          if (!stats.recent_activity || !Array.isArray(stats.recent_activity) || stats.recent_activity.length === 0) return 0;
                          const currentMonth = new Date().getMonth();
                          const currentYear = new Date().getFullYear();
                          return stats.recent_activity
                            .filter(a => {
                              const date = new Date(a.date);
                              return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
                            })
                            .reduce((sum, a) => sum + (a.triaged_count || 0), 0);
                        })()}
                      </p>
                    </div>
                    <div className="text-center p-3 bg-[#0F172A] rounded-lg">
                      <p className="text-xs text-[#94A3B8] mb-1">Last Month</p>
                      <p className="text-lg font-bold text-[#94A3B8]">
                        {(() => {
                          if (!stats.recent_activity || !Array.isArray(stats.recent_activity) || stats.recent_activity.length === 0) return 0;
                          const lastMonth = new Date().getMonth() - 1;
                          const year = lastMonth < 0 ? new Date().getFullYear() - 1 : new Date().getFullYear();
                          const month = lastMonth < 0 ? 11 : lastMonth;
                          return stats.recent_activity
                            .filter(a => {
                              const date = new Date(a.date);
                              return date.getMonth() === month && date.getFullYear() === year;
                            })
                            .reduce((sum, a) => sum + (a.triaged_count || 0), 0);
                        })()}
                      </p>
                    </div>
                    <div className="text-center p-3 bg-[#0F172A] rounded-lg">
                      <p className="text-xs text-[#94A3B8] mb-1">Total (6mo)</p>
                      <p className="text-lg font-bold text-[#A855F7]">
                        {(() => {
                          if (!stats.recent_activity || !Array.isArray(stats.recent_activity) || stats.recent_activity.length === 0) return 0;
                          return stats.recent_activity.reduce((sum, a) => sum + (a.triaged_count || 0), 0);
                        })()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Status Distribution Donut Chart */}
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-bold text-[#F8FAFC] mb-6">Status Distribution</h3>
                  
                  {/* Donut Chart */}
                  <div className="flex items-center justify-center mb-8">
                    <div className="relative w-64 h-64">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle 
                          cx="128" 
                          cy="128" 
                          r="100" 
                          fill="none" 
                          stroke="#0F172A" 
                          strokeWidth="40" 
                        />
                        {(() => {
                          if (!stats.status_breakdown) return null;
                          
                          const statusData = [
                            { label: 'New', count: stats.status_breakdown.new || 0, color: '#EF4444' },
                            { label: 'Triaged', count: stats.status_breakdown.triaged || 0, color: '#F59E0B' },
                            { label: 'Valid', count: stats.status_breakdown.valid || 0, color: '#06B6D4' },
                            { label: 'Invalid', count: stats.status_breakdown.invalid || 0, color: '#94A3B8' },
                            { label: 'Duplicate', count: stats.status_breakdown.duplicate || 0, color: '#A855F7' },
                            { label: 'Resolved', count: stats.status_breakdown.resolved || 0, color: '#10B981' },
                          ];
                          
                          const total = statusData.reduce((sum, s) => sum + s.count, 0);
                          if (total === 0) return null;
                          
                          const circumference = 2 * Math.PI * 100; // 628
                          let currentOffset = 0;
                          
                          return statusData.map((status, index) => {
                            if (status.count === 0) return null;
                            
                            const percentage = status.count / total;
                            const segmentLength = circumference * percentage;
                            const offset = -currentOffset;
                            currentOffset += segmentLength;
                            
                            return (
                              <circle
                                key={index}
                                cx="128"
                                cy="128"
                                r="100"
                                fill="none"
                                stroke={status.color}
                                strokeWidth="40"
                                strokeDasharray={`${segmentLength} ${circumference}`}
                                strokeDashoffset={offset}
                              />
                            );
                          });
                        })()}
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-4xl font-bold text-[#F8FAFC]">{stats.total_reports || 0}</p>
                          <p className="text-sm text-[#94A3B8] mt-1">Total</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Legend */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#EF4444]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">New</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.new || 0}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#F59E0B]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">Triaged</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.triaged || 0}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#06B6D4]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">Valid</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.valid || 0}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#94A3B8]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">Invalid</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.invalid || 0}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#A855F7]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">Duplicate</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.duplicate || 0}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg">
                      <div className="w-4 h-4 rounded-sm bg-[#10B981]"></div>
                      <div className="flex-1">
                        <p className="text-xs text-[#94A3B8]">Resolved</p>
                        <p className="text-sm font-semibold text-[#F8FAFC]">{stats.status_breakdown?.resolved || 0}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Team Performance Section */}
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Top Researchers */}
                {stats.top_researchers && stats.top_researchers.length > 0 && (
                  <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <h3 className="text-lg font-bold text-[#F8FAFC]">Top Researchers</h3>
                    </div>
                    <div className="space-y-3">
                      {stats.top_researchers.slice(0, 5).map((researcher, index) => {
                        const totalReports = researcher.total_reports || 0;
                        const validReports = researcher.valid_reports || 0;
                        const accuracy = totalReports > 0 
                          ? ((validReports / totalReports) * 100).toFixed(1) 
                          : '0.0';
                        return (
                          <div key={researcher.researcher_id} className="flex items-center justify-between p-3 bg-[#0F172A] rounded-lg hover:bg-[#334155] transition-colors">
                            <div className="flex items-center gap-3">
                              <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg ${
                                index === 0 ? 'bg-[#F59E0B] text-white' :
                                index === 1 ? 'bg-[#94A3B8] text-white' :
                                index === 2 ? 'bg-[#CD7F32] text-white' :
                                'bg-[#334155] text-[#94A3B8]'
                              }`}>
                                {index + 1}
                              </div>
                              <div>
                                <p className="text-sm font-semibold text-[#F8FAFC]">{researcher.email}</p>
                                <p className="text-xs text-[#94A3B8]">{validReports} valid / {totalReports} total</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-bold text-[#3B82F6]">{accuracy}%</p>
                              <p className="text-xs text-[#94A3B8]">accuracy</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Top Programs */}
                {stats.top_programs && stats.top_programs.length > 0 && (
                  <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <h3 className="text-lg font-bold text-[#F8FAFC]">Programs Needing Attention</h3>
                    </div>
                    <div className="space-y-3">
                      {stats.top_programs.slice(0, 5).map((program, index) => (
                        <div key={program.program_id} className="flex items-center justify-between p-3 bg-[#0F172A] rounded-lg hover:bg-[#334155] transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-[#334155] font-bold text-sm text-[#94A3B8]">
                              #{index + 1}
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-[#F8FAFC]">{program.name}</p>
                              <p className="text-xs text-[#94A3B8]">{program.total_reports} total reports</p>
                            </div>
                          </div>
                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#F59E0B] text-white">
                            {program.pending_count} pending
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Activity Timeline */}
              {stats.recent_activity && stats.recent_activity.length > 0 && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-bold text-[#F8FAFC] mb-4">Triage Trends (Last 7 Days)</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="border-b border-[#334155]">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase">Date</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase">Reports Triaged</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase">Avg Time</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase">Performance</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#334155]">
                        {stats.recent_activity.map((activity, index) => (
                          <tr key={index} className="hover:bg-[#0F172A] transition-colors">
                            <td className="px-4 py-3 text-sm font-medium text-[#F8FAFC]">
                              {new Date(activity.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                            </td>
                            <td className="px-4 py-3">
                              <span className="text-sm font-bold text-[#3B82F6]">{activity.triaged_count}</span>
                            </td>
                            <td className="px-4 py-3 text-sm text-[#94A3B8]">
                              {activity.avg_time_hours !== undefined && activity.avg_time_hours !== null 
                                ? activity.avg_time_hours.toFixed(1) 
                                : '0.0'}h
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                {activity.triaged_count > 10 ? (
                                  <span className="text-xs font-semibold text-[#3B82F6]">High</span>
                                ) : (
                                  <span className="text-xs font-semibold text-[#94A3B8]">Normal</span>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Workload & Efficiency */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold text-[#3B82F6] bg-[#3B82F6]/10 px-2 py-1 rounded">Daily</span>
                  </div>
                  <p className="text-sm text-[#94A3B8] mb-2">Avg Reports/Day</p>
                  <p className="text-3xl font-bold text-[#F8FAFC]">
                    {stats.recent_activity && stats.recent_activity.length > 0 
                      ? (stats.recent_activity.reduce((sum, a) => sum + a.triaged_count, 0) / stats.recent_activity.length).toFixed(1)
                      : '0.0'}
                  </p>
                  <p className="text-xs text-[#94A3B8] mt-2">Last 7 days average</p>
                </div>

                <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold text-[#F59E0B] bg-[#F59E0B]/10 px-2 py-1 rounded">Score</span>
                  </div>
                  <p className="text-sm text-[#94A3B8] mb-2">Efficiency Score</p>
                  <p className="text-3xl font-bold text-[#F8FAFC]">
                    {stats.triage_performance && 
                     stats.triage_performance.accuracy_rate !== undefined && 
                     stats.avg_triage_time_hours !== undefined
                      ? ((stats.triage_performance.accuracy_rate / (stats.avg_triage_time_hours + 1)) * 10).toFixed(0)
                      : '0'}
                  </p>
                  <p className="text-xs text-[#94A3B8] mt-2">Quality × Speed metric</p>
                </div>

                <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold text-[#3B82F6] bg-[#3B82F6]/10 px-2 py-1 rounded">Rate</span>
                  </div>
                  <p className="text-sm text-[#94A3B8] mb-2">Resolution Rate</p>
                  <p className="text-3xl font-bold text-[#F8FAFC]">
                    {stats.total_reports && stats.total_reports > 0
                      ? (((stats.status_breakdown?.resolved || 0) / stats.total_reports) * 100).toFixed(1)
                      : '0.0'}%
                  </p>
                  <p className="text-xs text-[#94A3B8] mt-2">Fully resolved reports</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">No analytics data available</p>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
