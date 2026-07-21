'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import { invalidateAllTriageData } from '@/lib/cacheManager';
import Button from '@/components/ui/Button';
import { ChevronLeft, AlertTriangle, User, TrendingUp, FileText, Copy, CheckSquare, X, AlertCircle, Layers } from 'lucide-react';
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
  bounty_amount: number | null;
  submitted_at: string;
  program_name: string;
  program_id: string;
}

interface ResearcherDetail {
  researcher: {
    id: string;
    username: string;
    email: string;
    reputation_score: number;
  };
  reports: Report[];
  total: number;
  stats: {
    total_reports: number;
    valid_reports: number;
    duplicate_reports: number;
    invalid_reports: number;
    spam_score: number;
  };
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

export default function ResearcherDetailPage() {
  const params = useParams();
  const router = useRouter();
  const researcherId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showDuplicatesOnly, setShowDuplicatesOnly] = useState(false);
  const [selectedReports, setSelectedReports] = useState<Set<string>>(new Set());
  const [bulkAction, setBulkAction] = useState<string>('');
  const [originalReportId, setOriginalReportId] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'groups'>('all');
  const [duplicateGroups, setDuplicateGroups] = useState<any[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(false);

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Build endpoint with current filter values
  const endpoint = `/triage/researchers/${researcherId}/reports?show_duplicates_only=${showDuplicatesOnly}${statusFilter ? `&status_filter=${statusFilter}` : ''}`;
  
  console.log('=== RESEARCHER DETAIL PAGE ===');
  console.log('Researcher ID:', researcherId);
  console.log('Status Filter:', statusFilter);
  console.log('Show Duplicates Only:', showDuplicatesOnly);
  console.log('Endpoint:', endpoint);

  const { data, isLoading, error, refetch } = useApiQuery<ResearcherDetail>({
    endpoint,
    queryKey: ['researcher-reports', researcherId, statusFilter, showDuplicatesOnly],
  });

  // Load duplicate groups when switching to groups tab
  useEffect(() => {
    if (activeTab === 'groups' && duplicateGroups.length === 0) {
      loadDuplicateGroups();
    }
  }, [activeTab]);

  const loadDuplicateGroups = async () => {
    setLoadingGroups(true);
    try {
      const response = await api.get(`/triage/researchers/${researcherId}/duplicate-groups`);
      setDuplicateGroups(response.data.groups || []);
    } catch (error) {
      console.error('Failed to load duplicate groups:', error);
    } finally {
      setLoadingGroups(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedReports.size === data?.reports.length) {
      setSelectedReports(new Set());
    } else {
      setSelectedReports(new Set(data?.reports.map(r => r.id) || []));
    }
  };

  const handleSelectReport = (reportId: string) => {
    const newSelected = new Set(selectedReports);
    if (newSelected.has(reportId)) {
      newSelected.delete(reportId);
    } else {
      newSelected.add(reportId);
    }
    setSelectedReports(newSelected);
  };

  const handleBulkAction = async () => {
    console.log('=== FUNCTION CALLED ===');
    console.log('=== Bulk Action Debug ===');
    console.log('Selected reports:', Array.from(selectedReports));
    console.log('Bulk action:', bulkAction);
    console.log('Original report ID:', originalReportId);
    console.log('Researcher ID:', researcherId);
    
    if (selectedReports.size === 0) {
      console.log('ERROR: No reports selected');
      alert('Please select at least one report');
      return;
    }

    if (!bulkAction) {
      console.log('ERROR: No action selected');
      alert('Please select an action');
      return;
    }

    if (bulkAction === 'mark_duplicate' && !originalReportId) {
      console.log('ERROR: No original report ID for duplicate action');
      alert('Please enter the original report ID');
      return;
    }

    console.log('Showing confirmation dialog...');
    const confirmed = confirm(`Are you sure you want to ${bulkAction.replace('_', ' ')} ${selectedReports.size} report(s)?`);
    console.log('User confirmed:', confirmed);

    if (!confirmed) return;

    console.log('Setting isProcessing to true...');
    setIsProcessing(true);
    
    try {
      const reportIds = Array.from(selectedReports);
      console.log('Report IDs array:', reportIds);
      
      // Build query parameters
      const params = new URLSearchParams();
      params.append('action', bulkAction);
      if (bulkAction === 'mark_duplicate' && originalReportId) {
        params.append('duplicate_of', originalReportId);
      }

      const url = `/triage/researchers/${researcherId}/reports/bulk-action?${params.toString()}`;
      console.log('=== SENDING REQUEST ===');
      console.log('Full URL:', url);
      console.log('Request body (report IDs):', reportIds);

      console.log('Calling api.post...');
      const response = await api.post(url, reportIds);
      
      console.log('=== REQUEST SUCCESSFUL ===');
      console.log('Response:', response);
      console.log('Response data:', response.data);

      // Invalidate all triage data
      invalidateAllTriageData(queryClient);

      alert(`Successfully updated ${selectedReports.size} report(s)`);
      setSelectedReports(new Set());
      setBulkAction('');
      setOriginalReportId('');
      await refetch();
      console.log('Refetch completed');
    } catch (error: any) {
      console.error('=== Bulk Action Error ===');
      console.error('Full error:', error);
      console.error('Error response:', error?.response);
      
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error';
      alert(`Failed to perform bulk action: ${errorMessage}`);
    } finally {
      console.log('Setting isProcessing to false...');
      setIsProcessing(false);
    }
  };

  const handleResolveDuplicateGroup = async (originalId: string, duplicateIds: string[]) => {
    if (!confirm(`This will keep the first report as original and mark ${duplicateIds.length} duplicate(s) as invalid. Continue?`)) {
      return;
    }

    setIsProcessing(true);
    try {
      const params = new URLSearchParams();
      params.append('original_id', originalId);
      duplicateIds.forEach(id => params.append('duplicate_ids', id));

      await api.post(
        `/triage/researchers/${researcherId}/resolve-duplicate-group?${params.toString()}`
      );

      alert(`Successfully resolved duplicate group: kept 1 original, marked ${duplicateIds.length} as invalid`);
      loadDuplicateGroups();
      refetch();
    } catch (error: any) {
      alert(`Failed to resolve duplicate group: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Calculate stats
  // Get stats from backend response (calculated from ALL reports, not filtered)
  const duplicateCount = data?.stats?.duplicate_reports || 0;
  const invalidCount = data?.stats?.invalid_reports || 0;
  const spamScore = data?.stats?.spam_score || 0;

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Reports"
          subtitle="Manage all reports from this researcher"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/triage/researchers" className="text-[#3B82F6] hover:underline text-sm">
              Researchers
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">{data?.researcher.username || 'Loading...'}</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading researcher data...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertTriangle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load researcher data</p>
              </div>
            </div>
          ) : data ? (
            <div className="space-y-6">
              {/* Researcher Info */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-[#3B82F6] flex items-center justify-center">
                      <User className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-[#F8FAFC]">{data.researcher.username}</h2>
                      <p className="text-sm text-[#94A3B8]">{data.researcher.email}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <TrendingUp className="w-4 h-4 text-[#10B981]" />
                        <span className="text-sm text-[#94A3B8]">
                          Reputation: <span className="text-[#F8FAFC] font-medium">{data.researcher.reputation_score}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Total Reports</p>
                  <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">{data.stats?.total_reports || 0}</p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Valid</p>
                  <p className="mt-2 text-2xl font-bold text-[#10B981]">
                    {data.stats?.valid_reports || 0}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Duplicates</p>
                  <p className="mt-2 text-2xl font-bold text-[#F59E0B]">{duplicateCount}</p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Invalid</p>
                  <p className="mt-2 text-2xl font-bold text-[#EF4444]">{invalidCount}</p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Spam Score</p>
                  <p className="mt-2 text-2xl font-bold text-[#EF4444]">{spamScore}%</p>
                </div>
              </div>

              {/* Spam Warning */}
              {Number(spamScore) >= 50 && (
                <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-[#EF4444] mb-1">
                        High Spam Risk Detected
                      </p>
                      <p className="text-xs text-[#94A3B8]">
                        This researcher has a spam score of {spamScore}%. Consider reviewing their submission pattern and taking appropriate action.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tabs */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
                <div className="flex border-b border-[#334155]">
                  <button
                    onClick={() => setActiveTab('all')}
                    className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                      activeTab === 'all'
                        ? 'bg-[#3B82F6] text-white'
                        : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#0F172A]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <FileText className="w-4 h-4" />
                      All Reports ({data.total})
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('groups')}
                    className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                      activeTab === 'groups'
                        ? 'bg-[#3B82F6] text-white'
                        : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#0F172A]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <Layers className="w-4 h-4" />
                      Duplicate Groups
                      {duplicateGroups.length > 0 && (
                        <span className="px-2 py-0.5 bg-[#EF4444] text-white text-xs rounded-full">
                          {duplicateGroups.length}
                        </span>
                      )}
                    </div>
                  </button>
                </div>
              </div>

              {/* All Reports Tab */}
              {activeTab === 'all' && (
                <>

              {/* Filters and Bulk Actions */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Filters */}
                  <div className="flex-1 flex gap-2">
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm focus:ring-2 focus:ring-[#3B82F6]"
                    >
                      <option value="">All Statuses</option>
                      <option value="new">New</option>
                      <option value="triaged">Triaged</option>
                      <option value="valid">Valid</option>
                      <option value="invalid">Invalid</option>
                      <option value="duplicate">Duplicate</option>
                      <option value="resolved">Resolved</option>
                    </select>

                    <label className="flex items-center gap-2 px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg cursor-pointer hover:bg-[#1E293B]">
                      <input
                        type="checkbox"
                        checked={showDuplicatesOnly}
                        onChange={(e) => setShowDuplicatesOnly(e.target.checked)}
                        className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                      />
                      <span className="text-sm text-[#F8FAFC]">Duplicates Only</span>
                    </label>
                  </div>

                  {/* Bulk Actions */}
                  {selectedReports.size > 0 && (
                    <div className="flex gap-2">
                      <select
                        value={bulkAction}
                        onChange={(e) => setBulkAction(e.target.value)}
                        className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm focus:ring-2 focus:ring-[#3B82F6]"
                      >
                        <option value="">Select Action...</option>
                        <option value="mark_invalid">Mark as Invalid</option>
                        <option value="mark_duplicate">Mark as Duplicate</option>
                      </select>

                      {bulkAction === 'mark_duplicate' && (
                        <input
                          type="text"
                          placeholder="Original Report ID"
                          value={originalReportId}
                          onChange={(e) => setOriginalReportId(e.target.value)}
                          className="px-3 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] text-sm placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6]"
                        />
                      )}

                      <Button
                        onClick={handleBulkAction}
                        disabled={isProcessing || !bulkAction}
                        size="sm"
                      >
                        {isProcessing ? 'Processing...' : `Apply to ${selectedReports.size}`}
                      </Button>

                      <Button
                        onClick={() => setSelectedReports(new Set())}
                        variant="outline"
                        size="sm"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Reports List */}
              {data.reports.length === 0 ? (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                  <FileText className="w-12 h-12 text-[#94A3B8] mx-auto mb-3" />
                  <p className="text-[#94A3B8]">No reports found</p>
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-[#0F172A] border-b border-[#334155]">
                        <tr>
                          <th className="px-4 py-3 text-left">
                            <input
                              type="checkbox"
                              checked={selectedReports.size === data.reports.length && data.reports.length > 0}
                              onChange={handleSelectAll}
                              className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                            />
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Report
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Severity
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Bounty
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Program
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Submitted
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#334155]">
                        {data.reports.map((report) => (
                          <tr
                            key={report.id}
                            className={`hover:bg-[#0F172A] transition-colors ${
                              selectedReports.has(report.id) ? 'bg-[#3B82F6]/10' : ''
                            }`}
                          >
                            <td className="px-4 py-4">
                              <input
                                type="checkbox"
                                checked={selectedReports.has(report.id)}
                                onChange={() => handleSelectReport(report.id)}
                                className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                              />
                            </td>
                            <td className="px-6 py-4">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <Copy className="w-3 h-3 text-[#3B82F6]" />
                                  <span className="text-xs font-mono text-[#3B82F6]">
                                    {report.report_number}
                                  </span>
                                  {report.is_duplicate && (
                                    <span className="px-1.5 py-0.5 bg-[#F59E0B]/20 text-[#F59E0B] text-xs rounded">
                                      DUP
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm font-medium text-[#F8FAFC] max-w-md truncate">
                                  {report.title}
                                </p>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                statusColors[report.status] || 'bg-[#94A3B8] text-white'
                              }`}>
                                {report.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-center">
                              {report.assigned_severity && (
                                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                  severityColors[report.assigned_severity.toLowerCase()]
                                }`}>
                                  {report.assigned_severity}
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-center">
                              {report.bounty_amount ? (
                                <span className="text-sm font-medium text-[#10B981]">
                                  {report.bounty_amount.toLocaleString()} ETB
                                </span>
                              ) : (
                                <span className="text-sm text-[#94A3B8]">-</span>
                              )}
                            </td>
                            <td className="px-6 py-4">
                              <span className="text-sm text-[#F8FAFC]">{report.program_name}</span>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="text-sm text-[#94A3B8]">
                                {new Date(report.submitted_at).toLocaleDateString()}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <Link href={`/triage/reports/${report.id}`}>
                                <Button variant="outline" size="sm">
                                  View
                                </Button>
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Results Count */}
                  <div className="px-6 py-3 bg-[#0F172A] border-t border-[#334155]">
                    <p className="text-sm text-[#94A3B8]">
                      Showing {data.reports.length} of {data.total} reports
                      {selectedReports.size > 0 && ` • ${selectedReports.size} selected`}
                    </p>
                  </div>
                </div>
              )}

              {/* Close All Reports Tab */}
              </>
              )}

              {/* Duplicate Groups Tab */}
              {activeTab === 'groups' && (
                <>
                  {loadingGroups ? (
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                      <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
                      <p className="mt-4 text-[#94A3B8]">Analyzing reports for duplicates...</p>
                    </div>
                  ) : duplicateGroups.length === 0 ? (
                    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
                      <Layers className="w-12 h-12 text-[#10B981] mx-auto mb-3" />
                      <p className="text-[#F8FAFC] font-medium mb-1">No Duplicate Groups Found</p>
                      <p className="text-sm text-[#94A3B8]">
                        This researcher hasn't submitted the same report multiple times.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Groups Info */}
                      <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="text-sm font-semibold text-[#F59E0B] mb-1">
                              {duplicateGroups.length} Duplicate Group(s) Detected
                            </p>
                            <p className="text-xs text-[#94A3B8]">
                              These reports have similar titles and were submitted by the same researcher. 
                              Recommended action: Keep the first submission, mark the rest as invalid (spam).
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Duplicate Groups */}
                      {duplicateGroups.map((group, index) => (
                        <div key={index} className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
                          <div className="bg-[#0F172A] px-6 py-4 border-b border-[#334155]">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Layers className="w-5 h-5 text-[#F59E0B]" />
                                  <h3 className="text-lg font-semibold text-[#F8FAFC]">
                                    Group {index + 1}
                                  </h3>
                                  <span className="px-2 py-1 bg-[#F59E0B]/20 text-[#F59E0B] text-xs font-bold rounded">
                                    {group.count} Reports
                                  </span>
                                </div>
                                <p className="text-sm text-[#94A3B8] line-clamp-2">
                                  {group.title}
                                </p>
                              </div>
                              <Button
                                onClick={() => handleResolveDuplicateGroup(group.original_id, group.duplicate_ids)}
                                disabled={isProcessing}
                                size="sm"
                                className="gap-2"
                              >
                                <CheckSquare className="w-4 h-4" />
                                {isProcessing ? 'Processing...' : 'Resolve Group'}
                              </Button>
                            </div>
                          </div>

                          <div className="p-6 space-y-3">
                            {group.reports.map((report: any, reportIndex: number) => (
                              <div
                                key={report.id}
                                className={`p-4 rounded-lg border ${
                                  reportIndex === 0
                                    ? 'bg-[#10B981]/10 border-[#10B981]/30'
                                    : 'bg-[#EF4444]/10 border-[#EF4444]/30'
                                }`}
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                      {reportIndex === 0 ? (
                                        <span className="px-2 py-1 bg-[#10B981] text-white text-xs font-bold rounded">
                                          ORIGINAL (Keep)
                                        </span>
                                      ) : (
                                        <span className="px-2 py-1 bg-[#EF4444] text-white text-xs font-bold rounded">
                                          DUPLICATE #{reportIndex}
                                        </span>
                                      )}
                                      <Copy className="w-3 h-3 text-[#3B82F6]" />
                                      <span className="text-xs font-mono text-[#3B82F6]">
                                        {report.report_number}
                                      </span>
                                      <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                        statusColors[report.status] || 'bg-[#94A3B8] text-white'
                                      }`}>
                                        {report.status}
                                      </span>
                                    </div>
                                    <p className="text-sm text-[#F8FAFC] mb-2">{report.title}</p>
                                    <div className="flex items-center gap-3 text-xs text-[#94A3B8]">
                                      <span>
                                        Submitted {new Date(report.submitted_at).toLocaleDateString()}
                                      </span>
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
                                    <Button variant="outline" size="sm">
                                      View
                                    </Button>
                                  </Link>
                                </div>
                              </div>
                            ))}
                          </div>

                          <div className="bg-[#0F172A] px-6 py-3 border-t border-[#334155]">
                            <p className="text-xs text-[#94A3B8]">
                              <span className="font-semibold text-[#F8FAFC]">Recommended Action:</span> Keep the first report 
                              (submitted {new Date(group.reports[0].submitted_at).toLocaleDateString()}) and mark {group.count - 1} duplicate(s) as invalid.
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
