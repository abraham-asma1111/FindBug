'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import {
  formatCompactNumber,
  formatCurrency,
  formatDateTime,
  getPortalNavItems,
} from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

type ReportListTab =
  | 'all'
  | 'new'
  | 'triaged'
  | 'valid'
  | 'invalid'
  | 'duplicate'
  | 'resolved'
  | 'closed';

type ReportDetailTab = 'overview' | 'activity' | 'comments' | 'evidence';

interface ProgramSummary {
  id: string;
  name: string;
  type?: string | null;
  visibility?: string | null;
  status?: string | null;
  budget?: number | string | null;
  description?: string | null;
}

interface ParticipationItem {
  program: ProgramSummary;
  joined_at?: string | null;
}

interface ResearcherReport {
  id: string;
  report_number?: string | null;
  program_id: string;
  title: string;
  description?: string | null;
  steps_to_reproduce?: string | null;
  impact_assessment?: string | null;
  suggested_severity?: string | null;
  affected_asset?: string | null;
  vulnerability_type?: string | null;
  status: string;
  assigned_severity?: string | null;
  cvss_score?: number | string | null;
  triage_notes?: string | null;
  is_duplicate?: boolean;
  duplicate_of?: string | null;
  bounty_amount?: number | string | null;
  bounty_status?: string | null;
  submitted_at?: string | null;
  updated_at?: string | null;
  last_activity_at?: string | null;
  acknowledged_at?: string | null;
  triaged_at?: string | null;
  resolved_at?: string | null;
  closed_at?: string | null;
}

interface ReportStatisticsResponse {
  total_reports: number;
  status_breakdown: Record<string, number>;
  severity_breakdown: Record<string, number>;
  bounties: {
    total_earned: number;
    pending: number;
    paid: number;
  };
  success_rate: number;
}

interface TimelinePoint {
  date: string;
  count: number;
  status_breakdown: Record<string, number>;
}

interface ReportTimelineResponse {
  timeline: TimelinePoint[];
  period_days: number;
  total_reports: number;
}

interface ReportComment {
  id: string;
  comment_text: string;
  comment_type?: string | null;
  is_internal?: boolean;
  author_role?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  edited?: boolean;
}

interface ReportAttachment {
  id: string;
  filename: string;
  original_filename?: string | null;
  file_type?: string | null;
  file_size?: number | null;
  is_safe?: boolean | null;
  uploaded_at?: string | null;
}

interface TrackingTimelineItem {
  event: string;
  timestamp?: string | null;
  description: string;
}

interface StatusHistoryItem {
  from_status?: string | null;
  to_status: string;
  changed_at?: string | null;
  change_reason?: string | null;
}

interface ReportTrackingResponse {
  report_id: string;
  report_number?: string | null;
  current_status: string;
  submitted_at?: string | null;
  last_activity_at?: string | null;
  timeline: TrackingTimelineItem[];
  status_history: StatusHistoryItem[];
  bounty_status?: string | null;
  bounty_amount?: number | null;
  is_duplicate?: boolean;
  duplicate_of?: string | null;
}

interface ActivityItem {
  type: 'event' | 'comment';
  event_type?: string | null;
  timestamp?: string | null;
  description?: string | null;
  author_role?: string | null;
  comment_text?: string | null;
  is_internal?: boolean;
}

interface ReportActivityResponse {
  report_id: string;
  report_number?: string | null;
  activity: ActivityItem[];
  total_events: number;
}

interface CreateReportDraft {
  programId: string;
  title: string;
  suggestedSeverity: string;
  vulnerabilityType: string;
  affectedAsset: string;
  description: string;
  stepsToReproduce: string;
  impactAssessment: string;
}

const reportListTabs: ReportListTab[] = [
  'all',
  'new',
  'triaged',
  'valid',
  'invalid',
  'duplicate',
  'resolved',
  'closed',
];

const detailTabs: Array<{ id: ReportDetailTab; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'activity', label: 'Activity' },
  { id: 'comments', label: 'Comments' },
  { id: 'evidence', label: 'Evidence' },
];

const statusTone: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  triaged: 'bg-[#faf1e1] text-[#9a6412]',
  valid: 'bg-[#eef7ef] text-[#24613a]',
  invalid: 'bg-[#fff2f1] text-[#b42318]',
  duplicate: 'bg-[#f6eefb] text-[#6f3da5]',
  resolved: 'bg-[#f2eee9] text-[#5f5851]',
  closed: 'bg-[#f2eee9] text-[#5f5851]',
  paid: 'bg-[#eef7ef] text-[#24613a]',
  pending: 'bg-[#faf1e1] text-[#9a6412]',
  approved: 'bg-[#eef7ef] text-[#24613a]',
  rejected: 'bg-[#fff2f1] text-[#b42318]',
};

const severityTone: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-white',
  low: 'bg-[#2d78a8] text-white',
};

const initialDraft: CreateReportDraft = {
  programId: '',
  title: '',
  suggestedSeverity: 'medium',
  vulnerabilityType: '',
  affectedAsset: '',
  description: '',
  stepsToReproduce: '',
  impactAssessment: '',
};

function formatStatusLabel(value?: string | null): string {
  if (!value) {
    return 'Unknown';
  }

  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatProgramLabel(program?: ProgramSummary | null): string {
  if (!program) {
    return 'No active program selected';
  }

  return `${program.name} · ${formatStatusLabel(program.visibility || 'private')}`;
}

function formatShortId(id?: string | null): string {
  if (!id) {
    return '-';
  }

  return id.slice(0, 8).toUpperCase();
}

function getToneClass(value?: string | null, tones?: Record<string, string>): string {
  if (!value || !tones) {
    return 'bg-[#f3ede6] text-[#5f5851]';
  }

  return tones[value.toLowerCase()] || 'bg-[#f3ede6] text-[#5f5851]';
}

function normalizeAmount(value?: number | string | null): number {
  if (value === null || value === undefined || value === '') {
    return 0;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatPercentage(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '0%';
  }

  return `${Math.round(value)}%`;
}

function formatFileSize(size?: number | null): string {
  if (!size) {
    return '0 B';
  }

  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function getProgramName(programId: string, programs: Map<string, ProgramSummary>): string {
  return programs.get(programId)?.name || `Program ${formatShortId(programId)}`;
}

function getReportNextStep(status?: string | null): string {
  switch (status?.toLowerCase()) {
    case 'new':
      return 'Complete evidence and wait for first triage review.';
    case 'triaged':
      return 'Read triage feedback and answer open questions.';
    case 'valid':
      return 'Track remediation and bounty approval from detail.';
    case 'invalid':
      return 'Review the decision and capture the reasoning.';
    case 'duplicate':
      return 'Inspect the linked report reference and outcome.';
    case 'resolved':
      return 'Watch the remediation handoff and retest path.';
    case 'closed':
      return 'Keep the record for history, reputation, and payouts.';
    default:
      return 'Open the record and inspect its current workflow state.';
  }
}

export default function ResearcherReportsWorkspace() {
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const [reports, setReports] = useState<ResearcherReport[]>([]);
  const [statistics, setStatistics] = useState<ReportStatisticsResponse | null>(null);
  const [timeline, setTimeline] = useState<ReportTimelineResponse | null>(null);
  const [participations, setParticipations] = useState<ParticipationItem[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<ResearcherReport | null>(null);
  const [comments, setComments] = useState<ReportComment[]>([]);
  const [attachments, setAttachments] = useState<ReportAttachment[]>([]);
  const [tracking, setTracking] = useState<ReportTrackingResponse | null>(null);
  const [activity, setActivity] = useState<ReportActivityResponse | null>(null);
  const [workspaceError, setWorkspaceError] = useState('');
  const [detailError, setDetailError] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [commentError, setCommentError] = useState('');
  const [attachmentError, setAttachmentError] = useState('');
  const [isLoadingWorkspace, setIsLoadingWorkspace] = useState(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [isUploadingAttachment, setIsUploadingAttachment] = useState(false);
  const [deletingAttachmentId, setDeletingAttachmentId] = useState('');
  const [activeListTab, setActiveListTab] = useState<ReportListTab>('all');
  const [activeDetailTab, setActiveDetailTab] = useState<ReportDetailTab>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [commentDraft, setCommentDraft] = useState('');
  const [attachmentFile, setAttachmentFile] = useState<File | null>(null);
  const [attachmentInputKey, setAttachmentInputKey] = useState(0);
  const [draft, setDraft] = useState<CreateReportDraft>(initialDraft);
  const requestedProgramId = searchParams.get('programId') || '';
  const requestedContextLabel = searchParams.get('contextLabel') || '';

  const programLookup = new Map(
    participations
      .filter((entry) => entry.program?.id)
      .map((entry) => [entry.program.id, entry.program])
  );

  const selectedProgram = draft.programId ? programLookup.get(draft.programId) || null : null;

  useEffect(() => {
    if (!requestedProgramId || !participations.length) {
      return;
    }

    const hasRequestedProgram = participations.some((entry) => entry.program.id === requestedProgramId);

    if (!hasRequestedProgram) {
      return;
    }

    setDraft((currentDraft) => {
      if (currentDraft.programId === requestedProgramId) {
        return currentDraft;
      }

      return {
        ...currentDraft,
        programId: requestedProgramId,
      };
    });
  }, [participations, requestedProgramId]);

  useEffect(() => {
    let cancelled = false;

    const loadWorkspace = async () => {
      try {
        setIsLoadingWorkspace(true);

        const [reportsResponse, statisticsResponse, timelineResponse, participationsResponse] =
          await Promise.all([
            api.get('/reports/my-reports', { params: { limit: 100, offset: 0 } }),
            api.get('/researcher/reports/statistics'),
            api.get('/researcher/reports/timeline', { params: { days: 30 } }),
            api.get('/programs/programs/my-participations'),
          ]);

        if (cancelled) {
          return;
        }

        const nextReports = reportsResponse.data?.reports || [];
        const nextParticipations = participationsResponse.data || [];

        setReports(nextReports);
        setStatistics(statisticsResponse.data || null);
        setTimeline(timelineResponse.data || null);
        setParticipations(nextParticipations);
        setWorkspaceError('');

        setDraft((currentDraft) => {
          if (currentDraft.programId || !nextParticipations.length) {
            return currentDraft;
          }

          return {
            ...currentDraft,
            programId: nextParticipations[0].program?.id || '',
          };
        });

        setSelectedReportId((currentId) => {
          if (currentId && nextReports.some((report: ResearcherReport) => report.id === currentId)) {
            return currentId;
          }

          return nextReports[0]?.id || '';
        });
      } catch (err: any) {
        if (!cancelled) {
          setWorkspaceError(err.response?.data?.detail || 'Failed to load the researcher reports workspace.');
        }
      } finally {
        if (!cancelled) {
          setIsLoadingWorkspace(false);
        }
      }
    };

    loadWorkspace();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedReportId) {
      setSelectedReport(null);
      setComments([]);
      setAttachments([]);
      setTracking(null);
      setActivity(null);
      return;
    }

    let cancelled = false;

    const loadDetail = async () => {
      try {
        setIsLoadingDetail(true);
        const [detailResponse, commentsResponse, attachmentsResponse, trackingResponse, activityResponse] =
          await Promise.all([
            api.get(`/reports/${selectedReportId}`),
            api.get(`/reports/${selectedReportId}/comments`),
            api.get(`/reports/${selectedReportId}/attachments`),
            api.get(`/reports/${selectedReportId}/tracking`),
            api.get(`/reports/${selectedReportId}/activity`),
          ]);

        if (cancelled) {
          return;
        }

        setSelectedReport(detailResponse.data || null);
        setComments(commentsResponse.data?.comments || []);
        setAttachments(attachmentsResponse.data?.attachments || []);
        setTracking(trackingResponse.data || null);
        setActivity(activityResponse.data || null);
        setDetailError('');
      } catch (err: any) {
        if (!cancelled) {
          setDetailError(err.response?.data?.detail || 'Failed to load report details.');
        }
      } finally {
        if (!cancelled) {
          setIsLoadingDetail(false);
        }
      }
    };

    loadDetail();

    return () => {
      cancelled = true;
    };
  }, [selectedReportId]);

  const filteredReports = reports.filter((report) => {
    const matchesStatus = activeListTab === 'all' || report.status?.toLowerCase() === activeListTab;
    const normalizedQuery = searchQuery.trim().toLowerCase();

    if (!matchesStatus) {
      return false;
    }

    if (!normalizedQuery) {
      return true;
    }

    return (
      report.title.toLowerCase().includes(normalizedQuery) ||
      (report.report_number || '').toLowerCase().includes(normalizedQuery) ||
      getProgramName(report.program_id, programLookup).toLowerCase().includes(normalizedQuery)
    );
  });

  const recentTimeline = (timeline?.timeline || []).slice(-8);
  const maxTimelineValue = recentTimeline.reduce((highest, item) => Math.max(highest, item.count), 1);

  const openReportDetail = (reportId: string, nextTab: ReportDetailTab = 'overview') => {
    setSelectedReportId(reportId);
    setActiveDetailTab(nextTab);
  };

  const handleDraftChange = (field: keyof CreateReportDraft, value: string) => {
    setDraft((currentDraft) => ({
      ...currentDraft,
      [field]: value,
    }));
  };

  const reloadWorkspace = async (preferredReportId?: string) => {
    const [reportsResponse, statisticsResponse, timelineResponse, participationsResponse] = await Promise.all([
      api.get('/reports/my-reports', { params: { limit: 100, offset: 0 } }),
      api.get('/researcher/reports/statistics'),
      api.get('/researcher/reports/timeline', { params: { days: 30 } }),
      api.get('/programs/programs/my-participations'),
    ]);

    const nextReports = reportsResponse.data?.reports || [];
    const nextParticipations = participationsResponse.data || [];

    setReports(nextReports);
    setStatistics(statisticsResponse.data || null);
    setTimeline(timelineResponse.data || null);
    setParticipations(nextParticipations);

    setSelectedReportId((currentId) => {
      if (preferredReportId && nextReports.some((report: ResearcherReport) => report.id === preferredReportId)) {
        return preferredReportId;
      }

      if (currentId && nextReports.some((report: ResearcherReport) => report.id === currentId)) {
        return currentId;
      }

      return nextReports[0]?.id || '';
    });
  };

  const handleSubmitReport = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      setIsSubmittingReport(true);
      setSubmitError('');
      setSubmitSuccess('');

      const response = await api.post('/reports', {
        program_id: draft.programId,
        title: draft.title,
        description: draft.description,
        steps_to_reproduce: draft.stepsToReproduce,
        impact_assessment: draft.impactAssessment,
        suggested_severity: draft.suggestedSeverity,
        affected_asset: draft.affectedAsset || undefined,
        vulnerability_type: draft.vulnerabilityType || undefined,
      });

      const nextProgramId = draft.programId;
      const createdReportId = response.data?.report_id || '';

      setDraft({
        ...initialDraft,
        programId: nextProgramId,
      });
      setSubmitSuccess(response.data?.message || 'Report submitted successfully.');
      setActiveDetailTab('overview');
      await reloadWorkspace(createdReportId);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to submit report.');
    } finally {
      setIsSubmittingReport(false);
    }
  };

  const handleSubmitComment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedReportId) {
      return;
    }

    try {
      setIsSubmittingComment(true);
      setCommentError('');

      await api.post(`/reports/${selectedReportId}/comments`, {
        comment_text: commentDraft,
        comment_type: 'comment',
        is_internal: false,
      });

      setCommentDraft('');
      await reloadWorkspace(selectedReportId);
    } catch (err: any) {
      setCommentError(err.response?.data?.detail || 'Failed to add comment.');
    } finally {
      setIsSubmittingComment(false);
    }
  };

  const handleUploadAttachment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedReportId || !attachmentFile) {
      return;
    }

    try {
      setIsUploadingAttachment(true);
      setAttachmentError('');

      const formData = new FormData();
      formData.append('file', attachmentFile);

      await api.post(`/reports/${selectedReportId}/attachments`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAttachmentFile(null);
      setAttachmentInputKey((current) => current + 1);
      await reloadWorkspace(selectedReportId);
    } catch (err: any) {
      setAttachmentError(err.response?.data?.detail || 'Failed to upload attachment.');
    } finally {
      setIsUploadingAttachment(false);
    }
  };

  const handleDeleteAttachment = async (attachmentId: string) => {
    if (!window.confirm('Delete this attachment from the report evidence set?')) {
      return;
    }

    try {
      setDeletingAttachmentId(attachmentId);
      setAttachmentError('');

      await api.post(`/attachments/${attachmentId}/delete`);
      await reloadWorkspace(selectedReportId);
    } catch (err: any) {
      setAttachmentError(err.response?.data?.detail || 'Failed to delete attachment.');
    } finally {
      setDeletingAttachmentId('');
    }
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Reports"
          subtitle="Submit findings, track triage progress, keep evidence organized, and keep the conversation attached to the report lifecycle."
          navItems={getPortalNavItems(user.role)}
        >
          {workspaceError ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {workspaceError}
            </div>
          ) : null}

          {submitSuccess ? (
            <div className="mb-6 rounded-2xl border border-[#b8dbbf] bg-[#eef7ef] p-4 text-sm text-[#24613a]">
              {submitSuccess}
            </div>
          ) : null}

          {requestedContextLabel ? (
            <div className="mb-6 rounded-2xl border border-[#d7c6b2] bg-[#fcf7f1] p-4 text-sm text-[#5f5851]">
              Reporting context: <span className="font-semibold text-[#2d2a26]">{requestedContextLabel}</span>
              {requestedProgramId ? ' is preselected below when it exists in your active participations.' : null}
            </div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total Reports"
              value={isLoadingWorkspace ? '...' : formatCompactNumber(statistics?.total_reports)}
              helper={`${statistics?.status_breakdown?.new || 0} currently new`}
            />
            <StatCard
              label="Accepted Rate"
              value={isLoadingWorkspace ? '...' : formatPercentage(statistics?.success_rate)}
              helper={`${statistics?.status_breakdown?.valid || 0} valid findings`}
            />
            <StatCard
              label="Total Earned"
              value={isLoadingWorkspace ? '...' : formatCurrency(statistics?.bounties?.total_earned)}
              helper={`Paid ${formatCurrency(statistics?.bounties?.paid)}`}
            />
            <StatCard
              label="Pending Reward"
              value={isLoadingWorkspace ? '...' : formatCurrency(statistics?.bounties?.pending)}
              helper={`${statistics?.status_breakdown?.triaged || 0} reports under review`}
            />
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
            <div className="space-y-6">
              <SectionCard
                title="Start a New Report"
                description="Create a submission from one of your active program participations."
              >
                {participations.length ? (
                  <form className="space-y-4" onSubmit={handleSubmitReport}>
                    <div>
                      <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Program</label>
                      <select
                        value={draft.programId}
                        onChange={(event) => handleDraftChange('programId', event.target.value)}
                        className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        required
                      >
                        <option value="">Select an active program</option>
                        {participations.map((entry) => (
                          <option key={entry.program.id} value={entry.program.id}>
                            {formatProgramLabel(entry.program)}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="sm:col-span-2">
                        <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Title</label>
                        <input
                          value={draft.title}
                          onChange={(event) => handleDraftChange('title', event.target.value)}
                          placeholder="Summarize the vulnerability clearly"
                          className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                          required
                          minLength={10}
                        />
                      </div>

                      <div>
                        <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Suggested Severity</label>
                        <select
                          value={draft.suggestedSeverity}
                          onChange={(event) => handleDraftChange('suggestedSeverity', event.target.value)}
                          className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        >
                          <option value="critical">Critical</option>
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </div>

                      <div>
                        <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Vulnerability Type</label>
                        <input
                          value={draft.vulnerabilityType}
                          onChange={(event) => handleDraftChange('vulnerabilityType', event.target.value)}
                          placeholder="XSS, SSRF, auth bypass"
                          className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        />
                      </div>

                      <div className="sm:col-span-2">
                        <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Affected Asset</label>
                        <input
                          value={draft.affectedAsset}
                          onChange={(event) => handleDraftChange('affectedAsset', event.target.value)}
                          placeholder="api.example.com or mobile-auth service"
                          className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Description</label>
                      <textarea
                        value={draft.description}
                        onChange={(event) => handleDraftChange('description', event.target.value)}
                        rows={5}
                        placeholder="Describe the issue, affected area, and attacker path."
                        className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        required
                        minLength={50}
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Steps to Reproduce</label>
                      <textarea
                        value={draft.stepsToReproduce}
                        onChange={(event) => handleDraftChange('stepsToReproduce', event.target.value)}
                        rows={4}
                        placeholder="List each step so triage can recreate the issue."
                        className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        required
                        minLength={20}
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Impact Assessment</label>
                      <textarea
                        value={draft.impactAssessment}
                        onChange={(event) => handleDraftChange('impactAssessment', event.target.value)}
                        rows={4}
                        placeholder="Explain business impact, exploitation value, and affected trust boundary."
                        className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                        required
                        minLength={20}
                      />
                    </div>

                    {selectedProgram ? (
                      <div className="rounded-2xl border border-[#e6ddd4] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
                        <p className="font-semibold text-[#2d2a26]">{selectedProgram.name}</p>
                        <p className="mt-1">
                          {selectedProgram.description || 'Program details will continue to expand in the engagements module.'}
                        </p>
                        <div className="mt-3 flex flex-wrap gap-2">
                          <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                            {formatStatusLabel(selectedProgram.type || 'bounty')}
                          </span>
                          <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                            Budget {formatCurrency(normalizeAmount(selectedProgram.budget))}
                          </span>
                        </div>
                      </div>
                    ) : null}

                    {submitError ? (
                      <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                        {submitError}
                      </div>
                    ) : null}

                    <button
                      type="submit"
                      disabled={isSubmittingReport}
                      className="w-full rounded-full bg-[#ef2330] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:bg-[#f4a0a5]"
                    >
                      {isSubmittingReport ? 'Submitting report...' : 'Submit report'}
                    </button>
                  </form>
                ) : (
                  <div className="rounded-2xl border border-[#e6ddd4] bg-[#fcfaf7] p-4 text-sm leading-6 text-[#6d6760]">
                    Join at least one active program from the engagements workspace before creating a report.
                  </div>
                )}
              </SectionCard>

              <SectionCard
                title="30-Day Submission Cadence"
                description="Recent submission volume from the researcher timeline endpoint."
              >
                <div className="space-y-3">
                  {recentTimeline.length ? (
                    recentTimeline.map((entry) => (
                      <div key={entry.date} className="grid grid-cols-[70px_minmax(0,1fr)_36px] items-center gap-3">
                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          {new Date(`${entry.date}T00:00:00`).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                        <div className="h-3 overflow-hidden rounded-full bg-[#f3ede6]">
                          <div
                            className="h-full rounded-full bg-[#ef2330]"
                            style={{ width: `${Math.max((entry.count / maxTimelineValue) * 100, entry.count ? 12 : 0)}%` }}
                          />
                        </div>
                        <span className="text-right text-sm font-semibold text-[#2d2a26]">{entry.count}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-[#6d6760]">
                      {isLoadingWorkspace ? 'Loading report cadence...' : 'No submission activity recorded in the last 30 days.'}
                    </p>
                  )}
                </div>
              </SectionCard>
            </div>

            <SectionCard
              title="Report Workspace"
              description="Filter your submitted findings, inspect detail, and keep evidence and comments attached to the same workflow."
            >
              <div className="mb-5 flex flex-col gap-4 border-b border-[#e6ddd4] pb-5">
                <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-center">
                  <input
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    placeholder="Search by report title, number, or program"
                    className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                  />
                  <div className="flex flex-wrap items-center gap-3 text-sm text-[#6d6760]">
                    <span className="rounded-full bg-[#f3ede6] px-4 py-2 font-semibold text-[#5f5851]">
                      Showing {filteredReports.length} of {statistics?.total_reports || reports.length}
                    </span>
                    {(searchQuery || activeListTab !== 'all') ? (
                      <button
                        type="button"
                        onClick={() => {
                          setSearchQuery('');
                          setActiveListTab('all');
                        }}
                        className="rounded-full border border-[#d8d0c8] px-4 py-2 font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                      >
                        Clear filters
                      </button>
                    ) : null}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {reportListTabs.map((tab) => {
                    const isActive = tab === activeListTab;
                    const count =
                      tab === 'all'
                        ? statistics?.total_reports || reports.length
                        : statistics?.status_breakdown?.[tab] || 0;

                    return (
                      <button
                        key={tab}
                        type="button"
                        onClick={() => setActiveListTab(tab)}
                        className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                          isActive
                            ? 'bg-[#ef2330] text-white'
                            : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                        }`}
                      >
                        <span>{formatStatusLabel(tab)}</span>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs ${
                            isActive ? 'bg-[#f9c6c2] text-[#8e1b22]' : 'bg-white text-[#6d6760]'
                          }`}
                        >
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-6">
                <div className="overflow-x-auto rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7]">
                  <table className="w-full min-w-[1040px] text-left text-sm">
                    <thead className="bg-[#f7f1ea]">
                      <tr className="border-b border-[#e6ddd4]">
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">REPORT</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">PROGRAM</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">SEVERITY</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">STATUS</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">BOUNTY</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">LAST ACTIVITY</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">NEXT STEP</th>
                        <th className="px-4 py-4 font-semibold text-[#2d2a26]">ACTIONS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {isLoadingWorkspace ? (
                        Array.from({ length: 5 }).map((_, index) => (
                          <tr key={`report-loading-${index}`} className="border-b border-[#e6ddd4] last:border-0">
                            <td colSpan={8} className="px-4 py-4">
                              <div className="h-10 animate-pulse rounded-2xl bg-[#efe7de]" />
                            </td>
                          </tr>
                        ))
                      ) : filteredReports.length ? (
                        filteredReports.map((report) => {
                          const isActive = report.id === selectedReportId;

                          return (
                            <tr
                              key={report.id}
                              className={`border-b border-[#e6ddd4] last:border-0 ${
                                isActive ? 'bg-[#fff7f6]' : 'bg-white'
                              }`}
                            >
                              <td className="px-4 py-4">
                                <button
                                  type="button"
                                  onClick={() => openReportDetail(report.id)}
                                  className="text-left"
                                >
                                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                    {report.report_number || formatShortId(report.id)}
                                  </p>
                                  <p className="mt-2 font-semibold text-[#2d2a26]">{report.title}</p>
                                  <p className="mt-1 text-xs text-[#6d6760]">
                                    {formatDateTime(report.submitted_at)}
                                  </p>
                                </button>
                              </td>
                              <td className="px-4 py-4 text-[#6d6760]">
                                {getProgramName(report.program_id, programLookup)}
                              </td>
                              <td className="px-4 py-4">
                                <span
                                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                    report.assigned_severity || report.suggested_severity
                                      ? getToneClass(report.assigned_severity || report.suggested_severity, severityTone)
                                      : 'bg-[#f3ede6] text-[#5f5851]'
                                  }`}
                                >
                                  {formatStatusLabel(report.assigned_severity || report.suggested_severity || 'unassigned')}
                                </span>
                              </td>
                              <td className="px-4 py-4">
                                <span
                                  className={`rounded-full px-3 py-1 text-xs font-semibold ${getToneClass(report.status, statusTone)}`}
                                >
                                  {formatStatusLabel(report.status)}
                                </span>
                              </td>
                              <td className="px-4 py-4 font-semibold text-[#2d2a26]">
                                {report.bounty_amount != null
                                  ? formatCurrency(normalizeAmount(report.bounty_amount))
                                  : 'No bounty yet'}
                              </td>
                              <td className="px-4 py-4 text-[#6d6760]">
                                {formatDateTime(report.last_activity_at || report.updated_at || report.submitted_at)}
                              </td>
                              <td className="px-4 py-4 text-[#6d6760]">{getReportNextStep(report.status)}</td>
                              <td className="px-4 py-4">
                                <div className="flex flex-wrap gap-2">
                                  <button
                                    type="button"
                                    onClick={() => openReportDetail(report.id, 'overview')}
                                    className="rounded-full border border-[#d8d0c8] px-3 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                                  >
                                    Open
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => openReportDetail(report.id, 'comments')}
                                    className="rounded-full border border-[#d8d0c8] px-3 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                                  >
                                    Comment
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => openReportDetail(report.id, 'evidence')}
                                    className="rounded-full border border-[#d8d0c8] px-3 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                                  >
                                    Evidence
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })
                      ) : (
                        <tr>
                          <td colSpan={8} className="px-4 py-10 text-center">
                            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                              No reports match the current filters
                            </p>
                            <p className="mt-2 text-sm text-[#6d6760]">
                              Adjust the status filter or search query to reopen the queue.
                            </p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="min-w-0">
                  {detailError ? (
                    <div className="mb-4 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                      {detailError}
                    </div>
                  ) : null}

                  {selectedReport ? (
                    <div className="space-y-5">
                      <div className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${getToneClass(selectedReport.status, statusTone)}`}
                          >
                            {formatStatusLabel(selectedReport.status)}
                          </span>
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${
                              selectedReport.assigned_severity || selectedReport.suggested_severity
                                ? getToneClass(
                                    selectedReport.assigned_severity || selectedReport.suggested_severity,
                                    severityTone
                                  )
                                : 'bg-[#f3ede6] text-[#5f5851]'
                            }`}
                          >
                            {formatStatusLabel(
                              selectedReport.assigned_severity || selectedReport.suggested_severity || 'unassigned'
                            )}
                          </span>
                          {selectedReport.bounty_status ? (
                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${getToneClass(
                                selectedReport.bounty_status,
                                statusTone
                              )}`}
                            >
                              Bounty {formatStatusLabel(selectedReport.bounty_status)}
                            </span>
                          ) : null}
                        </div>

                        <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          {selectedReport.report_number || formatShortId(selectedReport.id)}
                        </p>
                        <h2 className="mt-2 text-2xl font-semibold text-[#2d2a26]">{selectedReport.title}</h2>
                        <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                          {getProgramName(selectedReport.program_id, programLookup)}
                        </p>

                        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                          <div className="rounded-2xl bg-white p-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Submitted</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {formatDateTime(selectedReport.submitted_at)}
                            </p>
                          </div>
                          <div className="rounded-2xl bg-white p-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Last Activity</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {formatDateTime(selectedReport.last_activity_at)}
                            </p>
                          </div>
                          <div className="rounded-2xl bg-white p-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">CVSS</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {selectedReport.cvss_score ?? '-'}
                            </p>
                          </div>
                          <div className="rounded-2xl bg-white p-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Bounty</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {selectedReport.bounty_amount != null
                                ? formatCurrency(normalizeAmount(selectedReport.bounty_amount))
                                : 'Pending'}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {detailTabs.map((tab) => {
                          const isActive = tab.id === activeDetailTab;
                          return (
                            <button
                              key={tab.id}
                              type="button"
                              onClick={() => setActiveDetailTab(tab.id)}
                              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                                isActive
                                  ? 'bg-[#ef2330] text-white'
                                  : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                              }`}
                            >
                              {tab.label}
                            </button>
                          );
                        })}
                      </div>

                      {isLoadingDetail ? (
                        <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-6 text-sm text-[#6d6760]">
                          Loading report detail...
                        </div>
                      ) : null}

                      {!isLoadingDetail && activeDetailTab === 'overview' ? (
                        <div className="space-y-5">
                          <SectionCard title="Report Narrative" description="The core finding package as submitted by the researcher.">
                            <div className="space-y-5 text-sm leading-7 text-[#4f4943]">
                              <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                  Description
                                </p>
                                <p className="mt-2 whitespace-pre-line">{selectedReport.description || 'No description provided.'}</p>
                              </div>
                              <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                  Steps to Reproduce
                                </p>
                                <p className="mt-2 whitespace-pre-line">
                                  {selectedReport.steps_to_reproduce || 'No reproduction steps recorded.'}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                  Impact Assessment
                                </p>
                                <p className="mt-2 whitespace-pre-line">
                                  {selectedReport.impact_assessment || 'No impact assessment recorded.'}
                                </p>
                              </div>
                            </div>
                          </SectionCard>

                          <div className="grid gap-5 lg:grid-cols-2">
                            <SectionCard title="Metadata" description="Key report fields used by triage and finance.">
                              <dl className="space-y-4 text-sm">
                                <div className="flex items-start justify-between gap-4 border-b border-[#eee6de] pb-3">
                                  <dt className="text-[#6d6760]">Suggested severity</dt>
                                  <dd className="font-semibold text-[#2d2a26]">
                                    {formatStatusLabel(selectedReport.suggested_severity)}
                                  </dd>
                                </div>
                                <div className="flex items-start justify-between gap-4 border-b border-[#eee6de] pb-3">
                                  <dt className="text-[#6d6760]">Assigned severity</dt>
                                  <dd className="font-semibold text-[#2d2a26]">
                                    {formatStatusLabel(selectedReport.assigned_severity)}
                                  </dd>
                                </div>
                                <div className="flex items-start justify-between gap-4 border-b border-[#eee6de] pb-3">
                                  <dt className="text-[#6d6760]">Vulnerability type</dt>
                                  <dd className="font-semibold text-[#2d2a26]">
                                    {selectedReport.vulnerability_type || '-'}
                                  </dd>
                                </div>
                                <div className="flex items-start justify-between gap-4 border-b border-[#eee6de] pb-3">
                                  <dt className="text-[#6d6760]">Affected asset</dt>
                                  <dd className="font-semibold text-[#2d2a26]">
                                    {selectedReport.affected_asset || '-'}
                                  </dd>
                                </div>
                                <div className="flex items-start justify-between gap-4">
                                  <dt className="text-[#6d6760]">Duplicate reference</dt>
                                  <dd className="font-semibold text-[#2d2a26]">
                                    {selectedReport.duplicate_of ? formatShortId(selectedReport.duplicate_of) : '-'}
                                  </dd>
                                </div>
                              </dl>
                            </SectionCard>

                            <SectionCard title="Status Tracking" description="Timeline and status history returned by the tracking endpoint.">
                              <div className="space-y-5">
                                <div className="space-y-3">
                                  {(tracking?.timeline || []).length ? (
                                    tracking?.timeline.map((entry) => (
                                      <div key={`${entry.event}-${entry.timestamp}`} className="rounded-2xl bg-[#fcfaf7] p-4">
                                        <div className="flex items-center justify-between gap-3">
                                          <p className="text-sm font-semibold text-[#2d2a26]">
                                            {formatStatusLabel(entry.event)}
                                          </p>
                                          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                            {formatDateTime(entry.timestamp)}
                                          </p>
                                        </div>
                                        <p className="mt-2 text-sm leading-6 text-[#6d6760]">{entry.description}</p>
                                      </div>
                                    ))
                                  ) : (
                                    <p className="text-sm text-[#6d6760]">No tracking timeline is available yet.</p>
                                  )}
                                </div>

                                <div className="space-y-3 border-t border-[#eee6de] pt-4">
                                  {(tracking?.status_history || []).length ? (
                                    tracking?.status_history.map((entry, index) => (
                                      <div key={`${entry.to_status}-${entry.changed_at}-${index}`} className="rounded-2xl bg-white p-4">
                                        <div className="flex items-center justify-between gap-3">
                                          <p className="text-sm font-semibold text-[#2d2a26]">
                                            {formatStatusLabel(entry.from_status || 'new')} to {formatStatusLabel(entry.to_status)}
                                          </p>
                                          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                            {formatDateTime(entry.changed_at)}
                                          </p>
                                        </div>
                                        <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                                          {entry.change_reason || 'No reason recorded.'}
                                        </p>
                                      </div>
                                    ))
                                  ) : (
                                    <p className="text-sm text-[#6d6760]">Status history will appear here after the first state change.</p>
                                  )}
                                </div>
                              </div>
                            </SectionCard>
                          </div>
                        </div>
                      ) : null}

                      {!isLoadingDetail && activeDetailTab === 'activity' ? (
                        <SectionCard
                          title="Unified Activity Feed"
                          description="Status events and comments are merged here so the report narrative stays chronological."
                        >
                          <div className="space-y-4">
                            {(activity?.activity || []).length ? (
                              activity?.activity.map((entry, index) => (
                                <article key={`${entry.type}-${entry.timestamp}-${index}`} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                                  <div className="flex flex-wrap items-center gap-2">
                                    <span
                                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                        entry.type === 'comment'
                                          ? 'bg-[#edf5fb] text-[#2d78a8]'
                                          : 'bg-[#f3ede6] text-[#5f5851]'
                                      }`}
                                    >
                                      {formatStatusLabel(entry.type)}
                                    </span>
                                    {entry.author_role ? (
                                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#6d6760]">
                                        {formatStatusLabel(entry.author_role)}
                                      </span>
                                    ) : null}
                                  </div>
                                  <p className="mt-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                    {formatDateTime(entry.timestamp)}
                                  </p>
                                  <p className="mt-3 whitespace-pre-line text-sm leading-7 text-[#4f4943]">
                                    {entry.type === 'comment' ? entry.comment_text : entry.description}
                                  </p>
                                </article>
                              ))
                            ) : (
                              <p className="text-sm text-[#6d6760]">No activity has been recorded on this report yet.</p>
                            )}
                          </div>
                        </SectionCard>
                      ) : null}

                      {!isLoadingDetail && activeDetailTab === 'comments' ? (
                        <div className="space-y-5">
                          <SectionCard title="Add Comment" description="Keep clarifications attached to the report rather than in external chat.">
                            <form className="space-y-4" onSubmit={handleSubmitComment}>
                              <textarea
                                value={commentDraft}
                                onChange={(event) => setCommentDraft(event.target.value)}
                                rows={4}
                                placeholder="Add the clarification, follow-up, or context you want triage and the organization to see."
                                className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#c8bfb6]"
                                required
                              />

                              {commentError ? (
                                <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                                  {commentError}
                                </div>
                              ) : null}

                              <button
                                type="submit"
                                disabled={isSubmittingComment || !commentDraft.trim()}
                                className="rounded-full bg-[#ef2330] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:bg-[#f4a0a5]"
                              >
                                {isSubmittingComment ? 'Sending comment...' : 'Post comment'}
                              </button>
                            </form>
                          </SectionCard>

                          <SectionCard title="Comment Thread" description="External conversation visible from the report workflow.">
                            <div className="space-y-4">
                              {comments.length ? (
                                comments.map((entry) => (
                                  <article key={entry.id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                                    <div className="flex flex-wrap items-center gap-2">
                                      <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                                        {formatStatusLabel(entry.author_role)}
                                      </span>
                                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#6d6760]">
                                        {formatStatusLabel(entry.comment_type)}
                                      </span>
                                      {entry.edited ? (
                                        <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                                          Edited
                                        </span>
                                      ) : null}
                                    </div>
                                    <p className="mt-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                      {formatDateTime(entry.created_at)}
                                    </p>
                                    <p className="mt-3 whitespace-pre-line text-sm leading-7 text-[#4f4943]">
                                      {entry.comment_text}
                                    </p>
                                  </article>
                                ))
                              ) : (
                                <p className="text-sm text-[#6d6760]">No comments yet. Use this thread for clarifications and follow-ups.</p>
                              )}
                            </div>
                          </SectionCard>
                        </div>
                      ) : null}

                      {!isLoadingDetail && activeDetailTab === 'evidence' ? (
                        <div className="space-y-5">
                          <SectionCard title="Upload Evidence" description="Keep screenshots, videos, and PoC files attached directly to the report.">
                            <form className="space-y-4" onSubmit={handleUploadAttachment}>
                              <input
                                key={attachmentInputKey}
                                type="file"
                                onChange={(event) => setAttachmentFile(event.target.files?.[0] || null)}
                                className="w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26]"
                              />

                              {attachmentError ? (
                                <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                                  {attachmentError}
                                </div>
                              ) : null}

                              <button
                                type="submit"
                                disabled={isUploadingAttachment || !attachmentFile}
                                className="rounded-full bg-[#ef2330] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:bg-[#f4a0a5]"
                              >
                                {isUploadingAttachment ? 'Uploading evidence...' : 'Upload attachment'}
                              </button>
                            </form>
                          </SectionCard>

                          <SectionCard title="Evidence Set" description="Current attachments and scanner status for this report.">
                            <div className="space-y-4">
                              {attachments.length ? (
                                attachments.map((entry) => (
                                  <article key={entry.id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                                      <div>
                                        <p className="text-sm font-semibold text-[#2d2a26]">
                                          {entry.original_filename || entry.filename}
                                        </p>
                                        <p className="mt-1 text-sm text-[#6d6760]">{entry.file_type || 'Attachment'}</p>
                                        <div className="mt-3 flex flex-wrap gap-2">
                                          <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#6d6760]">
                                            {formatFileSize(entry.file_size)}
                                          </span>
                                          <span
                                            className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                              entry.is_safe ? 'bg-[#eef7ef] text-[#24613a]' : 'bg-[#fff2f1] text-[#b42318]'
                                            }`}
                                          >
                                            {entry.is_safe ? 'Scanner clear' : 'Safety check pending'}
                                          </span>
                                        </div>
                                      </div>

                                      <div className="flex items-center gap-3">
                                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                          {formatDateTime(entry.uploaded_at)}
                                        </p>
                                        <button
                                          type="button"
                                          onClick={() => handleDeleteAttachment(entry.id)}
                                          disabled={deletingAttachmentId === entry.id}
                                          className="rounded-full border border-[#e7b3ae] px-4 py-2 text-sm font-semibold text-[#b42318] transition hover:bg-[#fff2f1] disabled:cursor-not-allowed disabled:opacity-60"
                                        >
                                          {deletingAttachmentId === entry.id ? 'Deleting...' : 'Delete'}
                                        </button>
                                      </div>
                                    </div>
                                  </article>
                                ))
                              ) : (
                                <p className="text-sm text-[#6d6760]">No evidence files have been uploaded for this report yet.</p>
                              )}
                            </div>
                          </SectionCard>
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-8 text-sm leading-6 text-[#6d6760]">
                      {isLoadingWorkspace
                        ? 'Loading your report workspace...'
                        : 'Select a report from the list or submit your first finding to start the workflow.'}
                    </div>
                  )}
                </div>
              </div>
            </SectionCard>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
