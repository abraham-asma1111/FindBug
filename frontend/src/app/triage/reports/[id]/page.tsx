'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { api } from '@/lib/api';
import { invalidateAllTriageData } from '@/lib/cacheManager';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, ChevronLeft, Save, CheckCircle, Copy, Paperclip, Download, FileText, Image, Video, File, Search, User, X } from 'lucide-react';
import Link from 'next/link';

interface ReportDetail {
  id: string;
  report_number: string;
  title: string;
  description: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  affected_asset: string | null;
  vulnerability_type: string | null;
  status: string;
  assigned_severity: string | null;
  suggested_severity: string;
  cvss_score: number | null;
  vrt_category: string | null;
  bounty_amount: number | null;
  submitted_at?: string;
  created_at?: string;
  updated_at?: string;
  triaged_at: string | null;
  triaged_by: string | null;
  is_duplicate: boolean;
  duplicate_of: string | null;
  triage_notes: string | null;
  program_id?: string;
  researcher_id?: string;
  program?: {
    id: string;
    name: string;
  };
  researcher?: {
    id: string;
    username: string;
  };
  attachments?: Array<{
    id: string;
    filename: string;
    original_filename?: string;
    file_type: string;
    file_size: number;
    uploaded_at: string | null;
  }>;
}

interface ReportAttachmentsResponse {
  attachments: Array<{
    id: string;
    filename: string;
    original_filename?: string;
    file_type: string;
    file_size: number;
    uploaded_at: string | null;
  }>;
}

function mergeEvidenceAttachments(
  reportAttachments: ReportDetail['attachments'],
  listedAttachments: ReportAttachmentsResponse['attachments'] | undefined
) {
  const merged = new Map<string, NonNullable<ReportDetail['attachments']>[number]>();

  for (const attachment of reportAttachments || []) {
    merged.set(attachment.id, attachment);
  }

  for (const attachment of listedAttachments || []) {
    merged.set(attachment.id, attachment);
  }

  return Array.from(merged.values());
}

const severityColors: Record<string, string> = {
  critical: 'bg-[#EF4444] text-white',
  high: 'bg-[#F59E0B] text-white',
  medium: 'bg-[#F59E0B] text-white',
  low: 'bg-[#3B82F6] text-white',
  info: 'bg-[#94A3B8] text-white',
};

const statusColors: Record<string, string> = {
  new: 'bg-[#EF4444] text-white',
  triaged: 'bg-[#F59E0B] text-white',
  valid: 'bg-[#3B82F6] text-white',
  invalid: 'bg-[#EF4444] text-white',
  duplicate: 'bg-[#94A3B8] text-white',
  resolved: 'bg-[#3B82F6] text-white',
};

export default function TriageReportDetailPage() {
  const params = useParams();
  const reportId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Form state
  const [status, setStatus] = useState('');
  const [assignedSeverity, setAssignedSeverity] = useState('');
  const [cvssScore, setCvssScore] = useState('');
  const [vrtCategory, setVrtCategory] = useState('');
  const [triageNotes, setTriageNotes] = useState('');
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [duplicateOf, setDuplicateOf] = useState('');
  const [similarReports, setSimilarReports] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [researcherReports, setResearcherReports] = useState<any[]>([]);
  const [loadingResearcherReports, setLoadingResearcherReports] = useState(false);
  const [showResearcherReports, setShowResearcherReports] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [showTemplates, setShowTemplates] = useState(false);

  const { data: templatesData } = useApiQuery<{ templates: Array<{ id: string; name: string; title: string; content: string; category: string }> }>({
    endpoint: '/triage/templates?limit=100',
  });

  const { data: report, isLoading, error, refetch } = useApiQuery<ReportDetail>({
    endpoint: `/reports/${reportId}`,
  });
  const {
    data: attachmentsResponse,
    isLoading: attachmentsLoading,
    error: attachmentsError,
  } = useApiQuery<ReportAttachmentsResponse>({
    endpoint: `/reports/${reportId}/attachments`,
    enabled: !!reportId,
  });

  // Initialize form when report loads
  useEffect(() => {
    if (report) {
      setStatus(report.status || '');
      setAssignedSeverity(report.assigned_severity || report.suggested_severity || '');
      setCvssScore(report.cvss_score?.toString() || '');
      setVrtCategory(report.vrt_category || '');
      setTriageNotes(report.triage_notes || '');
      setIsDuplicate(report.is_duplicate || false);
      setDuplicateOf(report.duplicate_of || '');
    }
  }, [report]);

  const updateMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      invalidateAllTriageData(queryClient);
      alert('Report updated successfully');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || error.message || 'Unknown error';
      alert(`Failed to update report: ${errorMessage}`);
      console.error('Update error:', error);
    },
  });

  const acknowledgeMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      invalidateAllTriageData(queryClient);
      alert('Report acknowledged successfully');
    },
  });

  const resolveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      invalidateAllTriageData(queryClient);
      alert('Report resolved successfully');
    },
  });

  const handleUpdate = () => {
    // Validate required fields
    if (!status) {
      alert('Please select a status');
      return;
    }

    // Prepare payload with proper validation
    const payload: any = {
      status: status.toLowerCase(),
    };

    // Only include assigned_severity if it's set and valid
    if (assignedSeverity && assignedSeverity.trim()) {
      payload.assigned_severity = assignedSeverity.toLowerCase();
    }

    // Only include cvss_score if it's a valid number
    if (cvssScore && !isNaN(parseFloat(cvssScore))) {
      payload.cvss_score = parseFloat(cvssScore);
    }

    // Only include vrt_category if it's set
    if (vrtCategory && vrtCategory.trim()) {
      payload.vrt_category = vrtCategory;
    }

    // Only include triage_notes if it's set
    if (triageNotes && triageNotes.trim()) {
      payload.triage_notes = triageNotes;
    }

    // CRITICAL: Only include duplicate fields when explicitly marking as duplicate
    // This prevents clearing duplicate status on regular updates
    if (isDuplicate) {
      payload.is_duplicate = true;
      if (duplicateOf && duplicateOf.trim()) {
        payload.duplicate_of = duplicateOf;
      } else {
        alert('Please select the original report to mark as duplicate');
        return;
      }
    }

    updateMutation.mutate({ endpoint: `/triage/reports/${reportId}/update`, ...payload });
  };

  const handleFindSimilar = async () => {
    setLoadingSimilar(true);
    try {
      const response = await api.get(`/triage/reports/${reportId}/similar?limit=10`);
      setSimilarReports(response.data.similar_reports || []);
    } catch (error) {
      alert('Failed to find similar reports');
    } finally {
      setLoadingSimilar(false);
    }
  };

  const handleSelectOriginal = (selectedReportId: string) => {
    setDuplicateOf(selectedReportId);
  };

  const handleLoadResearcherReports = async () => {
    if (!report?.researcher?.id) {
      alert('Researcher information not available');
      return;
    }
    
    setLoadingResearcherReports(true);
    try {
      const response = await api.get(`/reports?limit=100`);
      // Filter reports from same researcher
      const sameResearcher = response.data.reports.filter(
        (r: any) => r.researcher_id === report?.researcher?.id && r.id !== report.id
      );
      setResearcherReports(sameResearcher);
      setShowResearcherReports(true);
    } catch (error) {
      console.error('Failed to load researcher reports:', error);
      alert('Failed to load researcher reports');
    } finally {
      setLoadingResearcherReports(false);
    }
  };

  const handleAcknowledge = () => {
    acknowledgeMutation.mutate({ endpoint: `/triage/reports/${reportId}/acknowledge` });
  };

  const handleResolve = () => {
    resolveMutation.mutate({
      endpoint: `/triage/reports/${reportId}/resolve`,
      resolution_notes: triageNotes,
    });
  };

  const handleViewAttachment = async (attachmentId: string, filename: string, fileType: string) => {
    try {
      const response = await api.get(`/reports/${reportId}/attachments/${attachmentId}/download`, {
        responseType: 'blob',
      });
      
      // Create blob URL
      const blob = new Blob([response.data], { type: fileType });
      const url = window.URL.createObjectURL(blob);
      
      // Open in new tab
      const newWindow = window.open(url, '_blank');
      
      // Clean up after window loads or after delay
      if (newWindow) {
        newWindow.onload = () => {
          setTimeout(() => window.URL.revokeObjectURL(url), 1000);
        };
      } else {
        setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      }
    } catch (error: any) {
      console.error('Failed to view attachment:', error);
      alert(`Failed to view file: ${error.response?.data?.detail || error.message}`);
    }
  };

  const reportData = report;
  const evidenceAttachments = mergeEvidenceAttachments(
    reportData?.attachments,
    attachmentsResponse?.attachments
  );

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Report Details"
          subtitle="Review and validate report"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/triage/queue" className="text-[#3B82F6] hover:underline text-sm">
              Queue
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">Report Details</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading report...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load report</p>
              </div>
            </div>
          ) : reportData ? (
            <div className="space-y-6">
              {/* Report Header */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                      {reportData.title}
                    </h2>
                    <div className="flex items-center gap-3 text-sm text-[#94A3B8]">
                      <span className="flex items-center gap-1">
                        <Copy className="w-4 h-4" />
                        {reportData.report_number}
                      </span>
                      <span>•</span>
                      <span>Submitted {new Date(reportData.submitted_at || reportData.created_at || '').toLocaleDateString()}</span>
                      {reportData.program?.name && (
                        <>
                          <span>•</span>
                          <span>Program: {reportData.program.name}</span>
                        </>
                      )}
                      {reportData.researcher?.username && (
                        <>
                          <span>•</span>
                          <span>Researcher: {reportData.researcher.username}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColors[reportData.status] || 'bg-[#94A3B8] text-white'}`}>
                      {reportData.status}
                    </span>
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${severityColors[reportData.assigned_severity?.toLowerCase() || reportData.suggested_severity?.toLowerCase() || 'info']}`}>
                      {reportData.assigned_severity || reportData.suggested_severity}
                    </span>
                  </div>
                </div>
                
                {/* Researcher Reports Button */}
                <div className="mt-4 pt-4 border-t border-[#334155]">
                  <Button
                    onClick={handleLoadResearcherReports}
                    disabled={loadingResearcherReports}
                    variant="outline"
                    className="gap-2"
                  >
                    <User className="w-4 h-4" />
                    {loadingResearcherReports ? 'Loading...' : `View All Reports from ${reportData.researcher?.username || 'This Researcher'}`}
                  </Button>
                </div>
              </div>

              {/* Researcher Reports Panel */}
              {showResearcherReports && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-[#F8FAFC] flex items-center gap-2">
                      <User className="w-5 h-5" />
                      All Reports from {reportData.researcher?.username} ({researcherReports.length})
                    </h3>
                    <button
                      onClick={() => setShowResearcherReports(false)}
                      className="text-[#94A3B8] hover:text-[#F8FAFC]"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  {researcherReports.length === 0 ? (
                    <p className="text-[#94A3B8] text-center py-4">
                      No other reports from this researcher
                    </p>
                  ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {researcherReports.map((report: any) => (
                        <div
                          key={report.id}
                          className="p-4 bg-[#0F172A] rounded-lg border border-[#334155] hover:border-[#3B82F6] transition-colors"
                        >
                          <div className="flex items-start justify-between gap-3">
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
                                {report.assigned_severity && (
                                  <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                    severityColors[report.assigned_severity.toLowerCase()]
                                  }`}>
                                    {report.assigned_severity}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-[#F8FAFC] font-medium mb-1">
                                {report.title}
                              </p>
                              <div className="flex items-center gap-3 text-xs text-[#94A3B8]">
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
                              <Button variant="outline" size="sm">
                                View
                              </Button>
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Duplicate Pattern Warning */}
                  {researcherReports.filter((r: any) => r.is_duplicate).length > 2 && (
                    <div className="mt-4 p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-[#EF4444] mb-1">
                            Potential Spam Pattern Detected
                          </p>
                          <p className="text-xs text-[#94A3B8]">
                            This researcher has {researcherReports.filter((r: any) => r.is_duplicate).length} duplicate reports. 
                            Consider reviewing their submission pattern for potential abuse.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Attachments/Evidence Section - ALWAYS SHOW */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <Paperclip className="w-5 h-5" />
                  Evidence & Attachments ({evidenceAttachments.length})
                </h3>
                
                {attachmentsLoading && evidenceAttachments.length === 0 ? (
                  <div className="text-center py-8 text-[#94A3B8]">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
                    <p className="mt-4 text-sm">Loading evidence files...</p>
                  </div>
                ) : attachmentsError && evidenceAttachments.length === 0 ? (
                  <div className="text-center py-8 text-[#94A3B8]">
                    <AlertCircle className="w-12 h-12 mx-auto mb-3 text-[#EF4444]" />
                    <p className="text-sm">Failed to load evidence files</p>
                  </div>
                ) : evidenceAttachments.length === 0 ? (
                  <div className="text-center py-8 text-[#94A3B8]">
                    <Paperclip className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No evidence files attached to this report</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {evidenceAttachments.map((attachment) => {
                      const getFileIcon = (fileType: string) => {
                        if (fileType.startsWith('image/')) return <Image className="w-5 h-5 text-[#3B82F6]" />;
                        if (fileType.startsWith('video/')) return <Video className="w-5 h-5 text-[#8B5CF6]" />;
                        if (fileType.includes('pdf')) return <FileText className="w-5 h-5 text-[#EF4444]" />;
                        return <File className="w-5 h-5 text-[#94A3B8]" />;
                      };

                      const formatFileSize = (bytes: number) => {
                        if (bytes < 1024) return bytes + ' B';
                        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
                        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
                      };

                      return (
                        <div
                          key={attachment.id}
                          onClick={() => handleViewAttachment(attachment.id, attachment.filename, attachment.file_type)}
                          className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg border border-[#334155] hover:border-[#3B82F6] transition-colors cursor-pointer"
                        >
                          {getFileIcon(attachment.file_type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-[#F8FAFC] truncate">
                              {attachment.original_filename || attachment.filename}
                            </p>
                            <p className="text-xs text-[#94A3B8]">
                              {formatFileSize(attachment.file_size)} • {attachment.uploaded_at ? new Date(attachment.uploaded_at).toLocaleDateString() : 'Unknown date'}
                            </p>
                          </div>
                          <div className="p-2 rounded-lg">
                            <Download className="w-4 h-4 text-[#94A3B8]" />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Report Details - What Researcher Submitted */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Report Details
                </h3>
                
                {/* Vulnerability Info Grid */}
                {(reportData.vulnerability_type || reportData.affected_asset) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                    {reportData.vulnerability_type && (
                      <div>
                        <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Vulnerability Type</p>
                        <p className="text-[#F8FAFC] font-medium">{reportData.vulnerability_type}</p>
                      </div>
                    )}
                    {reportData.affected_asset && (
                      <div>
                        <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Affected Asset</p>
                        <p className="text-[#F8FAFC] font-medium">{reportData.affected_asset}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Description */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Description</h4>
                  <div className="prose prose-invert max-w-none p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                    <p className="text-[#F8FAFC] leading-relaxed whitespace-pre-wrap">
                      {reportData.description}
                    </p>
                  </div>
                </div>

                {/* Steps to Reproduce */}
                {reportData.steps_to_reproduce && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Steps to Reproduce</h4>
                    <div className="prose prose-invert max-w-none p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] leading-relaxed whitespace-pre-wrap">
                        {reportData.steps_to_reproduce}
                      </p>
                    </div>
                  </div>
                )}

                {/* Impact Assessment */}
                {reportData.impact_assessment && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Impact Assessment</h4>
                    <div className="prose prose-invert max-w-none p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                      <p className="text-[#F8FAFC] leading-relaxed whitespace-pre-wrap">
                        {reportData.impact_assessment}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Triage Form */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Triage Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Status
                    </label>
                    <Select
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                      options={[
                        { value: 'new', label: 'New' },
                        { value: 'triaged', label: 'Triaged' },
                        { value: 'valid', label: 'Valid' },
                        { value: 'invalid', label: 'Invalid' },
                        { value: 'duplicate', label: 'Duplicate' },
                        { value: 'resolved', label: 'Resolved' },
                      ]}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Assigned Severity
                    </label>
                    <Select
                      value={assignedSeverity}
                      onChange={(e) => setAssignedSeverity(e.target.value)}
                      options={[
                        { value: 'critical', label: 'Critical' },
                        { value: 'high', label: 'High' },
                        { value: 'medium', label: 'Medium' },
                        { value: 'low', label: 'Low' },
                        { value: 'info', label: 'Info' },
                      ]}
                    />
                    <p className="mt-1 text-xs text-[#94A3B8]">
                      💡 Bounty will be auto-calculated from program reward tiers
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      CVSS Score (0-10)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={cvssScore}
                      onChange={(e) => setCvssScore(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      VRT Category
                    </label>
                    <input
                      type="text"
                      value={vrtCategory}
                      onChange={(e) => setVrtCategory(e.target.value)}
                      placeholder="e.g., server_security_misconfiguration"
                      className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="flex items-center gap-2 text-sm font-medium text-[#94A3B8] mb-2">
                    <input
                      type="checkbox"
                      checked={isDuplicate}
                      onChange={(e) => {
                        setIsDuplicate(e.target.checked);
                        if (e.target.checked) {
                          handleFindSimilar();
                        } else {
                          setSimilarReports([]);
                          setDuplicateOf('');
                        }
                      }}
                      className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                    />
                    Mark as Duplicate
                  </label>
                  
                  {isDuplicate && (
                    <div className="space-y-3 mt-3">
                      <Button
                        onClick={handleFindSimilar}
                        disabled={loadingSimilar}
                        variant="outline"
                        className="w-full gap-2"
                      >
                        <Search className="w-4 h-4" />
                        {loadingSimilar ? 'Searching...' : 'Find Similar Reports'}
                      </Button>

                      {similarReports.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-[#94A3B8]">
                            Select the original report (click to select):
                          </p>
                          <div className="max-h-64 overflow-y-auto space-y-2">
                            {similarReports.map((similar) => (
                              <div
                                key={similar.id}
                                onClick={() => handleSelectOriginal(similar.id)}
                                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                                  duplicateOf === similar.id
                                    ? 'border-[#3B82F6] bg-[#3B82F6]/10'
                                    : 'border-[#334155] bg-[#0F172A] hover:border-[#3B82F6]/50'
                                }`}
                              >
                                <div className="flex items-start justify-between gap-2">
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="text-xs font-mono text-[#3B82F6]">
                                        {similar.report_number}
                                      </span>
                                      <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                        statusColors[similar.status] || 'bg-[#94A3B8] text-white'
                                      }`}>
                                        {similar.status}
                                      </span>
                                    </div>
                                    <p className="text-sm text-[#F8FAFC] font-medium truncate mb-1">
                                      {similar.title}
                                    </p>
                                    <div className="flex items-center gap-3 text-xs text-[#94A3B8]">
                                      <span className="flex items-center gap-1">
                                        <User className="w-3 h-3" />
                                        {similar.researcher_username || 'Unknown'}
                                      </span>
                                      <span>•</span>
                                      <span>
                                        Submitted {new Date(similar.submitted_at).toLocaleDateString()}
                                      </span>
                                    </div>
                                  </div>
                                  {duplicateOf === similar.id && (
                                    <CheckCircle className="w-5 h-5 text-[#3B82F6] flex-shrink-0" />
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="p-3 bg-[#3B82F6]/10 border border-[#3B82F6]/30 rounded-lg">
                            <p className="text-xs text-[#94A3B8]">
                              <span className="font-semibold text-[#3B82F6]">BR-07:</span> Duplicate reports receive 50% bounty if submitted within 24 hours of the original.
                            </p>
                          </div>
                        </div>
                      )}

                      {similarReports.length === 0 && !loadingSimilar && (
                        <div className="p-3 bg-[#0F172A] border border-[#334155] rounded-lg text-center">
                          <p className="text-sm text-[#94A3B8]">
                            No similar reports found. You can still mark as duplicate if you know the original report ID.
                          </p>
                          <input
                            type="text"
                            value={duplicateOf}
                            onChange={(e) => setDuplicateOf(e.target.value)}
                            placeholder="Enter Original Report ID"
                            className="w-full mt-2 px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-[#94A3B8]">
                      Triage Notes
                    </label>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setShowTemplates(!showTemplates)}
                      className="gap-2"
                    >
                      <FileText className="w-4 h-4" />
                      {showTemplates ? 'Hide Templates' : 'Use Template'}
                    </Button>
                  </div>
                  
                  {showTemplates && templatesData?.templates && (
                    <div className="mb-3 p-3 bg-[#0F172A] border border-[#334155] rounded-lg">
                      <p className="text-xs text-[#94A3B8] mb-2">Select a template:</p>
                      <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
                        {templatesData.templates
                          .filter((t: any) => t.is_active)
                          .map((template: any) => (
                            <button
                              key={template.id}
                              type="button"
                              onClick={() => {
                                setTriageNotes(template.content);
                                setSelectedTemplate(template.id);
                                setShowTemplates(false);
                              }}
                              className={`text-left p-2 rounded border transition-colors ${
                                selectedTemplate === template.id
                                  ? 'border-[#3B82F6] bg-[#3B82F6]/10'
                                  : 'border-[#334155] hover:border-[#3B82F6]/50'
                              }`}
                            >
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-semibold text-[#F8FAFC]">
                                  {template.title}
                                </span>
                                <span className="text-xs px-2 py-0.5 rounded bg-[#3B82F6] text-white">
                                  {template.category.replace('_', ' ')}
                                </span>
                              </div>
                              <p className="text-xs text-[#94A3B8] line-clamp-2">
                                {template.content}
                              </p>
                            </button>
                          ))}
                      </div>
                    </div>
                  )}
                  
                  <Textarea
                    value={triageNotes}
                    onChange={(e) => setTriageNotes(e.target.value)}
                    rows={4}
                    placeholder="Add notes about your triage decision..."
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={handleUpdate}
                    disabled={updateMutation.isLoading}
                    className="gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  
                  {reportData.status === 'new' && (
                    <Button
                      onClick={handleAcknowledge}
                      disabled={acknowledgeMutation.isLoading}
                      variant="outline"
                      className="gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Acknowledge
                    </Button>
                  )}
                  
                  {reportData.status !== 'resolved' && (
                    <Button
                      onClick={handleResolve}
                      disabled={resolveMutation.isLoading}
                      variant="outline"
                      className="gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Mark Resolved
                    </Button>
                  )}
                </div>
              </div>

              {/* Report Info Grid */}
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Bounty</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.bounty_amount ? `${reportData.bounty_amount.toLocaleString()} ETB` : 'TBD'}
                  </p>
                  {!reportData.bounty_amount && (
                    <p className="mt-1 text-xs text-[#94A3B8]">
                      Assign severity to calculate
                    </p>
                  )}
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">CVSS Score</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.cvss_score || '-'}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-2">Triaged At</p>
                  <p className="text-sm text-[#F8FAFC]">
                    {reportData.triaged_at ? (
                      <>
                        <span className="block">{new Date(reportData.triaged_at).toLocaleDateString()}</span>
                        <span className="text-xs text-[#94A3B8]">{new Date(reportData.triaged_at).toLocaleTimeString()}</span>
                      </>
                    ) : (
                      <span className="text-[#94A3B8]">Not yet triaged</span>
                    )}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Duplicate</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.is_duplicate ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Link href="/triage/queue">
                  <Button variant="outline" className="gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Queue
                  </Button>
                </Link>
              </div>
            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
