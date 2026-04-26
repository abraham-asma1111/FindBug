'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { RefreshCw, ChevronLeft, AlertCircle, ExternalLink, Filter } from 'lucide-react';
import Link from 'next/link';

interface Report {
  id: string;
  report_number: string;
  title: string;
  status: string;
  assigned_severity: string | null;
  suggested_severity: string;
  is_duplicate: boolean;
  duplicate_of: string | null;
  researcher_name: string;
  researcher_email: string;
  submitted_at: string;
  bounty_amount: number | null;
}

interface ProgramDetail {
  id: string;
  name: string;
  organization_name: string;
  description: string;
  status: string;
  total_reports: number;
  pending_count: number;
  valid_count: number;
  invalid_count: number;
  duplicate_count: number;
}

const statusColors: Record<string, string> = {
  new: 'bg-[#EF4444] text-white',
  triaged: 'bg-[#F59E0B] text-white',
  valid: 'bg-[#3B82F6] text-white',
  invalid: 'bg-[#EF4444] text-white',
  duplicate: 'bg-[#94A3B8] text-white',
  resolved: 'bg-[#3B82F6] text-white',
};

const severityColors: Record<string, string> = {
  critical: 'bg-[#EF4444] text-white',
  high: 'bg-[#F59E0B] text-white',
  medium: 'bg-[#F59E0B] text-white',
  low: 'bg-[#3B82F6] text-white',
  info: 'bg-[#94A3B8] text-white',
};

export default function TriageProgramDetailPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [showDuplicatesOnly, setShowDuplicatesOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [allReports, setAllReports] = useState<Report[]>([]);
  const limit = 50;

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch program details
  const { data: programData, isLoading: programLoading, error: programError } = useApiQuery<ProgramDetail>({
    endpoint: `/triage/programs/${programId}`,
  });

  // Fetch program reports
  const { data: reportsData, isLoading: reportsLoading, error: reportsError, refetch } = useApiQuery<{ reports: Report[]; total: number }>({
    endpoint: `/triage/queue?program_id=${programId}&limit=100`,
  });

  const handleRefresh = async () => {
    await refetch();
    setLastUpdated(new Date());
  };

  // Filter reports
  const filteredReports = reportsData?.reports?.filter(report => {
    if (statusFilter && report.status !== statusFilter) return false;
    if (severityFilter) {
      const severity = report.assigned_severity || report.suggested_severity;
      if (severity !== severityFilter) return false;
    }
    if (showDuplicatesOnly && !report.is_duplicate) return false;
    return true;
  }) || [];

  // Group reports by similarity for duplicate detection
  const groupedReports = new Map<string, Report[]>();
  filteredReports.forEach(report => {
    const titleKey = report.title.toLowerCase().substring(0, 30);
    if (!groupedReports.has(titleKey)) {
      groupedReports.set(titleKey, []);
    }
    groupedReports.get(titleKey)?.push(report);
  });

  // Find potential duplicates (groups with 2+ reports)
  const potentialDuplicates = Array.from(groupedReports.values()).filter(group => group.length > 1);

  const isLoading = programLoading || reportsLoading;
  const error = programError || reportsError;

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title={programData?.name || 'Program Details'}
          subtitle={`Manage all reports for this program`}
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/triage/programs" className="text-[#3B82F6] hover:underline text-sm">
              Programs
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">{programData?.name || 'Loading...'}</span>
          </div>

          {/* Program Info Card */}
          {programData && (
            <div className="mb-6 bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">{programData.name}</h2>
                  <p className="text-sm text-[#94A3B8] mb-1">
                    Organization: {programData.organization_name || 'N/A'}
                  </p>
                  {programData.description && (
                    <p className="text-sm text-[#94A3B8] mt-2">{programData.description}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${
                  programData.status === 'active' ? 'bg-[#10B981] text-white' : 'bg-[#94A3B8] text-white'
                }`}>
                  {programData.status}
                </span>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-5 gap-4">
                <div className="bg-[#0F172A] rounded-lg p-3 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Total</p>
                  <p className="mt-1 text-xl font-bold text-[#F8FAFC]">{programData.total_reports}</p>
                </div>
                <div className="bg-[#0F172A] rounded-lg p-3 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Pending</p>
                  <p className="mt-1 text-xl font-bold text-[#F59E0B]">{programData.pending_count}</p>
                </div>
                <div className="bg-[#0F172A] rounded-lg p-3 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Valid</p>
                  <p className="mt-1 text-xl font-bold text-[#10B981]">{programData.valid_count}</p>
                </div>
                <div className="bg-[#0F172A] rounded-lg p-3 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Invalid</p>
                  <p className="mt-1 text-xl font-bold text-[#EF4444]">{programData.invalid_count}</p>
                </div>
                <div className="bg-[#0F172A] rounded-lg p-3 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Duplicates</p>
                  <p className="mt-1 text-xl font-bold text-[#F59E0B]">{programData.duplicate_count}</p>
                </div>
              </div>
            </div>
          )}

          {/* Potential Duplicates Alert */}
          {potentialDuplicates.length > 0 && !showDuplicatesOnly && (
            <div className="mb-6 bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-[#F59E0B] mb-1">
                    Potential Duplicates Detected
                  </p>
                  <p className="text-xs text-[#94A3B8] mb-2">
                    Found {potentialDuplicates.length} groups of reports with similar titles. Review these for potential duplicates.
                  </p>
                  <Button
                    onClick={() => setShowDuplicatesOnly(true)}
                    variant="outline"
                    size="sm"
                    className="text-[#F59E0B] border-[#F59E0B]"
                  >
                    Show Potential Duplicates
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Filters and Controls */}
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Filter className="w-5 h-5 text-[#94A3B8]" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] text-sm focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="new">New</option>
                <option value="triaged">Triaged</option>
                <option value="valid">Valid</option>
                <option value="invalid">Invalid</option>
                <option value="duplicate">Duplicate</option>
                <option value="resolved">Resolved</option>
              </select>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] text-sm focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
              >
                <option value="">All Severity</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="info">Info</option>
              </select>
              <label className="flex items-center gap-2 text-sm text-[#F8FAFC] cursor-pointer">
                <input
                  type="checkbox"
                  checked={showDuplicatesOnly}
                  onChange={(e) => setShowDuplicatesOnly(e.target.checked)}
                  className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                />
                Show Duplicates Only
              </label>
            </div>
            <div className="flex items-center gap-3">
              <p className="text-xs text-[#94A3B8]">
                Showing {filteredReports.length} of {reportsData?.total || 0} reports
              </p>
              <p className="text-xs text-[#94A3B8]">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
              <Button
                onClick={handleRefresh}
                variant="outline"
                size="sm"
                className="gap-2"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {/* Reports List */}
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading reports...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-[#EF4444] font-semibold">Failed to load reports</p>
                  <p className="text-sm text-[#94A3B8] mt-1">
                    {error instanceof Error ? error.message : 'Unknown error occurred'}
                  </p>
                  <Button
                    onClick={handleRefresh}
                    variant="outline"
                    size="sm"
                    className="mt-3"
                  >
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-lg font-semibold text-[#F8FAFC] mb-2">No reports found</p>
              <p className="text-sm text-[#94A3B8]">
                {statusFilter || severityFilter || showDuplicatesOnly
                  ? 'Try adjusting your filters'
                  : 'No reports have been submitted to this program yet'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredReports.map((report) => (
                <div
                  key={report.id}
                  className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 hover:border-[#3B82F6] transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono text-[#3B82F6]">
                          {report.report_number}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                          statusColors[report.status] || 'bg-[#94A3B8] text-white'
                        }`}>
                          {report.status}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                          severityColors[(report.assigned_severity || report.suggested_severity).toLowerCase()]
                        }`}>
                          {report.assigned_severity || report.suggested_severity}
                        </span>
                        {report.is_duplicate && (
                          <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-[#F59E0B] text-white">
                            DUPLICATE
                          </span>
                        )}
                      </div>
                      <h3 className="text-base font-semibold text-[#F8FAFC] mb-2">
                        {report.title}
                      </h3>
                      <div className="flex items-center gap-4 text-xs text-[#94A3B8]">
                        <span>Researcher: {report.researcher_name || report.researcher_email}</span>
                        <span>•</span>
                        <span>Submitted {new Date(report.submitted_at).toLocaleDateString()}</span>
                        {report.bounty_amount && (
                          <>
                            <span>•</span>
                            <span className="text-[#10B981]">
                              {report.bounty_amount.toLocaleString()} ETB
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <Link href={`/triage/reports/${report.id}`}>
                      <Button variant="outline" size="sm" className="gap-2">
                        <ExternalLink className="w-4 h-4" />
                        Review
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Back Button */}
          <div className="mt-6">
            <Link href="/triage/programs">
              <Button variant="outline" className="gap-2">
                <ChevronLeft className="w-4 h-4" />
                Back to Programs
              </Button>
            </Link>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
