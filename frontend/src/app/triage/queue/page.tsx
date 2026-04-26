'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, X, CheckCircle, XCircle } from 'lucide-react';

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
  // Database relations
  program_name?: string;
  researcher_name?: string;
  researcher_email?: string;
}

interface QueueResponse {
  reports: Report[];
  total: number;
  limit: number;
  offset: number;
}

export default function TriageQueuePage() {
  const user = useAuthStore((state) => state.user);
  const searchParams = useSearchParams();
  const router = useRouter();
  
  // Get status from URL query parameter (e.g., ?status=validated)
  const urlStatus = searchParams.get('status') || '';
  
  // Map URL status values to backend status values
  const mapStatusToBackend = (status: string): string => {
    const statusMap: Record<string, string> = {
      'validated': 'valid',
      'in-progress': 'triaged',
      'rejected': 'invalid',
    };
    return statusMap[status] || status;
  };
  
  const [statusFilter, setStatusFilter] = useState<string>(urlStatus);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;
  
  // Track assigned reports
  const [assignedReports, setAssignedReports] = useState<Set<string>>(new Set());

  // Modal states
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [triageStatus, setTriageStatus] = useState<string>('');
  const [assignedSeverity, setAssignedSeverity] = useState<string>('');
  const [bountyAmount, setBountyAmount] = useState<string>('');
  const [triageNotes, setTriageNotes] = useState<string>('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');
  
  // Similar reports for duplicate detection
  const [similarReports, setSimilarReports] = useState<Report[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [selectedDuplicateOf, setSelectedDuplicateOf] = useState<string>('');

  // Update status filter when URL changes
  useEffect(() => {
    setStatusFilter(urlStatus);
    setPage(0); // Reset to first page when filter changes
  }, [urlStatus]);

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
    return () => {
      // Optional: remove dark class when leaving triage portal
      // document.documentElement.classList.remove('dark');
    };
  }, []);

  const queryParams = new URLSearchParams();
  if (statusFilter) queryParams.append('status_filter', mapStatusToBackend(statusFilter));
  if (severityFilter) queryParams.append('severity_filter', severityFilter);
  queryParams.append('limit', limit.toString());
  queryParams.append('offset', (page * limit).toString());

  const endpoint = `/triage/queue?${queryParams.toString()}`;

  const { data, isLoading, error, refetch } = useApiQuery<QueueResponse>({
    endpoint,
  });

  // Fetch statistics for accurate counts
  const { data: stats, refetch: refetchStats } = useApiQuery<any>({
    endpoint: '/triage/statistics',
  });

  const reports = data?.reports || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);
  
  // Filter reports based on search query (client-side filtering)
  const filteredReports = searchQuery 
    ? reports.filter(report => 
        report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.report_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (report.researcher_name && report.researcher_name.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : reports;
  
  // Calculate new reports count from current page
  const newReportsCount = filteredReports.filter((r) => r.status === 'new').length;

  // Loading states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  // Handle opening review modal
  const handleReviewReport = (report: Report) => {
    setSelectedReport(report);
    setTriageStatus('');
    setAssignedSeverity(report.assigned_severity || report.suggested_severity);
    setBountyAmount(report.bounty_amount?.toString() || '');
    setTriageNotes('');
    setSimilarReports([]);
    setSelectedDuplicateOf('');
    setReviewModalOpen(true);
  };
  
  // Find similar reports for duplicate detection
  const handleFindSimilar = async () => {
    if (!selectedReport) return;
    
    setLoadingSimilar(true);
    try {
      const response = await api.get(`/triage/reports/${selectedReport.id}/similar?limit=10`);
      setSimilarReports(response.data.similar_reports || []);
      
      if (response.data.similar_reports?.length === 0) {
        setShowToast(true);
        setToastMessage('No similar reports found');
        setToastType('success');
      }
    } catch (error: any) {
      console.error('Find similar error:', error);
      setShowToast(true);
      setToastMessage('Failed to find similar reports');
      setToastType('error');
    } finally {
      setLoadingSimilar(false);
    }
  };

  // Handle submitting triage
  const handleSubmitTriage = async () => {
    if (!selectedReport || !triageStatus) return;

    setIsSubmitting(true);
    try {
      // Update triage status and severity
      const payload: any = {
        status: triageStatus,
        assigned_severity: assignedSeverity || undefined,
        triage_notes: triageNotes || undefined,
      };
      
      // If marking as duplicate and a duplicate report is selected
      if (triageStatus === 'duplicate' && selectedDuplicateOf) {
        payload.is_duplicate = true;
        payload.duplicate_of = selectedDuplicateOf;
      }

      await api.post(`/triage/reports/${selectedReport.id}/update`, payload);

      // If status is valid and bounty amount is provided, approve bounty
      if (triageStatus === 'valid' && bountyAmount) {
        try {
          await api.post(`/reports/${selectedReport.id}/bounty/approve?bounty_amount=${bountyAmount}`);
        } catch (bountyError) {
          console.error('Failed to set bounty:', bountyError);
          // Don't fail the whole operation if bounty fails
        }
      }

      setShowToast(true);
      setToastMessage('Report triaged successfully!');
      setToastType('success');
      setReviewModalOpen(false);
      
      // Refetch data to update the UI
      await refetch();
      await refetchStats();
    } catch (error: any) {
      setShowToast(true);
      setToastMessage(error?.response?.data?.detail || error?.message || 'Failed to triage report');
      setToastType('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle assigning report to current user (mark as in progress)
  const handleAssignToMe = async (reportId: string) => {
    setIsAssigning(true);
    try {
      const response = await api.post(`/triage/reports/${reportId}/update`, { 
        status: 'triaged'
      });

      // Mark this report as assigned
      setAssignedReports(prev => new Set(prev).add(reportId));

      setShowToast(true);
      setToastMessage('Report assigned to you and marked as In Progress!');
      setToastType('success');
      
      // Refetch data to update the UI immediately
      await refetch();
      await refetchStats();
    } catch (error: any) {
      console.error('Assign error:', error);
      const errorDetail = error?.response?.data?.detail || error?.message || 'Failed to assign report';
      setShowToast(true);
      setToastMessage(errorDetail);
      setToastType('error');
    } finally {
      setIsAssigning(false);
    }
  };

  // Handle viewing report details
  const handleViewDetails = (reportId: string) => {
    router.push(`/triage/reports/${reportId}`);
  };

  // Toast auto-hide
  useEffect(() => {
    if (showToast) {
      const timer = setTimeout(() => setShowToast(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [showToast]);

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
              {statusFilter && (
                <span className="px-3 py-1 rounded-lg bg-[#3B82F6] text-white text-sm font-semibold">
                  Filter: {statusFilter === 'validated' ? 'Validated' : statusFilter === 'in-progress' ? 'In Progress' : statusFilter === 'rejected' ? 'Rejected' : statusFilter}
                </span>
              )}
              {severityFilter && (
                <span className="px-3 py-1 rounded-lg bg-[#F59E0B] text-white text-sm font-semibold">
                  {severityFilter.charAt(0).toUpperCase() + severityFilter.slice(1)}
                </span>
              )}
              {newReportsCount > 0 && !statusFilter && !severityFilter && (
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
                {stats?.status_breakdown?.new || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                In Progress
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {stats?.status_breakdown?.triaged || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                Validated
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {stats?.status_breakdown?.valid || 0}
              </p>
            </div>
            <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                Rejected
              </p>
              <p className="text-3xl font-bold text-slate-100">
                {stats?.status_breakdown?.invalid || 0}
              </p>
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
            
            {/* Status Filters */}
            <div className="flex gap-2 border-l border-[#334155] pl-2">
              <button
                onClick={() => {
                  setStatusFilter('validated');
                  setSeverityFilter('');
                  setPage(0);
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'validated'
                    ? 'bg-[#3B82F6] text-white'
                    : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
                }`}
              >
                Validated
              </button>
              <button
                onClick={() => {
                  setStatusFilter('in-progress');
                  setSeverityFilter('');
                  setPage(0);
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'in-progress'
                    ? 'bg-[#3B82F6] text-white'
                    : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
                }`}
              >
                In Progress
              </button>
              <button
                onClick={() => {
                  setStatusFilter('rejected');
                  setSeverityFilter('');
                  setPage(0);
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === 'rejected'
                    ? 'bg-[#3B82F6] text-white'
                    : 'bg-[#1E293B] text-slate-300 hover:bg-[#334155]'
                }`}
              >
                Rejected
              </button>
            </div>
            
            {/* Severity Filters */}
            <div className="flex gap-2 border-l border-[#334155] pl-2">
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
            </div>
            
            <div className="ml-auto flex items-center gap-2 bg-[#1E293B] rounded-lg px-4 py-2 border border-[#334155]">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-slate-300 placeholder-slate-500 outline-none text-sm w-48"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="text-slate-400 hover:text-slate-300"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
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
            ) : filteredReports.length === 0 ? (
              <div className="bg-[#1E293B] rounded-lg p-12 text-center border border-[#334155]">
                <p className="text-slate-400">No reports match your search</p>
                <button
                  onClick={() => setSearchQuery('')}
                  className="mt-4 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Clear Search
                </button>
              </div>
            ) : (
              filteredReports.map((report) => (
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
                        {report.program_name && (
                          <>
                            <span>•</span>
                            <span>{report.program_name}</span>
                          </>
                        )}
                        {report.researcher_name && (
                          <>
                            <span>•</span>
                            <span>👤 {report.researcher_name}</span>
                          </>
                        )}
                        <span>•</span>
                        <span>🕐 {new Date(report.submitted_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                          hour12: true
                        })}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-3 py-1 rounded text-xs font-bold uppercase ${
                          (report.assigned_severity || report.suggested_severity) === 'critical'
                            ? 'bg-[#EF4444] text-white'
                            : (report.assigned_severity || report.suggested_severity) === 'high'
                            ? 'bg-[#F59E0B] text-white'
                            : (report.assigned_severity || report.suggested_severity) === 'medium'
                            ? 'bg-[#F59E0B] text-white'
                            : (report.assigned_severity || report.suggested_severity) === 'low'
                            ? 'bg-[#3B82F6] text-white'
                            : 'bg-slate-600 text-white'
                        }`}
                      >
                        {report.assigned_severity || report.suggested_severity}
                      </span>
                      <span className={`px-3 py-1 rounded text-xs font-medium ${
                        report.status === 'new' ? 'bg-[#EF4444] text-white' :
                        report.status === 'triaged' ? 'bg-[#F59E0B] text-white' :
                        report.status === 'valid' ? 'bg-[#3B82F6] text-white' :
                        report.status === 'invalid' ? 'bg-[#94A3B8] text-white' :
                        report.status === 'duplicate' ? 'bg-[#94A3B8] text-white' :
                        report.status === 'resolved' ? 'bg-[#10B981] text-white' :
                        'bg-slate-600 text-white'
                      }`}>
                        {report.status === 'new' ? 'New' :
                         report.status === 'triaged' ? 'In Progress' :
                         report.status === 'valid' ? 'Validated' :
                         report.status === 'invalid' ? 'Invalid' :
                         report.status === 'duplicate' ? 'Duplicate' :
                         report.status === 'resolved' ? 'Resolved' :
                         report.status}
                      </span>
                    </div>
                  </div>
                  <p className="text-slate-300 text-sm mb-4 line-clamp-2">
                    {report.description}
                  </p>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={() => handleReviewReport(report)}
                      className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      Review Report
                    </button>
                    <button 
                      onClick={() => handleViewDetails(report.id)}
                      className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-slate-300 rounded-lg text-sm font-medium transition-colors border border-[#334155]"
                    >
                      View Details
                    </button>
                    <button 
                      onClick={() => handleAssignToMe(report.id)}
                      disabled={isAssigning || assignedReports.has(report.id) || report.status === 'triaged'}
                      className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-slate-300 rounded-lg text-sm font-medium transition-colors border border-[#334155] disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {assignedReports.has(report.id) || report.status === 'triaged' 
                        ? 'Assigned' 
                        : isAssigning 
                        ? 'Assigning...' 
                        : 'Assign to Me'}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          {!searchQuery && totalPages > 1 && (
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
          
          {searchQuery && filteredReports.length > 0 && (
            <div className="mt-6">
              <p className="text-sm text-slate-400 text-center">
                Showing {filteredReports.length} of {reports.length} reports
              </p>
            </div>
          )}

          {/* Review Modal */}
          <Modal
            isOpen={reviewModalOpen}
            onClose={() => setReviewModalOpen(false)}
            title="Review Report"
          >
            {selectedReport && (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    {selectedReport.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {selectedReport.report_number}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Triage Decision
                  </label>
                  <Select
                    value={triageStatus}
                    onChange={(e) => setTriageStatus(e.target.value)}
                    className="w-full"
                  >
                    <option value="">Select status...</option>
                    <option value="valid">Valid</option>
                    <option value="invalid">Invalid</option>
                    <option value="duplicate">Duplicate</option>
                    <option value="triaged">In Progress</option>
                  </Select>
                </div>

                {triageStatus === 'duplicate' && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                    <div className="flex items-start gap-2 mb-3">
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div className="flex-1">
                        <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-1">
                          Marking as Duplicate
                        </h4>
                        <p className="text-sm text-amber-800 dark:text-amber-200 mb-2">
                          Find similar reports to identify the original report this is a duplicate of.
                        </p>
                        <p className="text-xs text-amber-700 dark:text-amber-300">
                          Note: According to BR-07, duplicate reports submitted within 24 hours of the original may receive 50% bounty.
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={handleFindSimilar}
                      disabled={loadingSimilar}
                      className="w-full px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                    >
                      {loadingSimilar ? 'Searching...' : 'Find Similar Reports'}
                    </button>
                    
                    {similarReports.length > 0 && (
                      <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                        <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                          Similar Reports ({similarReports.length}):
                        </p>
                        {similarReports.map((similar) => (
                          <div
                            key={similar.id}
                            onClick={() => setSelectedDuplicateOf(similar.id)}
                            className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                              selectedDuplicateOf === similar.id
                                ? 'bg-amber-100 dark:bg-amber-800 border-amber-400 dark:border-amber-600'
                                : 'bg-white dark:bg-slate-800 border-amber-200 dark:border-amber-700 hover:bg-amber-50 dark:hover:bg-amber-900/30'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-xs font-mono text-amber-700 dark:text-amber-300">
                                    {similar.report_number}
                                  </span>
                                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                    similar.status === 'valid' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                    similar.status === 'invalid' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                    'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
                                  }`}>
                                    {similar.status}
                                  </span>
                                </div>
                                <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                                  {similar.title}
                                </p>
                                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                                  {new Date(similar.submitted_at).toLocaleDateString()}
                                </p>
                              </div>
                              {selectedDuplicateOf === similar.id && (
                                <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Assigned Severity
                  </label>
                  <Select
                    value={assignedSeverity}
                    onChange={(e) => setAssignedSeverity(e.target.value)}
                    className="w-full"
                  >
                    <option value="">Select severity...</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                  </Select>
                </div>

                {triageStatus === 'valid' && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Bounty Amount (ETB)
                    </label>
                    <input
                      type="number"
                      value={bountyAmount}
                      onChange={(e) => setBountyAmount(e.target.value)}
                      placeholder="Enter bounty amount"
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Triage Notes
                  </label>
                  <Textarea
                    value={triageNotes}
                    onChange={(e) => setTriageNotes(e.target.value)}
                    placeholder="Add notes about your triage decision..."
                    rows={4}
                    className="w-full"
                  />
                </div>

                <div className="flex gap-2 justify-end pt-4">
                  <Button
                    onClick={() => setReviewModalOpen(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSubmitTriage}
                    disabled={!triageStatus || isSubmitting}
                    className="bg-[#3B82F6] hover:bg-[#2563EB] text-white"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Triage'}
                  </Button>
                </div>
              </div>
            )}
          </Modal>

          {/* Toast Notification */}
          {showToast && (
            <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-5">
              <div className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg ${
                toastType === 'success' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-red-500 text-white'
              }`}>
                {toastType === 'success' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <XCircle className="w-5 h-5" />
                )}
                <span className="font-medium">{toastMessage}</span>
                <button
                  onClick={() => setShowToast(false)}
                  className="ml-2 hover:opacity-80"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
