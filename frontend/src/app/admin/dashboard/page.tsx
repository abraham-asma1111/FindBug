'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import PieChart from '@/components/ui/PieChart';
import LineChart from '@/components/ui/LineChart';

export default function AdminDashboardPage() {
  const user = useAuthStore((state) => state.user);

  // Force dark mode for admin portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch data from working endpoints
  const { data: dashboardData } = useApiQuery<any>({ endpoint: '/dashboard' });
  const { data: triageStats } = useApiQuery<any>({ endpoint: '/triage/statistics' });
  const { data: financeKpis } = useApiQuery<any>({ endpoint: '/finance/analytics/executive-kpis' });
  const { data: adminStats } = useApiQuery<any>({ endpoint: '/admin/statistics' });
  const { data: topPrograms } = useApiQuery<any>({ endpoint: '/finance/analytics/top-programs-by-reports?limit=5' });
  
  // Fetch pending reviews from triage queue (new + triaged status)
  const { data: pendingReviewsData } = useApiQuery<any>({ 
    endpoint: '/triage/queue?limit=100' 
  });
  
  // Fetch top researchers by valid reports
  const { data: topResearchersData } = useApiQuery<any>({ 
    endpoint: '/admin/researchers?limit=50' 
  });
  
  // Fetch recent reports for activity (sorted by submitted_at) - fetch ALL for accurate chart
  const { data: recentReportsData } = useApiQuery<any>({ 
    endpoint: '/admin/reports?limit=1000' 
  });

  // Extract KPI data from working endpoints
  const totalReports = dashboardData?.reports?.total || 0;
  const criticalOpen = triageStats?.severity_breakdown?.critical || 0;
  const pendingTriage = triageStats?.status_breakdown?.new || 0;
  const bountyPaid = financeKpis?.total_payouts || 0;
  const activePrograms = adminStats?.programs?.active || 0;

  const [severityTimeframe, setSeverityTimeframe] = useState('all');
  const [reportsTimeframe, setReportsTimeframe] = useState('6m');

  // Vulnerability by Severity data for donut chart
  const severityChartData = useMemo(() => {
    // For 'all' time, ALWAYS use the 100% accurate triageStats directly to ensure perfect parity with the Triage Dashboard
    if (severityTimeframe === 'all' && triageStats?.severity_breakdown) {
      const breakdown = triageStats.severity_breakdown;
      return [
        { label: 'Critical', value: breakdown.critical || 0, color: '#EF4444' },
        { label: 'High', value: breakdown.high || 0, color: '#F97316' },
        { label: 'Medium', value: breakdown.medium || 0, color: '#EAB308' },
        { label: 'Low', value: breakdown.low || 0, color: '#3B82F6' },
        { label: 'Info', value: breakdown.info || 0, color: '#818CF8' },
      ].filter(item => item.value > 0);
    }

    if (!recentReportsData?.reports) return [];
    
    let filteredReports = recentReportsData.reports;
    const now = new Date();
    
    if (severityTimeframe === '7d') {
      const cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      filteredReports = filteredReports.filter((r: any) => new Date(r.submitted_at) >= cutoff);
    } else if (severityTimeframe === '30d') {
      const cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      filteredReports = filteredReports.filter((r: any) => new Date(r.submitted_at) >= cutoff);
    } else if (severityTimeframe === '90d') {
      const cutoff = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
      filteredReports = filteredReports.filter((r: any) => new Date(r.submitted_at) >= cutoff);
    }

    const breakdown: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    filteredReports.forEach((r: any) => {
      // Use exact severity fields matching the database mapping
      const sev = (r.assigned_severity || r.suggested_severity || 'info').toLowerCase();
      if (breakdown[sev] !== undefined) breakdown[sev]++;
    });

    return [
      { label: 'Critical', value: breakdown.critical, color: '#EF4444' },
      { label: 'High', value: breakdown.high, color: '#F97316' },
      { label: 'Medium', value: breakdown.medium, color: '#EAB308' },
      { label: 'Low', value: breakdown.low, color: '#3B82F6' },
      { label: 'Info', value: breakdown.info, color: '#818CF8' },
    ].filter(item => item.value > 0);
  }, [recentReportsData, triageStats, severityTimeframe]);

  // Reports Over Time data for line chart - dynamically grouped by day or month
  const reportsOverTimeData = useMemo(() => {
    const now = new Date();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    if (reportsTimeframe === '3m' || reportsTimeframe === '6m' || reportsTimeframe === '12m') {
      // Group by month
      const monthsToShow = reportsTimeframe === '3m' ? 3 : reportsTimeframe === '6m' ? 6 : 12;
      const monthCounts: Record<string, { label: string; count: number; date: Date }> = {};
      
      for (let i = monthsToShow - 1; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const key = `${d.getFullYear()}-${d.getMonth()}`;
        monthCounts[key] = { label: monthNames[d.getMonth()], count: 0, date: d };
      }
      
      if (recentReportsData?.reports) {
        recentReportsData.reports.forEach((report: any) => {
          const d = new Date(report.submitted_at);
          const key = `${d.getFullYear()}-${d.getMonth()}`;
          if (monthCounts[key]) {
            monthCounts[key].count++;
          }
        });
      }
      
      return Object.values(monthCounts)
        .sort((a, b) => a.date.getTime() - b.date.getTime())
        .map(d => ({ label: d.label, reports: d.count }));
    } else {
      // Group by day for 7d, 30d
      const days = reportsTimeframe === '7d' ? 7 : 30;
      const dayCounts: Record<string, { label: string; count: number; date: Date }> = {};
      
      for (let i = days - 1; i >= 0; i--) {
        const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
        d.setHours(0, 0, 0, 0);
        const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
        dayCounts[key] = { label: `${monthNames[d.getMonth()]} ${d.getDate()}`, count: 0, date: d };
      }
      
      if (recentReportsData?.reports) {
        recentReportsData.reports.forEach((report: any) => {
          const d = new Date(report.submitted_at);
          d.setHours(0, 0, 0, 0);
          const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
          if (dayCounts[key]) {
            dayCounts[key].count++;
          }
        });
      }
      
      return Object.values(dayCounts)
        .sort((a, b) => a.date.getTime() - b.date.getTime())
        .map(d => ({ label: d.label, reports: d.count }));
    }
  }, [recentReportsData, reportsTimeframe]);

  // Recent activity data - actual reports from database with real timestamps
  const recentActivityData = useMemo(() => {
    const activities: Array<{
      type: string;
      title: string;
      description: string;
      time: string;
      severity: string;
    }> = [];
    
    if (recentReportsData?.reports) {
      recentReportsData.reports.slice(0, 5).forEach((report: any) => {
        const submittedDate = new Date(report.submitted_at);
        const now = new Date();
        const diffMs = now.getTime() - submittedDate.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        let timeAgo = '';
        if (diffMins < 1) timeAgo = 'Just now';
        else if (diffMins < 60) timeAgo = `${diffMins}m ago`;
        else if (diffHours < 24) timeAgo = `${diffHours}h ago`;
        else timeAgo = `${diffDays}d ago`;
        
        activities.push({
          type: 'report',
          title: `Report ${report.report_number} submitted`,
          description: report.title,
          time: timeAgo,
          severity: report.assigned_severity || report.suggested_severity || 'medium',
        });
      });
    }
    return activities;
  }, [recentReportsData]);

  // Pending Reviews - reports with status "new" or "triaged" grouped by severity
  const pendingReviews = useMemo(() => {
    if (!pendingReviewsData?.reports) return [];
    
    const reports = pendingReviewsData.reports;
    
    if (reports.length === 0) return [];
    
    // Count by severity (use assigned_severity if available, otherwise suggested_severity)
    const severityCounts: Record<string, number> = {
      critical: 0,
      high: 0,
      medium: 0,
    };
    
    reports.forEach((report: any) => {
      const severity = (report.assigned_severity || report.suggested_severity || '').toLowerCase();
      if (severity in severityCounts) {
        severityCounts[severity]++;
      }
    });
    
    return [
      { severity: 'Critical', count: severityCounts.critical, color: '#EF4444' },
      { severity: 'High', count: severityCounts.high, color: '#F59E0B' },
      { severity: 'Medium', count: severityCounts.medium, color: '#FBBF24' },
    ].filter(item => item.count > 0);
  }, [pendingReviewsData]);



  // Active researchers - ALL active users (verified OR has reputation)
  const activeResearchers = useMemo(() => {
    if (!topResearchersData?.researchers || topResearchersData.researchers.length === 0) return [];
    
    // Filter for ACTIVE researchers:
    // Show if: (email_verified AND persona_verified) OR (has reputation > 0)
    const activeResearchers = topResearchersData.researchers.filter((r: any) => {
      const isFullyVerified = r.email_verified === true && r.persona_verified === true;
      const hasReputation = (r.reputation_score || 0) > 0;
      return isFullyVerified || hasReputation;
    });
    
    // Sort by reputation_score descending (best performers first)
    const sortedResearchers = activeResearchers.sort((a: any, b: any) => 
      (b.reputation_score || 0) - (a.reputation_score || 0)
    );
    
    // Return ALL active researchers (no limit)
    // Only show username if it exists, otherwise skip that researcher
    return sortedResearchers
      .filter((researcher: any) => researcher.username && researcher.username.trim() !== '')
      .map((researcher: any) => ({
        name: researcher.username,
        avatar: researcher.username.substring(0, 2).toUpperCase(),
        reports: researcher.valid_reports || 0,
        reputation: Math.round(researcher.reputation_score || 0),
      }));
  }, [topResearchersData]);

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Admin Dashboard"
          subtitle="System overview and management"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2 mb-3">
            {/* Total Reports */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl hover:shadow-[#EF2330]/10 transition-all">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Total Reports</p>
                <div className="w-8 h-8 bg-[#EF2330]/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-[#EF2330]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{totalReports.toLocaleString()}</p>
              <p className="text-xs text-[#64748B]">All submissions</p>
            </div>

            {/* Critical Open */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl hover:shadow-red-500/10 transition-all">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Critical Open</p>
                <div className="w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{criticalOpen}</p>
              <p className="text-xs text-red-400">Requires attention</p>
            </div>

            {/* Pending Triage */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl hover:shadow-orange-500/10 transition-all">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Pending Triage</p>
                <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{pendingTriage}</p>
              <p className="text-xs text-orange-400">Awaiting review</p>
            </div>

            {/* Bounty Paid */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl hover:shadow-green-500/10 transition-all">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Bounty Paid</p>
                <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">ETB {bountyPaid.toLocaleString()}</p>
              <p className="text-xs text-green-400">Total payouts</p>
            </div>

            {/* Active Programs */}
            <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg hover:shadow-xl hover:shadow-blue-500/10 transition-all">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Active Programs</p>
                <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{activePrograms}</p>
              <p className="text-xs text-blue-400">Currently running</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-2 mb-3">
            {/* Vulnerability by Severity - Donut Chart */}
            <div className="lg:col-span-4 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-bold text-white">Vulnerability by Severity</h2>
                <select 
                  className="px-3 py-1.5 bg-[#0F172A] border border-[#334155] rounded-lg text-xs text-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-purple-500"
                  value={severityTimeframe}
                  onChange={(e) => setSeverityTimeframe(e.target.value)}
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 3 Months</option>
                  <option value="all">All time</option>
                </select>
              </div>
              <div className="flex-1 flex items-center justify-center py-4">
                {severityChartData.length > 0 ? (
                  <PieChart data={severityChartData} size={180} showLegend={true} />
                ) : (
                  <div className="w-full h-48 flex items-center justify-center text-[#64748B]">
                    <p>No data available</p>
                  </div>
                )}
              </div>
            </div>

            {/* Reports Over Time - Line Chart */}
            <div className="lg:col-span-5 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-bold text-white">Reports Over Time</h2>
                  <p className="text-xs text-[#64748B] mt-1">Monthly submission trends</p>
                </div>
                <select 
                  className="px-3 py-1.5 bg-[#0F172A] border border-[#334155] rounded-lg text-xs text-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-purple-500"
                  value={reportsTimeframe}
                  onChange={(e) => setReportsTimeframe(e.target.value)}
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="3m">Last 3 Months</option>
                  <option value="6m">Last 6 Months</option>
                  <option value="12m">Last 12 Months</option>
                </select>
              </div>
              <div className="h-72">
                <LineChart
                  data={reportsOverTimeData}
                  xKey="label"
                  lines={[
                    { key: 'reports', color: '#A855F7', name: 'Reports' }
                  ]}
                  height={288}
                />
              </div>
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-3 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl border border-[#334155] shadow-lg overflow-hidden">
              <div className="p-6 border-b border-[#334155]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-bold text-white">Recent Activity</h2>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                      <span className="text-xs text-green-400">Live</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="divide-y divide-[#334155] max-h-[400px] overflow-y-auto">
                {recentActivityData.length > 0 ? (
                  recentActivityData.map((activity, index) => (
                    <div key={index} className="p-4 hover:bg-[#0F172A]/50 transition-colors">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                          activity.severity === 'critical' ? 'bg-red-400' :
                          activity.severity === 'high' ? 'bg-orange-400' :
                          activity.severity === 'medium' ? 'bg-yellow-400' :
                          'bg-blue-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white mb-1">{activity.title}</p>
                          <p className="text-xs text-[#64748B] truncate">{activity.description}</p>
                          <p className="text-xs text-[#475569] mt-1">{activity.time}</p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center text-[#64748B]">
                    <p className="text-sm">No recent activity</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Row */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-2">
            {/* Top Programs by Submissions */}
            <div className="lg:col-span-4 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white">Top Programs</h2>
                <Link href="/admin/programs">
                  <Button variant="ghost" size="xs" className="text-[#EF2330] hover:text-[#EF2330]/80">
                    View all →
                  </Button>
                </Link>
              </div>
              <div className="space-y-3">
                {topPrograms?.programs && topPrograms.programs.length > 0 ? (
                  topPrograms.programs.map((program: any, index: number) => {
                    const maxReports = topPrograms.programs[0]?.report_count || 1;
                    const percentage = (program.report_count / maxReports) * 100;
                    return (
                      <div key={program.program_id || index}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-white font-medium truncate">{program.program_name}</span>
                          <span className="text-sm font-bold text-purple-400">{program.report_count}</span>
                        </div>
                        <div className="w-full bg-[#0F172A] rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-[#EF2330] to-[#DC143C] h-2 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="py-8 text-center text-[#64748B]">
                    <p className="text-sm">No programs yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Pending Reviews by Severity */}
            <div className="lg:col-span-5 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
              <h2 className="text-lg font-bold text-white mb-4">Pending Reviews</h2>
              <div className="space-y-3">
                {pendingReviews.length > 0 ? (
                  pendingReviews.map((item) => (
                    <div key={item.severity} className="flex items-center justify-between p-3 bg-[#0F172A] rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-white font-medium">{item.severity}</span>
                      </div>
                      <span className="text-lg font-bold text-white">{item.count}</span>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-[#64748B]">
                    <p className="text-sm">No pending reviews</p>
                  </div>
                )}
              </div>
            </div>

            {/* Active Researchers */}
            <div className="lg:col-span-3 bg-gradient-to-br from-[#1E293B] to-[#0F172A] rounded-xl p-6 border border-[#334155] shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white">Active Researchers</h2>
                <Link href="/admin/users?role=researcher">
                  <Button variant="ghost" size="xs" className="text-[#EF2330] hover:text-[#EF2330]/80">
                    View all →
                  </Button>
                </Link>
              </div>
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {activeResearchers.length > 0 ? (
                  activeResearchers.map((researcher: { name: string; avatar: string; reports: number; reputation: number }, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 hover:bg-[#0F172A]/50 rounded-lg transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-[#EF2330] to-[#DC143C] rounded-full flex items-center justify-center text-white text-xs font-bold">
                          {researcher.avatar}
                        </div>
                        <span className="text-sm text-white font-medium">{researcher.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <svg className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="text-xs font-semibold text-yellow-400">{researcher.reputation}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-[#64748B]">
                    <p className="text-sm">No active researchers</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
