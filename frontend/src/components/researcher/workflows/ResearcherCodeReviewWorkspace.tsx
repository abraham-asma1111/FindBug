'use client';

import { useEffect, useMemo, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Alert from '@/components/ui/Alert';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import {
  Banner,
  EmptyCollection,
  MetricGrid,
  PillList,
  SectionCard,
  StatusBadge,
  WorkflowPickerCard,
  WorkflowTabs,
  WorkflowTimeline,
  formatStatusLabel,
  formatWorkflowDate,
} from './shared';

interface CodeReviewEngagement {
  id: string;
  title: string;
  repository_url: string;
  review_type: string;
  status: string;
  findings_count: number;
  report_submitted_at?: string | null;
  created_at?: string | null;
}

interface CodeReviewFinding {
  id: string;
  title: string;
  description: string;
  severity: string;
  issue_type: string;
  file_path?: string | null;
  line_number?: number | null;
  status: string;
  created_at?: string | null;
}

interface CodeReviewStats {
  total_findings: number;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  by_issue_type: Record<string, number>;
}

const codeReviewSteps = [
  {
    label: 'Private repository access',
    detail: 'International code review platforms begin with a scoped repository, trust controls, and reviewer access confirmation.',
    state: 'complete' as const,
  },
  {
    label: 'Manual review and hotspot analysis',
    detail: 'Trace authentication, authorization, sensitive logic, and dependency boundaries before writing findings.',
    state: 'active' as const,
  },
  {
    label: 'Precise finding capture',
    detail: 'Every issue should include issue type, file path, line reference, exploitability, and clear remediation guidance.',
    state: 'active' as const,
  },
  {
    label: 'Report handoff and verification',
    detail: 'Once evidence is complete, submit the review package and hand the remediation cycle back to the organization.',
    state: 'upcoming' as const,
  },
];

export default function ResearcherCodeReviewWorkspace() {
  const user = useAuthStore((state) => state.user);
  const [selectedEngagementId, setSelectedEngagementId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'submission'>('overview');
  const [pageError, setPageError] = useState('');
  const [pageSuccess, setPageSuccess] = useState('');
  const [findingForm, setFindingForm] = useState({
    title: '',
    description: '',
    severity: 'high',
    issue_type: 'security_vulnerability',
    file_path: '',
    line_number: '',
  });
  const [isStarting, setIsStarting] = useState(false);
  const [isSubmittingFinding, setIsSubmittingFinding] = useState(false);
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);

  const {
    data: engagementsResponse,
    isLoading: isLoadingEngagements,
    error: engagementsError,
    refetch: refetchEngagements,
  } = useApiQuery<{ engagements: CodeReviewEngagement[]; total: number }>('/code-review/engagements', {
    enabled: !!user,
  });

  const engagements = engagementsResponse?.engagements || [];

  useEffect(() => {
    if (!engagements.length) {
      setSelectedEngagementId('');
      return;
    }

    if (!selectedEngagementId || !engagements.some((entry) => entry.id === selectedEngagementId)) {
      setSelectedEngagementId(engagements[0].id);
    }
  }, [engagements, selectedEngagementId]);

  const selectedEngagement = useMemo(
    () => engagements.find((entry) => entry.id === selectedEngagementId) ?? null,
    [engagements, selectedEngagementId]
  );

  const {
    data: findingsResponse,
    isLoading: isLoadingFindings,
    refetch: refetchFindings,
  } = useApiQuery<{ findings: CodeReviewFinding[]; total: number }>(
    selectedEngagementId ? `/code-review/engagements/${selectedEngagementId}/findings` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const {
    data: stats,
    isLoading: isLoadingStats,
    refetch: refetchStats,
  } = useApiQuery<CodeReviewStats>(
    selectedEngagementId ? `/code-review/engagements/${selectedEngagementId}/stats` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const findings = findingsResponse?.findings || [];

  const metrics = selectedEngagement
    ? [
        {
          label: 'Review type',
          value: formatStatusLabel(selectedEngagement.review_type),
          helper: selectedEngagement.repository_url,
        },
        {
          label: 'Status',
          value: formatStatusLabel(selectedEngagement.status),
          helper: `${selectedEngagement.findings_count} findings recorded`,
        },
        {
          label: 'Critical and high',
          value: `${(stats?.by_severity?.critical || 0) + (stats?.by_severity?.high || 0)}`,
          helper: 'Top-priority code paths needing attention',
        },
        {
          label: 'Submitted',
          value: selectedEngagement.report_submitted_at ? 'Yes' : 'Not yet',
          helper: formatWorkflowDate(selectedEngagement.report_submitted_at, 'Awaiting final report'),
        },
      ]
    : [];

  async function handleStartReview() {
    if (!selectedEngagementId) {
      return;
    }

    try {
      setIsStarting(true);
      setPageError('');
      setPageSuccess('');
      await api.post(`/code-review/engagements/${selectedEngagementId}/start`);
      setPageSuccess('Code review moved into progress. Start logging findings with file-level precision.');
      await Promise.all([refetchEngagements(), refetchStats()]);
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to start the code review.');
    } finally {
      setIsStarting(false);
    }
  }

  async function handleSubmitFinding() {
    if (!selectedEngagementId) {
      return;
    }

    try {
      setIsSubmittingFinding(true);
      setPageError('');
      setPageSuccess('');

      await api.post(`/code-review/engagements/${selectedEngagementId}/findings`, {
        title: findingForm.title,
        description: findingForm.description,
        severity: findingForm.severity,
        issue_type: findingForm.issue_type,
        file_path: findingForm.file_path || null,
        line_number: findingForm.line_number ? Number(findingForm.line_number) : null,
      });

      setFindingForm({
        title: '',
        description: '',
        severity: 'high',
        issue_type: 'security_vulnerability',
        file_path: '',
        line_number: '',
      });
      setPageSuccess('Code review finding logged successfully.');
      await Promise.all([refetchFindings(), refetchStats(), refetchEngagements()]);
      setActiveTab('findings');
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to add the code review finding.');
    } finally {
      setIsSubmittingFinding(false);
    }
  }

  async function handleSubmitReport() {
    if (!selectedEngagementId) {
      return;
    }

    try {
      setIsSubmittingReport(true);
      setPageError('');
      setPageSuccess('');
      await api.post(`/code-review/engagements/${selectedEngagementId}/submit`);
      setPageSuccess('Code review report submitted. The engagement is now ready for remediation follow-up.');
      await Promise.all([refetchEngagements(), refetchStats()]);
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to submit the code review report.');
    } finally {
      setIsSubmittingReport(false);
    }
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Code Review Workflow Desk"
          subtitle="Operate your white-box review assignments with repository context, issue-type tracking, and a clean report handoff."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-sm tracking-[0.25em]"
        >
          <div className="space-y-6">
            <Banner
              title="Expert Code Review"
              subtitle="This page now behaves like a real code-review delivery surface: assigned repositories, file-based findings, workflow state changes, and final report submission."
              badge="White-Box Review Lifecycle"
              icon="CR"
              tone="emerald"
            />

            {pageError ? (
              <Alert variant="error" title="Workflow issue">
                {pageError}
              </Alert>
            ) : null}

            {pageSuccess ? (
              <Alert variant="success" title="Workflow updated">
                {pageSuccess}
              </Alert>
            ) : null}

            {engagementsError ? (
              <Alert variant="warning" title="Code review assignments are unavailable">
                {engagementsError.message}
              </Alert>
            ) : null}

            <SectionCard title="Assigned reviews" description="Pick a repository review assignment to continue the white-box workflow.">
              {isLoadingEngagements ? (
                <p className="text-sm text-[#6d6760]">Loading code review assignments...</p>
              ) : engagements.length ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  {engagements.map((engagement) => (
                    <WorkflowPickerCard
                      key={engagement.id}
                      onClick={() => setSelectedEngagementId(engagement.id)}
                      selected={engagement.id === selectedEngagementId}
                      tone="emerald"
                      title={engagement.title}
                      description={engagement.repository_url}
                      status={engagement.status}
                      metrics={[
                        { label: 'Review type', value: formatStatusLabel(engagement.review_type) },
                        { label: 'Findings', value: String(engagement.findings_count) },
                      ]}
                    />
                  ))}
                </div>
              ) : (
                <EmptyCollection
                  title="No code review assignments yet"
                  description="Once an organization assigns you to a repository review, the live reviewer desk appears here."
                />
              )}
            </SectionCard>

            {selectedEngagement ? (
              <>
                <MetricGrid items={metrics} />

                <WorkflowTabs
                  tone="emerald"
                  active={activeTab}
                  onChange={setActiveTab}
                  items={[
                    { value: 'overview', label: 'Overview' },
                    { value: 'findings', label: 'Findings', badge: findings.length },
                    { value: 'submission', label: 'Submission' },
                  ]}
                />

                {activeTab === 'overview' ? (
                  <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                    <SectionCard
                      title="Review brief"
                      description="Repository context, review category, and the current status of this assignment."
                      action={
                        selectedEngagement.status === 'assigned' ? (
                          <Button variant="primary" isLoading={isStarting} onClick={handleStartReview}>
                            Start review
                          </Button>
                        ) : undefined
                      }
                    >
                      <div className="space-y-5">
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Repository</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26] break-all">
                              {selectedEngagement.repository_url}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Review type</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {formatStatusLabel(selectedEngagement.review_type)}
                            </p>
                          </div>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Findings captured</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">{selectedEngagement.findings_count}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Created</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">
                              {formatWorkflowDate(selectedEngagement.created_at, 'Not available')}
                            </p>
                          </div>
                        </div>
                      </div>
                    </SectionCard>

                    <div className="space-y-6">
                      <SectionCard title="Lifecycle" description="Built around how mature platforms run reviewer-delivery and remediation handoff.">
                        <WorkflowTimeline steps={codeReviewSteps} />
                      </SectionCard>

                      <SectionCard title="Issue distribution" description="Current breakdown from the live repository review data.">
                        {isLoadingStats ? (
                          <p className="text-sm text-[#6d6760]">Loading issue distribution...</p>
                        ) : (
                          <div className="space-y-4">
                            <div>
                              <p className="text-sm font-semibold text-[#2d2a26]">Severity mix</p>
                              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                                {Object.entries(stats?.by_severity || {}).map(([key, value]) => (
                                  <div key={key} className="rounded-[18px] border border-[#dbe3ec] bg-[#f8fbfa] px-4 py-3 text-sm text-[#0f172a]">
                                    {formatStatusLabel(key)}: <span className="font-semibold">{value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-[#2d2a26]">Issue types found</p>
                              <div className="mt-3">
                                <PillList items={Object.entries(stats?.by_issue_type || {}).map(([key, value]) => `${formatStatusLabel(key)}: ${value}`)} />
                              </div>
                            </div>
                          </div>
                        )}
                      </SectionCard>
                    </div>
                  </div>
                ) : null}

                {activeTab === 'findings' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
                    <SectionCard title="Recorded findings" description="Every finding should be precise enough for engineering remediation and later verification.">
                      {isLoadingFindings ? (
                        <p className="text-sm text-[#6d6760]">Loading findings...</p>
                      ) : findings.length ? (
                        <div className="space-y-4">
                          {findings.map((finding) => (
                            <div key={finding.id} className="rounded-[24px] border border-[#dbe3ec] bg-white dark:bg-[#111111] p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
                              <div className="flex flex-wrap items-start justify-between gap-3">
                                <div>
                                  <p className="text-base font-semibold text-[#2d2a26]">{finding.title}</p>
                                  <p className="mt-2 text-sm text-[#6d6760]">{finding.description}</p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  <StatusBadge status={finding.severity} />
                                  <StatusBadge status={finding.status} />
                                </div>
                              </div>
                              <div className="mt-4 grid gap-3 md:grid-cols-2">
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Issue type</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">{formatStatusLabel(finding.issue_type)}</p>
                                </div>
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Location</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">
                                    {finding.file_path ? `${finding.file_path}${finding.line_number ? `:${finding.line_number}` : ''}` : 'Repository-wide concern'}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyCollection
                          title="No code review findings yet"
                          description="Add the first reviewer finding once you have a clear issue type and remediation path."
                        />
                      )}
                    </SectionCard>

                    <SectionCard title="Add finding" description="File and line context are optional, but they materially improve remediation quality.">
                      <div className="space-y-4">
                        <Input label="Finding title" value={findingForm.title} onChange={(event) => setFindingForm((current) => ({ ...current, title: event.target.value }))} />
                        <Textarea label="Description" rows={5} value={findingForm.description} onChange={(event) => setFindingForm((current) => ({ ...current, description: event.target.value }))} />
                        <div className="grid gap-4 md:grid-cols-2">
                          <Select label="Severity" value={findingForm.severity} onChange={(event) => setFindingForm((current) => ({ ...current, severity: event.target.value }))}>
                            {['critical', 'high', 'medium', 'low', 'info'].map((entry) => (
                              <option key={entry} value={entry}>
                                {formatStatusLabel(entry)}
                              </option>
                            ))}
                          </Select>
                          <Select label="Issue type" value={findingForm.issue_type} onChange={(event) => setFindingForm((current) => ({ ...current, issue_type: event.target.value }))}>
                            {['security_vulnerability', 'logic_flaw', 'insecure_dependency', 'race_condition', 'performance_issue', 'code_smell', 'other'].map((entry) => (
                              <option key={entry} value={entry}>
                                {formatStatusLabel(entry)}
                              </option>
                            ))}
                          </Select>
                        </div>
                        <div className="grid gap-4 md:grid-cols-[1fr_160px]">
                          <Input label="File path" value={findingForm.file_path} onChange={(event) => setFindingForm((current) => ({ ...current, file_path: event.target.value }))} />
                          <Input label="Line number" type="number" min={1} value={findingForm.line_number} onChange={(event) => setFindingForm((current) => ({ ...current, line_number: event.target.value }))} />
                        </div>
                        <Button variant="primary" isLoading={isSubmittingFinding} onClick={handleSubmitFinding}>
                          Add reviewer finding
                        </Button>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}

                {activeTab === 'submission' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
                    <SectionCard title="Submission checklist" description="A mature review closes with a coherent final report, not just a loose list of issues.">
                      <WorkflowTimeline
                        steps={[
                          {
                            label: 'Complete high-confidence issue capture',
                            detail: 'Ensure the key vulnerabilities are documented with enough specificity for developers.',
                            state: 'complete',
                          },
                          {
                            label: 'Sanity-check severity and issue type',
                            detail: 'Normalize severity and issue typing so the organization gets a consistent report.',
                            state: 'active',
                          },
                          {
                            label: 'Submit the final review package',
                            detail: 'Once findings are ready, submit the report and move the engagement into remediation mode.',
                            state: 'upcoming',
                          },
                        ]}
                      />
                    </SectionCard>

                    <SectionCard title="Finalize review" description="Use this once the repository walkthrough and issue capture are complete.">
                      <div className="space-y-4">
                        <p className="text-sm leading-6 text-[#6d6760]">
                          The submit action closes the reviewer delivery phase for this engagement and marks the report as ready for organization follow-up.
                        </p>
                        <Button variant="primary" isLoading={isSubmittingReport} onClick={handleSubmitReport}>
                          Submit final report
                        </Button>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}
              </>
            ) : null}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
