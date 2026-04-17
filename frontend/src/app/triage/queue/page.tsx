'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { AlertCircle } from 'lucide-react';

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

interface QueueResponse {
  reports: Report[];
  total: number;
  limit: number;
  offset: number;
}

export default function TriageQueuePage() {
  const user = useAuthStore((state) => state.user);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
    return () => {
      // Optional: remove dark class when leaving triage portal
      // document.documentElement.classList.remove('dark');
    };
  }, []);

  const queryParams = new URLSearchParams();
  if (statusFilter) queryParams.append('status_filter', statusFilter);
  if (severityFilter) queryParams.append('severity_filter', severityFilter);
  queryParams.append('limit', limit.toString());
  queryParams.append('offset', (page * limit).toString());

  const { data, isLoading, error } = useApiQuery<QueueResponse>(
    `/triage/queue?${queryParams.toString()}`
  );

  const reports = data?.reports || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);
  
  // Calculate new reports count
  const newReportsCount = reports.filter((r) => r.status === 'new').length;

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title=""
          subtitle=""
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideTitle={true}
          hideSubtitle={true}
          hideThemeToggle={true}
        >
          {/* Custom Header */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-slate-100">Triage Queue</h1>
              {newReportsCount > 0 && (
                <span className="px-3 py-1 rounded-lg bg-[#2563EB] text-white text-sm font-semibold">
                  {newReportsCount} New
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-slate-300 rounded-lg text-sm font-medium transition-colors border border-[#334155]">
                Export
              </button>
              <button className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors">
                Bulk Actions
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                New Reports
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {reports.filter((r) => r.status === 'new').length}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                In Review
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {reports.filter((r) => r.status === 'triaged').length}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                Today's Total
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {total}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                Avg Response Time
              </p>
              <p className="text-3xl font-bold text-slate-100">2.5h</p>
            </div>
          </div>

          {/* Filter Buttons */}
          <div className="mb-6 flex flex-wrap gap-2 items-center">
            <button
              onClick={() => {
                setStatusFilter('');
                setSeverityFilter('');
                setPage(0);
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                !statusFilter && !severityFilter
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
              }`}
            >
              All
            </button>
            <button
              onClick={() => {
                setSeverityFilter('critical');
                setPage(0);
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                severityFilter === 'critical'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
              }`}
            >
              Critical
            </button>
            <button
              onClick={() => {
                setSeverityFilter('high');
                setPage(0);
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                severityFilter === 'high'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
              }`}
            >
              High
            </button>
            <button
              onClick={() => {
                setSeverityFilter('medium');
                setPage(0);
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                severityFilter === 'medium'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
              }`}
            >
              Medium
            </button>
            <button
              onClick={() => {
                setSeverityFilter('low');
                setPage(0);
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                severityFilter === 'low'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
              }`}
            >
              Low
            </button>
            <div className="ml-auto flex items-center gap-2 bg-[#1E293B] rounded-lg px-4 py-2 border border-[#334155]">
              <input
                type="text"
                placeholder="Search reports..."
                className="bg-transparent text-slate-300 placeholder-slate-500 outline-none text-sm"
              />
            </div>
          </div>

          {/* Reports List */}
          <div className="space-y-4">

            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg p-12 text-center border border-[#334155]">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
                <p className="mt-4 text-slate-400">Loading reports...</p>
              </div>
            ) : error ? (
              <div className="bg-[#1E293B] rounded-lg p-12 text-center border border-[#334155]">
                <AlertCircle className="mx-auto h-8 w-8 text-red-400" />
                <p className="mt-4 text-red-400">Failed to load reports</p>
              </div>
            ) : reports.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg p-12 text-center border border-[#334155]">
                <p className="text-slate-400">No reports found</p>
              </div>
            ) : (
              reports.map((report) => (
                <div
                  key={report.id}
                  className="bg-[#1E293B] rounded-lg p-6 border border-[#334155] hover:bg-[#334155] transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-slate-100 mb-1">
                        {report.title}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span>{report.report_number}</span>
                        <span>•</span>
                        <span>Ethiopian Airlines: Web Application</span>
                        <span>•</span>
                        <span>👤 Abraham Asimamaw</span>
                        <span>•</span>
                        <span>🕐 2 hours ago</span>
                        <span>•</span>
                        <span>🌐 api.ethiopianairlines.com</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-3 py-1 rounded text-xs font-bold uppercase ${
                          report.assigned_severity === 'critical'
                            ? 'bg-[#EF4444] text-white'
                            : report.assigned_severity === 'high'
                            ? 'bg-[#F59E0B] text-white'
                            : 'bg-slate-600 text-white'
                        }`}
                      >
                        {report.assigned_severity || report.suggested_severity}
                      </span>
                      <span className="px-3 py-1 rounded bg-[#3B82F6] text-white text-xs font-medium">
                        New
                      </span>
                    </div>
                  </div>
                  <p className="text-slate-300 text-sm mb-4 line-clamp-2">
                    {report.description}
                  </p>
                  <div className="flex items-center gap-2">
                    <button className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors">
                      Review Report
                    </button>
                    <button className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-slate-300 rounded-lg text-sm font-medium transition-colors border border-[#334155]">
                      View Details
                    </button>
                    <button className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-slate-300 rounded-lg text-sm font-medium transition-colors border border-[#334155]">
                      Assign to Me
                    </button>
                  </div>
                </div>
              ))
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
