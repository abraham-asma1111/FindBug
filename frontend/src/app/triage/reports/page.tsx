'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Card from '@/components/ui/Card';
import { ChevronRight, AlertCircle, Clock, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

interface Report {
  id: string;
  report_number: string;
  program_id: string;
  researcher_id: string;
  title: string;
  description: string;
  status: string;
  assigned_severity: string | null;
  suggested_severity: string;
  triaged_by: string | null;
  triaged_at: string | null;
  is_duplicate: boolean;
  bounty_amount: number | null;
  submitted_at: string;
  updated_at: string;
}

interface ReportsResponse {
  reports: Report[];
  total: number;
  limit: number;
  offset: number;
}

const severityColors: Record<string, string> = {
  critical: 'bg-[#EF4444] text-white',
  high: 'bg-[#F59E0B] text-white',
  medium: 'bg-[#F59E0B] text-white',
  low: 'bg-[#3B82F6] text-white',
  info: 'bg-[#94A3B8] text-white',
};

const statusIcons: Record<string, React.ReactNode> = {
  new: <AlertCircle className="w-4 h-4" />,
  triaged: <Clock className="w-4 h-4" />,
  valid: <CheckCircle className="w-4 h-4" />,
  invalid: <XCircle className="w-4 h-4" />,
  duplicate: <XCircle className="w-4 h-4" />,
  resolved: <CheckCircle className="w-4 h-4" />,
};

const statusColors: Record<string, string> = {
  new: 'text-[#EF4444]',
  triaged: 'text-[#F59E0B]',
  valid: 'text-[#3B82F6]',
  invalid: 'text-[#EF4444]',
  duplicate: 'text-[#94A3B8]',
  resolved: 'text-[#3B82F6]',
};

export default function TriageReportsPage() {
  const user = useAuthStore((state) => state.user);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const queryParams = new URLSearchParams();
  if (statusFilter) queryParams.append('status_filter', statusFilter);
  if (severityFilter) queryParams.append('severity_filter', severityFilter);
  queryParams.append('limit', limit.toString());
  queryParams.append('offset', (page * limit).toString());

  const { data, isLoading, error } = useApiQuery<ReportsResponse>({
    endpoint: `/triage/queue?${queryParams.toString()}`,
  });

  const reports = data?.reports || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Triage Reports"
          subtitle="Manage report validation and classification"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Filters */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                Status
              </label>
              <Select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(0);
                }}
                options={[
                  { value: '', label: 'All Statuses' },
                  { value: 'new', label: 'New' },
                  { value: 'triaged', label: 'Triaged' },
                  { value: 'valid', label: 'Valid' },
                  { value: 'invalid', label: 'Invalid' },
                  { value: 'duplicate', label: 'Duplicate' },
                  { value: 'resolved', label: 'Resolved' },
                ]}
              />
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                Severity
              </label>
              <Select
                value={severityFilter}
                onChange={(e) => {
                  setSeverityFilter(e.target.value);
                  setPage(0);
                }}
                options={[
                  { value: '', label: 'All Severities' },
                  { value: 'critical', label: 'Critical' },
                  { value: 'high', label: 'High' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'low', label: 'Low' },
                  { value: 'info', label: 'Info' },
                ]}
              />
            </div>

            <div>
              <Button
                onClick={() => {
                  setStatusFilter('');
                  setSeverityFilter('');
                  setPage(0);
                }}
                variant="outline"
              >
                Clear Filters
              </Button>
            </div>
          </div>

          {/* Reports Stats */}
          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Total Reports
              </p>
              <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                {total}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                New
              </p>
              <p className="mt-2 text-2xl font-bold text-[#EF4444]">
                {reports.filter((r) => r.status === 'new').length}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Pending Triage
              </p>
              <p className="mt-2 text-2xl font-bold text-[#F59E0B]">
                {reports.filter((r) => r.status === 'triaged').length}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                Duplicates
              </p>
              <p className="mt-2 text-2xl font-bold text-[#94A3B8]">
                {reports.filter((r) => r.is_duplicate).length}
              </p>
            </div>
          </div>

          {/* Reports Table */}
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
                <p className="mt-4 text-[#94A3B8]">Loading reports...</p>
              </div>
            ) : error ? (
              <div className="p-8 text-center">
                <AlertCircle className="mx-auto h-8 w-8 text-[#EF4444]" />
                <p className="mt-4 text-[#EF4444]">Failed to load reports</p>
              </div>
            ) : reports.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-[#94A3B8]">No reports found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Report
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Severity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Bounty
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Submitted
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                    {reports.map((report) => (
                      <tr
                        key={report.id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-semibold text-slate-900 dark:text-slate-100">
                              {report.title}
                            </p>
                            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                              {report.report_number}
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className={`flex items-center gap-2 ${statusColors[report.status] || 'text-slate-600'}`}>
                            {statusIcons[report.status]}
                            <span className="text-sm font-medium capitalize">
                              {report.status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {report.assigned_severity ? (
                            <span
                              className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                severityColors[report.assigned_severity.toLowerCase()] ||
                                severityColors.info
                              }`}
                            >
                              {report.assigned_severity}
                            </span>
                          ) : (
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                              {report.suggested_severity}
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {report.bounty_amount ? (
                            <span className="font-semibold text-slate-900 dark:text-slate-100">
                              ${report.bounty_amount.toLocaleString()}
                            </span>
                          ) : (
                            <span className="text-slate-500 dark:text-slate-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                          {new Date(report.submitted_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Link href={`/triage/reports/${report.id}`}>
                            <Button variant="ghost" size="sm" className="gap-2">
                              Review
                              <ChevronRight className="w-4 h-4" />
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Page {page + 1} of {totalPages} ({total} total reports)
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  variant="outline"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page === totalPages - 1}
                  variant="outline"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
