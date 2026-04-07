'use client';

import { useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems, formatCurrency } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import EmptyState from '@/components/ui/EmptyState';

export default function OrganizationReportsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('');
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  // Fetch reports list - always fetch all reports to get accurate counts
  const { data: reportsData, isLoading, error, refetch } = useApiQuery(
    `/reports?search=${search}&severity=${severityFilter}`,
    { enabled: !!user }
  );

  const allReports = reportsData?.reports || [];
  
  // Filter reports by active tab on the client side
  const reports = activeTab 
    ? allReports.filter((r: any) => r.status === activeTab)
    : allReports;

  // Count reports by status for tab badges
  const getStatusCount = (status: string) => {
    if (!allReports) return 0;
    if (status === '') return allReports.length; // All
    return allReports.filter((r: any) => r.status === status).length;
  };

  const tabs = [
    { id: '', label: 'All', count: getStatusCount('') },
    { id: 'new', label: 'New', count: getStatusCount('new') },
    { id: 'triaged', label: 'Triaged', count: getStatusCount('triaged') },
    { id: 'valid', label: 'Valid', count: getStatusCount('valid') },
    { id: 'resolved', label: 'Resolved', count: getStatusCount('resolved') },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-[#9d1f1f] text-white';
      case 'high':
        return 'bg-[#d6561c] text-white';
      case 'medium':
        return 'bg-[#d89b16] text-[#2d2a26]';
      case 'low':
        return 'bg-[#2d78a8] text-white';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'new':
        return 'bg-[#eef5fb] text-[#2d78a8]';
      case 'triaged':
        return 'bg-[#faf1e1] text-[#9a6412]';
      case 'valid':
        return 'bg-[#eef7ef] text-[#24613a]';
      case 'resolved':
        return 'bg-[#f3ede6] text-[#5f5851]';
      case 'invalid':
        return 'bg-[#fff2f1] text-[#b42318]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Reports Management"
          subtitle="Review and manage vulnerability reports"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Horizontal Filters Bar */}
            <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
              {/* Search Input */}
              <div className="relative flex-1 max-w-xs">
                <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <Input
                  placeholder="Search"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10 border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
                />
              </div>

              {/* Scope Type Dropdown */}
              <Select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="w-auto min-w-[140px] border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              >
                <option value="">Scope type</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </Select>

              {/* Max Reward Dropdown */}
              <Select
                value=""
                onChange={() => {}}
                className="w-auto min-w-[140px] border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              >
                <option value="">Max reward</option>
              </Select>

              {/* Status Dropdown with Active Badge */}
              <div className="relative">
                <Select
                  value={activeTab}
                  onChange={(e) => setActiveTab(e.target.value)}
                  className="w-auto min-w-[140px] border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 pr-20"
                >
                  <option value="">Status</option>
                  <option value="new">New</option>
                  <option value="triaged">Triaged</option>
                  <option value="valid">Valid</option>
                  <option value="resolved">Resolved</option>
                </Select>
                {activeTab && (
                  <span className="absolute right-10 top-1/2 -translate-y-1/2 rounded-full bg-blue-600 px-2 py-0.5 text-xs font-semibold text-white">
                    Active
                  </span>
                )}
              </div>

              {/* Add Filter Button */}
              <button className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add filter
              </button>

              {/* Reset Button */}
              <button
                onClick={() => {
                  setSearch('');
                  setSeverityFilter('');
                  setActiveTab('');
                }}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Reset
              </button>

              {/* Divider */}
              <div className="h-8 w-px bg-gray-200 dark:bg-slate-600"></div>

              {/* Sort Button */}
              <button className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                </svg>
                SORT
              </button>
            </div>

            {/* Error State */}
            {error && (
              <Card className="border-[#f2c0bc] bg-[#fff2f1]">
                <p className="text-sm text-[#b42318]">{error.message || 'An error occurred'}</p>
              </Card>
            )}

            {/* Reports Grid */}
            {isLoading ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={`loading-${i}`} className="h-80 animate-pulse rounded-2xl bg-gray-100 dark:bg-slate-800" />
                ))}
              </div>
            ) : reports && reports.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {reports.map((report: any) => (
                  <div
                    key={report.id}
                    className="group relative flex flex-col rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
                  >
                    {/* Program Icon/Avatar */}
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full border-2 border-gray-200 bg-white dark:border-slate-600 dark:bg-slate-700">
                      <svg className="h-8 w-8 text-gray-400 dark:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>

                    {/* Report Title */}
                    <h3 className="mb-2 text-lg font-bold text-gray-900 dark:text-slate-100 line-clamp-2">
                      {report.title}
                    </h3>

                    {/* Program Name */}
                    <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">
                      {report.program?.name || 'Unknown Program'}
                    </p>

                    {/* Report Number Badge */}
                    <div className="mb-4 flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 text-sm text-gray-500 dark:text-slate-400">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                        </svg>
                        {report.report_number || `#${report.id.slice(0, 8)}`}
                      </span>
                    </div>

                    {/* Badges */}
                    <div className="mb-4 flex flex-wrap gap-2">
                      <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold ${
                        report.status === 'new' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                        report.status === 'triaged' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        report.status === 'valid' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        report.status === 'resolved' ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {report.status}
                      </span>
                      <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold ${
                        (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                        (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                        (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'low' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {report.assigned_severity || report.suggested_severity || 'Unscored'}
                      </span>
                      {report.cvss_score && (
                        <span className="inline-flex items-center rounded-md bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                          {report.cvss_score.toFixed(1)} scopes
                        </span>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="mb-4 space-y-2 border-t border-gray-100 pt-4 dark:border-slate-700">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500 dark:text-slate-400">Reports</span>
                        <span className="font-bold text-gray-900 dark:text-slate-100">1</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500 dark:text-slate-400">1st response</span>
                        <span className="font-bold text-gray-900 dark:text-slate-100">
                          {report.submitted_at ? '< 1 DAY' : '-'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500 dark:text-slate-400">Rewards</span>
                        <span className="font-bold text-red-600 dark:text-red-400">
                          {report.bounty_amount ? formatCurrency(report.bounty_amount) : 'ETB 0 - ETB 0'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500 dark:text-slate-400">Last update on</span>
                        <span className="font-bold text-gray-900 dark:text-slate-100">
                          {report.submitted_at
                            ? new Date(report.submitted_at).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                              })
                            : '-'}
                        </span>
                      </div>
                    </div>

                    {/* View Button */}
                    <Link
                      href={`/organization/reports/${report.id}`}
                      className="flex w-full items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700"
                    >
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      View Report
                    </Link>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No reports found"
                description={
                  activeTab
                    ? `No reports with "${activeTab}" status yet. Reports will appear here once they are processed by the triage team.`
                    : search || severityFilter
                      ? 'No reports match your filters. Try adjusting your search criteria.'
                      : 'No reports have been submitted to your programs yet. Once researchers submit vulnerability reports, they will appear here.'
                }
              />
            )}
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
