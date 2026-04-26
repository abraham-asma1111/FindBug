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
  WorkflowTimeline,
  formatStatusLabel,
  formatWorkflowDate,
  stringifyStructuredValue,
} from './shared';

interface AIRedTeamingEngagement {
  id: string;
  name: string;
  target_ai_system: string;
  model_type: string;
  testing_environment: string;
  ethical_guidelines: string;
  scope_description?: string | null;
  allowed_attack_types?: string[] | null;
  status: string;
  start_date?: string | null;
  end_date?: string | null;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
}

interface AITestingEnvironment {
  sandbox_url: string;
  api_endpoint: string;
  access_controls?: Record<string, unknown> | null;
  rate_limits?: Record<string, unknown> | null;
  is_isolated: boolean;
  monitoring_enabled: boolean;
  log_all_interactions: boolean;
}

interface AIVulnerabilityReport {
  id: string;
  title: string;
  attack_type: string;
  severity: string;
  status: string;
  classification?: string | null;
  impact: string;
  mitigation_recommendation?: string | null;
  submitted_at?: string | null;
}

const aiWorkflow = [
  {
    label: 'Briefing and policy calibration',
    detail: 'Review the model target, ethical limits, and in-scope harms before sending a single prompt.',
    state: 'complete' as const,
  },
  {
    label: 'Adversarial prompt execution',
    detail: 'Run prompt-injection, jailbreak, privacy, and safety probes against the approved sandbox.',
    state: 'active' as const,
  },
  {
    label: 'Transcript-backed evidence capture',
    detail: 'Good AI red teaming reports include the prompt, model response, attack framing, and observed impact.',
    state: 'active' as const,
  },
  {
    label: 'Model-specific remediation handoff',
    detail: 'Summarize mitigation guidance with model version, policy impact, and reproduction context.',
    state: 'upcoming' as const,
  },
];

export default function ResearcherAIRedTeamingWorkspace() {
  const user = useAuthStore((state) => state.user);
  const [selectedEngagementId, setSelectedEngagementId] = useState('');
  const [activeTab, setActiveTab] = useState<'briefing' | 'reports' | 'environment'>('briefing');
  const [pageError, setPageError] = useState('');
  const [pageSuccess, setPageSuccess] = useState('');
  const [reportForm, setReportForm] = useState({
    title: '',
    attack_type: 'prompt_injection',
    severity: 'high',
    input_prompt: '',
    model_response: '',
    impact: '',
    reproduction_steps: '',
    mitigation_recommendation: '',
    model_version: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    data: engagements,
    isLoading: isLoadingEngagements,
    error: engagementsError,
    refetch: refetchEngagements,
  } = useApiQuery<AIRedTeamingEngagement[]>('/ai-red-teaming/researcher/engagements', {
    enabled: !!user,
  });

  useEffect(() => {
    if (!engagements?.length) {
      setSelectedEngagementId('');
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
    data: testingEnvironment,
    isLoading: isLoadingEnvironment,
  } = useApiQuery<AITestingEnvironment>(
    selectedEngagementId ? `/ai-red-teaming/engagements/${selectedEngagementId}/testing-environment` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const {
    data: reports,
    isLoading: isLoadingReports,
    refetch: refetchReports,
  } = useApiQuery<AIVulnerabilityReport[]>(
    selectedEngagementId ? `/ai-red-teaming/engagements/${selectedEngagementId}/reports` : '',
    { enabled: !!user && !!selectedEngagementId }
  );

  const metrics = selectedEngagement
    ? [
        {
          label: 'Model type',
          value: formatStatusLabel(selectedEngagement.model_type),
          helper: selectedEngagement.target_ai_system,
        },
        {
          label: 'Engagement status',
          value: formatStatusLabel(selectedEngagement.status),
          helper: `${selectedEngagement.total_findings} AI findings tracked`,
        },
        {
          label: 'Critical plus high',
          value: `${selectedEngagement.critical_findings + selectedEngagement.high_findings}`,
          helper: 'Highest-risk model failures',
        },
        {
          label: 'Testing window',
          value: `${formatWorkflowDate(selectedEngagement.start_date, 'Not started')}`,
          helper: `Ends ${formatWorkflowDate(selectedEngagement.end_date, 'TBD')}`,
        },
      ]
    : [];

  async function handleSubmitReport() {
    if (!selectedEngagementId) {
      return;
    }

    try {
      setIsSubmitting(true);
      setPageError('');
      setPageSuccess('');
      await api.post(`/ai-red-teaming/engagements/${selectedEngagementId}/reports`, {
        ...reportForm,
        mitigation_recommendation: reportForm.mitigation_recommendation || null,
        model_version: reportForm.model_version || null,
      });
      setReportForm({
        title: '',
        attack_type: 'prompt_injection',
        severity: 'high',
        input_prompt: '',
        model_response: '',
        impact: '',
        reproduction_steps: '',
        mitigation_recommendation: '',
        model_version: '',
      });
      setPageSuccess('AI vulnerability report submitted with prompt and model-response evidence.');
      await Promise.all([refetchReports(), refetchEngagements()]);
      setActiveTab('reports');
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to submit the AI red teaming report.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="AI Red Teaming Desk"
          subtitle="Work assigned AI security engagements through a transcript-first workflow: scoped probing, evidence capture, and safety remediation handoff."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-sm tracking-[0.25em]"
        >
          <div className="space-y-6">
            <Banner
              title="AI Red Teaming"
              subtitle="This workspace now runs on live AI engagement data instead of a static invitation-only description. Assigned work, environment details, and report submission stay on one surface."
              accentClassName="bg-[linear-gradient(135deg,#50237e_0%,#7d39c2_45%,#c176ff_100%)]"
              badge="Transcript-Driven Testing"
              icon="🤖"
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
              <Alert variant="warning" title="AI engagement data is unavailable">
                {engagementsError.message}
              </Alert>
            ) : null}

            <SectionCard title="Assigned AI engagements" description="Only engagements explicitly assigned to you appear here.">
              {isLoadingEngagements ? (
                <p className="text-sm text-[#6d6760]">Loading AI red teaming engagements...</p>
              ) : engagements?.length ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  {engagements.map((engagement) => (
                    <button
                      key={engagement.id}
                      type="button"
                      onClick={() => setSelectedEngagementId(engagement.id)}
                      className={`rounded-[20px] border p-5 text-left transition ${
                        engagement.id === selectedEngagementId
                          ? 'border-[#7d39c2] bg-[#f6efff]'
                          : 'border-[#e6ddd4] bg-[#fcfaf7] hover:border-[#d5c4eb]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-lg font-semibold text-[#2d2a26]">{engagement.name}</p>
                          <p className="mt-2 text-sm text-[#6d6760]">{engagement.target_ai_system}</p>
                        </div>
                        <StatusBadge status={engagement.status} />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <EmptyCollection
                  title="No AI red teaming assignments yet"
                  description="This desk activates when an organization assigns you to an invitation-only AI engagement."
                />
              )}
            </SectionCard>

            {selectedEngagement ? (
              <>
                <MetricGrid items={metrics} />

                <div className="flex flex-wrap gap-2 rounded-[22px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-2">
                  {(['briefing', 'reports', 'environment'] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                        activeTab === tab
                          ? 'bg-[#7d39c2] text-white'
                          : 'text-[#6d6760] hover:bg-[#f5efe8] hover:text-[#2d2a26]'
                      }`}
                    >
                      {formatStatusLabel(tab)}
                    </button>
                  ))}
                </div>

                {activeTab === 'briefing' ? (
                  <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                    <SectionCard title="Engagement brief" description="Scope, approved attack types, and ethics guidance for this model assessment.">
                      <div className="space-y-5">
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Target AI system</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">{selectedEngagement.target_ai_system}</p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Scope description</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                            {selectedEngagement.scope_description || 'No additional scope notes were attached.'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Allowed attack types</p>
                          <div className="mt-2">
                            <PillList items={(selectedEngagement.allowed_attack_types || []).map((entry) => formatStatusLabel(entry))} />
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Ethical guidelines</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">{selectedEngagement.ethical_guidelines}</p>
                        </div>
                      </div>
                    </SectionCard>

                    <div className="space-y-6">
                      <SectionCard title="AI workflow" description="Modeled on how international AI red teaming programs handle scoped probing and evidence.">
                        <WorkflowTimeline steps={aiWorkflow} />
                      </SectionCard>

                      <SectionCard title="Safety surface" description="Current pressure points from the engagement counters.">
                        <div className="space-y-3 text-sm text-[#6d6760]">
                          <div className="flex items-center justify-between gap-3">
                            <span>Critical findings</span>
                            <span className="font-semibold text-[#2d2a26]">{selectedEngagement.critical_findings}</span>
                          </div>
                          <div className="flex items-center justify-between gap-3">
                            <span>High findings</span>
                            <span className="font-semibold text-[#2d2a26]">{selectedEngagement.high_findings}</span>
                          </div>
                          <div className="flex items-center justify-between gap-3">
                            <span>Medium findings</span>
                            <span className="font-semibold text-[#2d2a26]">{selectedEngagement.medium_findings}</span>
                          </div>
                          <div className="flex items-center justify-between gap-3">
                            <span>Low findings</span>
                            <span className="font-semibold text-[#2d2a26]">{selectedEngagement.low_findings}</span>
                          </div>
                        </div>
                      </SectionCard>
                    </div>
                  </div>
                ) : null}

                {activeTab === 'reports' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
                    <SectionCard title="Submitted AI reports" description="Prompt, response, and impact evidence already captured in this engagement.">
                      {isLoadingReports ? (
                        <p className="text-sm text-[#6d6760]">Loading AI vulnerability reports...</p>
                      ) : reports?.length ? (
                        <div className="space-y-4">
                          {reports.map((report) => (
                            <div key={report.id} className="rounded-[20px] border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                              <div className="flex flex-wrap items-start justify-between gap-3">
                                <div>
                                  <p className="text-base font-semibold text-[#2d2a26]">{report.title}</p>
                                  <p className="mt-2 text-sm text-[#6d6760]">{report.impact}</p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  <StatusBadge status={report.attack_type} />
                                  <StatusBadge status={report.severity} />
                                  <StatusBadge status={report.status} />
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyCollection
                          title="No AI reports yet"
                          description="Once you start probing the sandbox, submit your first prompt-and-response evidence package here."
                        />
                      )}
                    </SectionCard>

                    <SectionCard title="Submit AI report" description="Capture prompt, model response, impact, and mitigation in one structured submission.">
                      <div className="space-y-4">
                        <Input label="Report title" value={reportForm.title} onChange={(event) => setReportForm((current) => ({ ...current, title: event.target.value }))} />
                        <div className="grid gap-4 md:grid-cols-2">
                          <Select label="Attack type" value={reportForm.attack_type} onChange={(event) => setReportForm((current) => ({ ...current, attack_type: event.target.value }))}>
                            {['prompt_injection', 'jailbreak', 'data_leakage', 'model_extraction', 'adversarial_input', 'bias_exploitation', 'hallucination_trigger', 'context_manipulation', 'training_data_poisoning', 'model_inversion'].map((entry) => (
                              <option key={entry} value={entry}>
                                {formatStatusLabel(entry)}
                              </option>
                            ))}
                          </Select>
                          <Select label="Severity" value={reportForm.severity} onChange={(event) => setReportForm((current) => ({ ...current, severity: event.target.value }))}>
                            {['critical', 'high', 'medium', 'low'].map((entry) => (
                              <option key={entry} value={entry}>
                                {formatStatusLabel(entry)}
                              </option>
                            ))}
                          </Select>
                        </div>
                        <Textarea label="Input prompt" rows={4} value={reportForm.input_prompt} onChange={(event) => setReportForm((current) => ({ ...current, input_prompt: event.target.value }))} />
                        <Textarea label="Model response" rows={4} value={reportForm.model_response} onChange={(event) => setReportForm((current) => ({ ...current, model_response: event.target.value }))} />
                        <Textarea label="Impact" rows={3} value={reportForm.impact} onChange={(event) => setReportForm((current) => ({ ...current, impact: event.target.value }))} />
                        <Textarea label="Reproduction steps" rows={4} value={reportForm.reproduction_steps} onChange={(event) => setReportForm((current) => ({ ...current, reproduction_steps: event.target.value }))} />
                        <Textarea label="Mitigation recommendation" rows={3} value={reportForm.mitigation_recommendation} onChange={(event) => setReportForm((current) => ({ ...current, mitigation_recommendation: event.target.value }))} />
                        <Input label="Model version" value={reportForm.model_version} onChange={(event) => setReportForm((current) => ({ ...current, model_version: event.target.value }))} />
                        <Button variant="primary" isLoading={isSubmitting} onClick={handleSubmitReport}>
                          Submit AI finding
                        </Button>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}

                {activeTab === 'environment' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
                    <SectionCard title="Testing environment" description="Live sandbox and guardrail details for the assigned AI environment.">
                      {isLoadingEnvironment ? (
                        <p className="text-sm text-[#6d6760]">Loading environment details...</p>
                      ) : testingEnvironment ? (
                        <div className="space-y-5">
                          <div className="grid gap-4 md:grid-cols-2">
                            <div>
                              <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Sandbox URL</p>
                              <p className="mt-2 text-sm font-semibold text-[#2d2a26] break-all">{testingEnvironment.sandbox_url}</p>
                            </div>
                            <div>
                              <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">API endpoint</p>
                              <p className="mt-2 text-sm font-semibold text-[#2d2a26] break-all">{testingEnvironment.api_endpoint}</p>
                            </div>
                          </div>
                          <div className="grid gap-4 md:grid-cols-3">
                            <div className="rounded-2xl bg-[#fcfaf7] p-4 text-sm text-[#2d2a26]">
                              Isolated: <span className="font-semibold">{testingEnvironment.is_isolated ? 'Yes' : 'No'}</span>
                            </div>
                            <div className="rounded-2xl bg-[#fcfaf7] p-4 text-sm text-[#2d2a26]">
                              Monitoring: <span className="font-semibold">{testingEnvironment.monitoring_enabled ? 'Enabled' : 'Off'}</span>
                            </div>
                            <div className="rounded-2xl bg-[#fcfaf7] p-4 text-sm text-[#2d2a26]">
                              Transcript logging: <span className="font-semibold">{testingEnvironment.log_all_interactions ? 'On' : 'Off'}</span>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <EmptyCollection
                          title="Environment setup is not available"
                          description="The organization may not have published the sandbox details yet."
                        />
                      )}
                    </SectionCard>

                    <SectionCard title="Guardrails and rate limits" description="Use these controls to keep testing aligned with the engagement contract.">
                      {testingEnvironment ? (
                        <div className="space-y-4">
                          <div>
                            <p className="text-sm font-semibold text-[#2d2a26]">Access controls</p>
                            <pre className="mt-2 overflow-x-auto rounded-2xl bg-[#fcfaf7] p-4 text-xs text-[#5f584f]">
                              {stringifyStructuredValue(testingEnvironment.access_controls)}
                            </pre>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-[#2d2a26]">Rate limits</p>
                            <pre className="mt-2 overflow-x-auto rounded-2xl bg-[#fcfaf7] p-4 text-xs text-[#5f584f]">
                              {stringifyStructuredValue(testingEnvironment.rate_limits)}
                            </pre>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-[#6d6760]">No guardrail payload was returned for this engagement.</p>
                      )}
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
