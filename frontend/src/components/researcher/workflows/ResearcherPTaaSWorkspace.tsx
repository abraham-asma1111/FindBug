'use client';

import { useEffect, useMemo, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Alert from '@/components/ui/Alert';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useResearcherEngagementsData } from '@/hooks/useResearcherEngagementsData';
import { useApiQuery } from '@/hooks/useApiQuery';
import api from '@/lib/api';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import {
  Banner,
  EmptyCollection,
  InfoList,
  MetricGrid,
  PillList,
  SectionCard,
  StatusBadge,
  StructuredValueBlock,
  WorkflowPickerCard,
  WorkflowTabs,
  WorkflowTimeline,
  formatStatusLabel,
  formatWorkflowDate,
  formatWorkflowMoney,
  toLines,
} from './shared';

interface PTaaSEngagement {
  id: number;
  name: string;
  description?: string | null;
  status: string;
  scope?: Record<string, unknown> | null;
  testing_methodology: string;
  custom_methodology_details?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  duration_days?: number | null;
  compliance_requirements?: string[] | null;
  compliance_notes?: string | null;
  deliverables?: Record<string, unknown> | null;
  base_price?: number | string | null;
  total_price?: number | string | null;
  pricing_model?: string | null;
  team_size?: number | null;
}

interface PTaaSFinding {
  id: number;
  title: string;
  severity: string;
  status: string;
  affected_component?: string | null;
  vulnerability_type?: string | null;
  business_impact?: string | null;
  remediation_priority?: string | null;
  discovered_at?: string | null;
  description?: string | null;
}

interface PTaaSProgressUpdate {
  id: number;
  update_text: string;
  progress_percentage: number;
  created_at?: string | null;
}

interface PTaaSDeliverable {
  id: number;
  deliverable_type: string;
  title: string;
  description?: string | null;
  version?: string | null;
  file_url?: string | null;
  approved?: boolean | null;
  submitted_at?: string | null;
}

const ptaasSteps = [
  {
    label: 'Scoping and access alignment',
    detail: 'Confirm methodology, constraints, environments, and evidence expectations before testing begins.',
    state: 'complete' as const,
  },
  {
    label: 'Methodology-driven execution',
    detail: 'Work through the checklist like an enterprise PTaaS engagement, not an opportunistic bug hunt.',
    state: 'active' as const,
  },
  {
    label: 'Structured findings and progress',
    detail: 'Capture exploit proof, business impact, remediation guidance, and progress updates as the engagement evolves.',
    state: 'active' as const,
  },
  {
    label: 'Deliverable and retest handoff',
    detail: 'Package the report, supporting documentation, and any retest notes into final deliverables.',
    state: 'upcoming' as const,
  },
];

const findingDefaults = {
  title: '',
  description: '',
  severity: 'High',
  affected_component: '',
  proof_of_exploit: '',
  impact_analysis: '',
  remediation: '',
  remediation_steps: '',
  reproduction_steps: '',
  vulnerability_type: '',
  business_impact: 'High',
  remediation_priority: 'High',
  remediation_effort: 'Medium',
  confidentiality: 'High',
  integrity: 'High',
  availability: 'Low',
  attack_vector: 'Network',
  attack_complexity: 'Low',
  privileges_required: 'None',
  user_interaction: 'None',
  exploit_code: '',
  exploit_screenshots: '',
  exploit_video_url: '',
  data_at_risk: '',
  affected_users: '',
  code_fix_example: '',
  references: '',
  cwe_id: '',
  owasp_category: '',
};

export default function ResearcherPTaaSWorkspace() {
  const user = useAuthStore((state) => state.user);
  const { ptaasOpportunities } = useResearcherEngagementsData();
  const [selectedEngagementId, setSelectedEngagementId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'progress' | 'deliverables'>('overview');
  const [pageError, setPageError] = useState('');
  const [pageSuccess, setPageSuccess] = useState('');
  const [findingForm, setFindingForm] = useState(findingDefaults);
  const [progressForm, setProgressForm] = useState({ update_text: '', progress_percentage: 35 });
  const [deliverableForm, setDeliverableForm] = useState({
    deliverable_type: 'report',
    title: '',
    description: '',
    file_url: '',
    version: '1.0',
  });
  const [isSubmittingFinding, setIsSubmittingFinding] = useState(false);
  const [isSubmittingProgress, setIsSubmittingProgress] = useState(false);
  const [isSubmittingDeliverable, setIsSubmittingDeliverable] = useState(false);

  const {
    data: engagements,
    isLoading: isLoadingEngagements,
    error: engagementsError,
    refetch: refetchEngagements,
  } = useApiQuery<PTaaSEngagement[]>('/ptaas/researcher/engagements', {
    enabled: !!user,
  });

  useEffect(() => {
    if (!engagements?.length) {
      setSelectedEngagementId(null);
      return;
    }

    if (!selectedEngagementId || !engagements.some((entry) => entry.id === selectedEngagementId)) {
      setSelectedEngagementId(engagements[0].id);
    }
  }, [engagements, selectedEngagementId]);

  const selectedEngagement = useMemo(
    () => engagements?.find((entry) => entry.id === selectedEngagementId) ?? null,
    [engagements, selectedEngagementId]
  );

  const {
    data: findings,
    isLoading: isLoadingFindings,
    refetch: refetchFindings,
  } = useApiQuery<PTaaSFinding[]>(
    selectedEngagementId ? `/ptaas/engagements/${selectedEngagementId}/findings` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const {
    data: progressUpdates,
    isLoading: isLoadingProgress,
    refetch: refetchProgress,
  } = useApiQuery<PTaaSProgressUpdate[]>(
    selectedEngagementId ? `/ptaas/engagements/${selectedEngagementId}/progress` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const {
    data: deliverables,
    isLoading: isLoadingDeliverables,
    refetch: refetchDeliverables,
  } = useApiQuery<PTaaSDeliverable[]>(
    selectedEngagementId ? `/ptaas/engagements/${selectedEngagementId}/deliverables` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const overviewMetrics = selectedEngagement
    ? [
        {
          label: 'Methodology',
          value: formatStatusLabel(selectedEngagement.testing_methodology),
          helper: selectedEngagement.custom_methodology_details || 'Structured testing path',
        },
        {
          label: 'Status',
          value: formatStatusLabel(selectedEngagement.status),
          helper: `${findings?.length || 0} findings logged`,
        },
        {
          label: 'Timeline',
          value: selectedEngagement.duration_days ? `${selectedEngagement.duration_days} days` : 'Open timeline',
          helper: `${formatWorkflowDate(selectedEngagement.start_date)} to ${formatWorkflowDate(selectedEngagement.end_date)}`,
        },
        {
          label: 'Commercials',
          value: formatWorkflowMoney(selectedEngagement.total_price ?? selectedEngagement.base_price),
          helper: `${formatStatusLabel(selectedEngagement.pricing_model)} engagement`,
        },
      ]
    : [];

  async function handleSubmitFinding() {
    if (!selectedEngagementId) {
      setPageError('Select an engagement before adding a finding.');
      return;
    }

    try {
      setIsSubmittingFinding(true);
      setPageError('');
      setPageSuccess('');

      await api.post('/ptaas/findings', {
        engagement_id: selectedEngagementId,
        title: findingForm.title,
        description: findingForm.description,
        severity: findingForm.severity,
        affected_component: findingForm.affected_component,
        proof_of_exploit: findingForm.proof_of_exploit,
        impact_analysis: findingForm.impact_analysis,
        remediation: findingForm.remediation,
        remediation_steps: toLines(findingForm.remediation_steps),
        reproduction_steps: findingForm.reproduction_steps,
        vulnerability_type: findingForm.vulnerability_type,
        business_impact: findingForm.business_impact,
        remediation_priority: findingForm.remediation_priority,
        remediation_effort: findingForm.remediation_effort,
        technical_impact: {
          confidentiality: findingForm.confidentiality,
          integrity: findingForm.integrity,
          availability: findingForm.availability,
        },
        attack_vector: findingForm.attack_vector,
        attack_complexity: findingForm.attack_complexity,
        privileges_required: findingForm.privileges_required,
        user_interaction: findingForm.user_interaction,
        exploit_code: findingForm.exploit_code || null,
        exploit_screenshots: toLines(findingForm.exploit_screenshots),
        exploit_video_url: findingForm.exploit_video_url || null,
        data_at_risk: findingForm.data_at_risk || null,
        affected_users: findingForm.affected_users || null,
        code_fix_example: findingForm.code_fix_example || null,
        references: toLines(findingForm.references),
        cwe_id: findingForm.cwe_id || null,
        owasp_category: findingForm.owasp_category || null,
      });

      setFindingForm(findingDefaults);
      setPageSuccess('PTaaS finding submitted with structured exploit, impact, and remediation fields.');
      await refetchFindings();
      await refetchEngagements();
      setActiveTab('findings');
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to submit the PTaaS finding.');
    } finally {
      setIsSubmittingFinding(false);
    }
  }

  async function handleSubmitProgress() {
    if (!selectedEngagementId) {
      setPageError('Select an engagement before posting an update.');
      return;
    }

    try {
      setIsSubmittingProgress(true);
      setPageError('');
      setPageSuccess('');

      await api.post('/ptaas/progress', {
        engagement_id: selectedEngagementId,
        update_text: progressForm.update_text,
        progress_percentage: Number(progressForm.progress_percentage),
      });

      setProgressForm({ update_text: '', progress_percentage: progressForm.progress_percentage });
      setPageSuccess('Progress update posted to the PTaaS workbench.');
      await refetchProgress();
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to publish the progress update.');
    } finally {
      setIsSubmittingProgress(false);
    }
  }

  async function handleSubmitDeliverable() {
    if (!selectedEngagementId) {
      setPageError('Select an engagement before submitting a deliverable.');
      return;
    }

    try {
      setIsSubmittingDeliverable(true);
      setPageError('');
      setPageSuccess('');

      await api.post('/ptaas/deliverables', {
        engagement_id: selectedEngagementId,
        deliverable_type: deliverableForm.deliverable_type,
        title: deliverableForm.title,
        description: deliverableForm.description || null,
        file_url: deliverableForm.file_url || null,
        version: deliverableForm.version || '1.0',
      });

      setDeliverableForm({
        deliverable_type: 'report',
        title: '',
        description: '',
        file_url: '',
        version: '1.0',
      });
      setPageSuccess('Deliverable submitted to the PTaaS engagement.');
      await refetchDeliverables();
      setActiveTab('deliverables');
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to submit the deliverable.');
    } finally {
      setIsSubmittingDeliverable(false);
    }
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Workflow Desk"
          subtitle="Run assigned PTaaS engagements like a modern enterprise security platform: structured testing, live progress, and report-ready deliverables."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-sm tracking-[0.25em]"
        >
          <div className="space-y-6">
            <Banner
              title="Penetration Testing As A Service"
              subtitle="This workspace replaces the old static PTaaS explanation with a live engagement desk. It supports methodology-driven execution, structured findings, progress updates, and final deliverables."
              badge="Researcher Delivery Workflow"
              icon="PT"
              tone="blue"
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
              <Alert variant="warning" title="Assigned PTaaS data is unavailable">
                {engagementsError.message}
              </Alert>
            ) : null}

            <SectionCard
              title="Assigned PTaaS Engagements"
              description="Choose an active assessment to open its workflow, evidence trail, and delivery tasks."
            >
              {isLoadingEngagements ? (
                <p className="text-sm text-[#6d6760]">Loading PTaaS engagements...</p>
              ) : engagements?.length ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  {engagements.map((engagement) => (
                    <WorkflowPickerCard
                      key={engagement.id}
                      onClick={() => setSelectedEngagementId(engagement.id)}
                      selected={selectedEngagementId === engagement.id}
                      tone="blue"
                      title={engagement.name}
                      description={engagement.description || 'No engagement description provided yet.'}
                      status={engagement.status}
                      metrics={[
                        {
                          label: 'Methodology',
                          value: formatStatusLabel(engagement.testing_methodology),
                        },
                        {
                          label: 'Timeline',
                          value: engagement.duration_days ? `${engagement.duration_days} days` : 'Open window',
                        },
                      ]}
                    />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  <EmptyCollection
                    title="No assigned PTaaS engagements yet"
                    description="When an organization places you on a PTaaS squad, the live assessment workspace will appear here."
                    hint="Researcher workflow opens after assignment"
                  />
                  {ptaasOpportunities.length ? (
                    <div className="rounded-[24px] border border-[#dbe3ec] bg-[#fbfcfd] p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
                      <p className="text-sm font-semibold text-[#0f172a]">Current PTaaS opportunity radar</p>
                      <div className="mt-4 grid gap-3 md:grid-cols-2">
                        {ptaasOpportunities.map((opportunity) => (
                          <WorkflowPickerCard
                            key={opportunity.id}
                            tone="blue"
                            title={opportunity.name}
                            description={opportunity.description || opportunity.reason || 'Matching engine surfaced this PTaaS opportunity.'}
                            status={opportunity.status || opportunity.source}
                          />
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
            </SectionCard>

            {selectedEngagement ? (
              <>
                <MetricGrid items={overviewMetrics} />

                <WorkflowTabs
                  tone="blue"
                  active={activeTab}
                  onChange={setActiveTab}
                  items={[
                    { value: 'overview', label: 'Overview' },
                    { value: 'findings', label: 'Findings', badge: findings?.length || 0 },
                    { value: 'progress', label: 'Progress', badge: progressUpdates?.length || 0 },
                    { value: 'deliverables', label: 'Deliverables', badge: deliverables?.length || 0 },
                  ]}
                />

                {activeTab === 'overview' ? (
                  <div className="grid gap-6 xl:grid-cols-[1.25fr_0.85fr]">
                    <SectionCard
                      title="Assessment Brief"
                      description="Scope, compliance expectations, and delivery framing for the selected PTaaS engagement."
                    >
                      <div className="space-y-5">
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Scope definition</p>
                          <div className="mt-2">
                            <StructuredValueBlock value={selectedEngagement.scope} />
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Deliverables expected</p>
                          <div className="mt-2">
                            <StructuredValueBlock value={selectedEngagement.deliverables} />
                          </div>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-sm font-semibold text-[#2d2a26]">Compliance requirements</p>
                            <div className="mt-2">
                              <PillList items={selectedEngagement.compliance_requirements || []} />
                            </div>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-[#2d2a26]">Compliance notes</p>
                            <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                              {selectedEngagement.compliance_notes || 'No extra compliance notes were attached.'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </SectionCard>

                    <div className="space-y-6">
                      <SectionCard
                        title="Delivery Lifecycle"
                        description="Modeled after mature PTaaS platforms: methodology first, evidence throughout, report-ready finish."
                      >
                        <WorkflowTimeline steps={ptaasSteps} />
                      </SectionCard>

                      <SectionCard title="Engagement snapshot" description="Operational context for the current testing window.">
                        <InfoList
                          items={[
                            { label: 'Window opens', value: formatWorkflowDate(selectedEngagement.start_date) },
                            { label: 'Window closes', value: formatWorkflowDate(selectedEngagement.end_date) },
                            { label: 'Pricing model', value: formatStatusLabel(selectedEngagement.pricing_model) },
                            { label: 'Team size', value: `${selectedEngagement.team_size || 1} researchers` },
                          ]}
                        />
                      </SectionCard>
                    </div>
                  </div>
                ) : null}

                {activeTab === 'findings' ? (
                  <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
                    <SectionCard
                      title="Structured PTaaS Findings"
                      description="These findings stay aligned to methodology, business impact, and remediation expectations."
                    >
                      {isLoadingFindings ? (
                        <p className="text-sm text-[#6d6760]">Loading PTaaS findings...</p>
                      ) : findings?.length ? (
                        <div className="space-y-4">
                          {findings.map((finding) => (
                            <div key={finding.id} className="rounded-[24px] border border-[#dbe3ec] bg-white dark:bg-[#111111] p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
                              <div className="flex flex-wrap items-start justify-between gap-3">
                                <div>
                                  <p className="text-base font-semibold text-[#2d2a26]">{finding.title}</p>
                                  <p className="mt-2 text-sm text-[#6d6760]">
                                    {finding.description || 'No description recorded.'}
                                  </p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  <StatusBadge status={finding.severity} />
                                  <StatusBadge status={finding.status} />
                                </div>
                              </div>
                              <div className="mt-4 grid gap-3 md:grid-cols-2">
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Affected component</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">
                                    {finding.affected_component || 'Not specified'}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Vulnerability type</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">
                                    {finding.vulnerability_type || 'Not specified'}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyCollection
                          title="No PTaaS findings captured yet"
                          description="Submit the first structured finding once you have exploit evidence and remediation guidance ready."
                        />
                      )}
                    </SectionCard>

                    <SectionCard
                      title="Capture New Finding"
                      description="This form follows the stricter enterprise PTaaS pattern: exploit proof, impact, and remediation are mandatory."
                    >
                      <div className="space-y-4">
                        <Input label="Finding title" value={findingForm.title} onChange={(event) => setFindingForm((current) => ({ ...current, title: event.target.value }))} />
                        <div className="grid gap-4 md:grid-cols-2">
                          <Select label="Severity" value={findingForm.severity} onChange={(event) => setFindingForm((current) => ({ ...current, severity: event.target.value }))}>
                            {['Critical', 'High', 'Medium', 'Low', 'Info'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                          <Input label="Affected component" value={findingForm.affected_component} onChange={(event) => setFindingForm((current) => ({ ...current, affected_component: event.target.value }))} />
                        </div>
                        <Input label="Vulnerability type" value={findingForm.vulnerability_type} onChange={(event) => setFindingForm((current) => ({ ...current, vulnerability_type: event.target.value }))} />
                        <Textarea label="Description" rows={3} value={findingForm.description} onChange={(event) => setFindingForm((current) => ({ ...current, description: event.target.value }))} />
                        <Textarea label="Proof of exploit" rows={4} value={findingForm.proof_of_exploit} onChange={(event) => setFindingForm((current) => ({ ...current, proof_of_exploit: event.target.value }))} />
                        <Textarea label="Impact analysis" rows={4} value={findingForm.impact_analysis} onChange={(event) => setFindingForm((current) => ({ ...current, impact_analysis: event.target.value }))} />
                        <Textarea label="Reproduction steps" rows={4} value={findingForm.reproduction_steps} onChange={(event) => setFindingForm((current) => ({ ...current, reproduction_steps: event.target.value }))} />
                        <Textarea label="Remediation guidance" rows={4} value={findingForm.remediation} onChange={(event) => setFindingForm((current) => ({ ...current, remediation: event.target.value }))} />
                        <Textarea
                          label="Remediation steps"
                          rows={3}
                          helperText="One action per line."
                          value={findingForm.remediation_steps}
                          onChange={(event) => setFindingForm((current) => ({ ...current, remediation_steps: event.target.value }))}
                        />
                        <div className="grid gap-4 md:grid-cols-3">
                          <Select label="Business impact" value={findingForm.business_impact} onChange={(event) => setFindingForm((current) => ({ ...current, business_impact: event.target.value }))}>
                            {['Critical', 'High', 'Medium', 'Low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                          <Select label="Remediation priority" value={findingForm.remediation_priority} onChange={(event) => setFindingForm((current) => ({ ...current, remediation_priority: event.target.value }))}>
                            {['Immediate', 'High', 'Medium', 'Low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                          <Select label="Remediation effort" value={findingForm.remediation_effort} onChange={(event) => setFindingForm((current) => ({ ...current, remediation_effort: event.target.value }))}>
                            {['Low', 'Medium', 'High', 'Very High'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                        </div>
                        <div className="grid gap-4 md:grid-cols-3">
                          <Select label="Confidentiality impact" value={findingForm.confidentiality} onChange={(event) => setFindingForm((current) => ({ ...current, confidentiality: event.target.value }))}>
                            {['Critical', 'High', 'Medium', 'Low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                          <Select label="Integrity impact" value={findingForm.integrity} onChange={(event) => setFindingForm((current) => ({ ...current, integrity: event.target.value }))}>
                            {['Critical', 'High', 'Medium', 'Low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                          <Select label="Availability impact" value={findingForm.availability} onChange={(event) => setFindingForm((current) => ({ ...current, availability: event.target.value }))}>
                            {['Critical', 'High', 'Medium', 'Low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {entry}
                              </option>
                            ))}
                          </Select>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                          <Textarea label="References" rows={2} helperText="One reference per line." value={findingForm.references} onChange={(event) => setFindingForm((current) => ({ ...current, references: event.target.value }))} />
                          <Textarea label="Exploit screenshot URLs" rows={2} helperText="One URL per line." value={findingForm.exploit_screenshots} onChange={(event) => setFindingForm((current) => ({ ...current, exploit_screenshots: event.target.value }))} />
                        </div>
                        <Button variant="primary" isLoading={isSubmittingFinding} onClick={handleSubmitFinding}>
                          Submit structured finding
                        </Button>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}

                {activeTab === 'progress' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
                    <SectionCard
                      title="Progress Updates"
                      description="Keep the client and internal team aligned with visible phase-by-phase PTaaS progress."
                    >
                      {isLoadingProgress ? (
                        <p className="text-sm text-[#6d6760]">Loading progress updates...</p>
                      ) : progressUpdates?.length ? (
                        <div className="space-y-4">
                          {progressUpdates.map((update) => (
                            <div key={update.id} className="rounded-[24px] border border-[#dbe3ec] bg-white dark:bg-[#111111] p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
                              <div className="flex items-center justify-between gap-3">
                                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                                  {update.progress_percentage}% complete
                                </p>
                                <p className="text-xs text-[#8b8177]">{formatWorkflowDate(update.created_at, 'Recently')}</p>
                              </div>
                              <p className="mt-3 text-sm leading-6 text-[#2d2a26]">{update.update_text}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyCollection
                          title="No progress updates yet"
                          description="Publish reconnaissance milestones, test coverage notes, and stakeholder handoff updates here."
                        />
                      )}
                    </SectionCard>

                    <SectionCard title="Post progress update" description="Use this for methodology progress, blockers, and coverage confirmation.">
                      <div className="space-y-4">
                        <Textarea label="Update text" rows={5} value={progressForm.update_text} onChange={(event) => setProgressForm((current) => ({ ...current, update_text: event.target.value }))} />
                        <Input label="Progress percentage" type="number" min={0} max={100} value={progressForm.progress_percentage} onChange={(event) => setProgressForm((current) => ({ ...current, progress_percentage: Number(event.target.value) }))} />
                        <Button variant="primary" isLoading={isSubmittingProgress} onClick={handleSubmitProgress}>
                          Publish update
                        </Button>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}

                {activeTab === 'deliverables' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
                    <SectionCard
                      title="Deliverables"
                      description="Track the client-facing outputs tied to the assessment: final report, methodology notes, and presentation material."
                    >
                      {isLoadingDeliverables ? (
                        <p className="text-sm text-[#6d6760]">Loading PTaaS deliverables...</p>
                      ) : deliverables?.length ? (
                        <div className="space-y-4">
                          {deliverables.map((deliverable) => (
                            <div key={deliverable.id} className="rounded-[24px] border border-[#dbe3ec] bg-white dark:bg-[#111111] p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
                              <div className="flex flex-wrap items-start justify-between gap-3">
                                <div>
                                  <p className="text-base font-semibold text-[#2d2a26]">{deliverable.title}</p>
                                  <p className="mt-2 text-sm text-[#6d6760]">
                                    {deliverable.description || 'No description provided.'}
                                  </p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  <StatusBadge status={deliverable.deliverable_type} />
                                  <StatusBadge status={deliverable.approved ? 'approved' : 'pending'} />
                                </div>
                              </div>
                              <div className="mt-4 grid gap-3 md:grid-cols-2">
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Version</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">{deliverable.version || '1.0'}</p>
                                </div>
                                <div>
                                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Submitted</p>
                                  <p className="mt-1 text-sm font-semibold text-[#2d2a26]">
                                    {formatWorkflowDate(deliverable.submitted_at, 'Not submitted')}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyCollection
                          title="No deliverables uploaded yet"
                          description="Final reports and supporting documentation will appear here once you publish them."
                        />
                      )}
                    </SectionCard>

                    <SectionCard title="Submit deliverable" description="Publish the final artifact or a supporting document for organization review.">
                      <div className="space-y-4">
                        <Select label="Deliverable type" value={deliverableForm.deliverable_type} onChange={(event) => setDeliverableForm((current) => ({ ...current, deliverable_type: event.target.value }))}>
                          {['report', 'documentation', 'presentation'].map((entry) => (
                            <option key={entry} value={entry}>
                              {formatStatusLabel(entry)}
                            </option>
                          ))}
                        </Select>
                        <Input label="Deliverable title" value={deliverableForm.title} onChange={(event) => setDeliverableForm((current) => ({ ...current, title: event.target.value }))} />
                        <Textarea label="Description" rows={4} value={deliverableForm.description} onChange={(event) => setDeliverableForm((current) => ({ ...current, description: event.target.value }))} />
                        <Input label="Hosted file URL" value={deliverableForm.file_url} onChange={(event) => setDeliverableForm((current) => ({ ...current, file_url: event.target.value }))} />
                        <Input label="Version" value={deliverableForm.version} onChange={(event) => setDeliverableForm((current) => ({ ...current, version: event.target.value }))} />
                        <Button variant="primary" isLoading={isSubmittingDeliverable} onClick={handleSubmitDeliverable}>
                          Submit deliverable
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
