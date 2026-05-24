'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function AdminReportsPage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const router = useRouter();
  const statusFilter   = searchParams.get('status')     || 'all';
  const severityFilter = searchParams.get('severity')   || 'all';
  const programId      = searchParams.get('program_id') || '';
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const params = new URLSearchParams();
  if (statusFilter   !== 'all') params.set('status_filter',   statusFilter);
  if (severityFilter !== 'all') params.set('severity_filter', severityFilter);
  if (programId)                params.set('program_id',      programId);
  const endpoint = `/admin/reports${params.toString() ? '?' + params.toString() : ''}`;

  const { data, isLoading } = useApiQuery<any>({ endpoint });
  const reports = data?.reports || [];

  const filteredReports = reports.filter((r: any) => {
    const searchLower = searchQuery.toLowerCase();
    return (
      (r.title && r.title.toLowerCase().includes(searchLower)) ||
      (r.researcher_name && r.researcher_name.toLowerCase().includes(searchLower)) ||
      (r.program_name && r.program_name.toLowerCase().includes(searchLower))
    );
  });

  const getStatusBadge = (status: string) => {
    const map: Record<string, { bg: string; label: string }> = {
      new:       { bg: 'bg-[#3B82F6]', label: 'NEW' },
      submitted: { bg: 'bg-[#3B82F6]', label: 'SUBMITTED' },
      triaged:   { bg: 'bg-[#F59E0B]', label: 'TRIAGED' },
      valid:     { bg: 'bg-[#10B981]', label: 'VALID' },
      validated: { bg: 'bg-[#10B981]', label: 'VALID' },
      invalid:   { bg: 'bg-[#EF4444]', label: 'INVALID' },
      rejected:  { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      duplicate: { bg: 'bg-[#94A3B8]', label: 'DUPLICATE' },
      resolved:  { bg: 'bg-[#8B5CF6]', label: 'RESOLVED' },
      closed:    { bg: 'bg-[#64748B]', label: 'CLOSED' },
    };
    const config = map[status] || { bg: 'bg-[#94A3B8]', label: status?.toUpperCase() || '—' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const getSeverityBadge = (severity: string | null) => {
    if (!severity) return null;
    const map: Record<string, string> = {
      critical: 'bg-[#DC2626]',
      high:     'bg-[#EA580C]',
      medium:   'bg-[#CA8A04]',
      low:      'bg-[#16A34A]',
      info:     'bg-[#0284C7]',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${map[severity] || 'bg-[#94A3B8]'} text-white`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  const STATUS_FILTERS: { value: string; label: string }[] = [
    { value: 'all',       label: 'All' },
    { value: 'new',       label: 'New' },
    { value: 'triaged',   label: 'Triaged' },
    { value: 'valid',     label: 'Valid' },
    { value: 'invalid',   label: 'Invalid' },
    { value: 'duplicate', label: 'Duplicate' },
    { value: 'resolved',  label: 'Resolved' },
  ];
  const SEVERITY_FILTERS = ['all', 'critical', 'high', 'medium', 'low'];

  const makeHref = (sv: string, st: string) => {
    const p = new URLSearchParams();
    if (st !== 'all') p.set('status', st);
    if (sv !== 'all') p.set('severity', sv);
    return `/admin/reports${p.toString() ? '?' + p.toString() : ''}`;
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Reports"
          subtitle="Manage vulnerability reports"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          {/* Hero */}
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Report Management
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Vulnerability Reports
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Platform-wide view of all vulnerability reports across every program.
              </p>
            </div>
          </section>

          {/* Controls Row */}
          <div className="mt-4 flex flex-col xl:flex-row items-center justify-between gap-6">
            
            {/* Filters */}
            <div className="flex flex-col sm:flex-row items-center gap-4">
            {/* Status Dropdown */}
            <div className="flex items-center gap-3 bg-[#0F172A] p-2 rounded-lg border border-[#334155]">
              <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider pl-2">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => router.push(makeHref(severityFilter, e.target.value))}
                className="rounded-md border border-[#334155] bg-[#1E293B] px-3 py-1.5 text-sm font-medium text-[#F8FAFC] focus:border-[#EF2330] focus:ring-1 focus:ring-[#EF2330] focus:outline-none transition-all cursor-pointer min-w-[140px]"
              >
                {STATUS_FILTERS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            {/* Severity Dropdown */}
            <div className="flex items-center gap-3 bg-[#0F172A] p-2 rounded-lg border border-[#334155]">
              <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider pl-2">Severity:</span>
              <select
                value={severityFilter}
                onChange={(e) => router.push(makeHref(e.target.value, statusFilter))}
                className="rounded-md border border-[#334155] bg-[#1E293B] px-3 py-1.5 text-sm font-medium text-[#F8FAFC] focus:border-[#EF2330] focus:ring-1 focus:ring-[#EF2330] focus:outline-none transition-all cursor-pointer min-w-[140px]"
              >
                {SEVERITY_FILTERS.map((sv) => (
                  <option key={sv} value={sv}>{sv === 'all' ? 'All' : sv.charAt(0).toUpperCase() + sv.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Bar */}
          <div className="w-full xl:w-72 flex justify-end">
            <div className="relative w-full max-w-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-[#64748B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-[#334155] rounded-lg leading-5 bg-[#0F172A] text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#EF2330] focus:border-[#EF2330] sm:text-sm transition-colors"
              />
            </div>
          </div>
        </div>

          {/* Active program filter banner */}
          {programId && (
            <div className="mt-3 flex items-center gap-3 rounded-md bg-[#1E3A5F] border border-[#3B82F6]/40 px-4 py-2">
              <span className="text-xs text-[#93C5FD]">
                Filtered by program: <code className="font-mono text-[#F8FAFC]">{programId}</code>
              </span>
              <a
                href="/admin/reports"
                className="ml-auto text-xs text-[#64748B] hover:text-[#F8FAFC] transition-colors"
              >
                ✕ Clear
              </a>
            </div>
          )}

          {/* Reports List */}
          <div className="mt-3">
            {isLoading ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">Loading reports…</p>
              </div>
            ) : filteredReports.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 text-center">
                <p className="text-[#94A3B8]">No reports found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredReports.map((report: any) => (
                  <Link key={report.id} href={`/admin/reports/${report.id}`}>
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:border-[#475569] transition-colors cursor-pointer">
                      <div className="flex items-center justify-between gap-4">
                        <div className="min-w-0 flex-1">
                          <h3 className="font-semibold text-[#F8FAFC] mb-1 truncate">
                            {report.title || '(Untitled)'}
                          </h3>
                          <p className="text-sm text-[#94A3B8] truncate">
                            {report.researcher_name || 'Unknown researcher'}
                            {report.program_name ? ` · ${report.program_name}` : ''}
                            {report.submitted_at
                              ? ` · ${new Date(report.submitted_at).toLocaleDateString()}`
                              : ''}
                          </p>
                          {report.report_number && (
                            <p className="text-xs text-[#64748B] mt-1">#{report.report_number}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          {getSeverityBadge(report.assigned_severity)}
                          {getStatusBadge(report.status)}
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-[#64748B]">
            Showing {filteredReports.length} report{filteredReports.length !== 1 ? 's' : ''}
            {statusFilter !== 'all' ? ` · status: ${statusFilter}` : ''}
            {severityFilter !== 'all' ? ` · severity: ${severityFilter}` : ''}
          </p>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
