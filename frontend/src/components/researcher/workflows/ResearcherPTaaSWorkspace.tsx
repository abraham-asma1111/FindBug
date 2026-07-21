'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Alert from '@/components/ui/Alert';
import Button from '@/components/ui/Button';
import Spinner from '@/components/ui/Spinner';
import { useApiQuery } from '@/hooks/useApiQuery';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import {
  Banner,
  EmptyCollection,
  MetricGrid,
  ProgramGuide,
  ProgramHighlights,
  SectionCard,
  WorkflowPickerCard,
  WorkflowTimeline,
  formatStatusLabel,
  formatWorkflowDate,
} from './shared';
import { ptaasProgramGuide } from './programGuideContent';

interface PTaaSEngagement {
  id: string;
  name: string;
  description?: string | null;
  status: string;
  testing_methodology?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  duration_days?: number | null;
  team_size?: number | null;
  pricing_model?: string | null;
  base_price?: number | null;
}

const ptaasWorkflow = [
  {
    label: 'Scope and methodology alignment',
    detail: 'Confirm OWASP, PTES, NIST, or custom methodology before testing begins.',
    state: 'complete' as const,
  },
  {
    label: 'Structured testing execution',
    detail: 'Work through phase checklists, capture findings with CVSS, and collaborate with triage.',
    state: 'active' as const,
  },
  {
    label: 'Deliverable and executive reporting',
    detail: 'Submit technical and executive outputs once the engagement testing window closes.',
    state: 'active' as const,
  },
  {
    label: 'Retest and verification',
    detail: 'Validate remediations during the free retest window and close findings cleanly.',
    state: 'upcoming' as const,
  },
];

const highlights = [
  {
    title: 'Structured methodologies',
    description: 'OWASP, PTES, NIST, and custom frameworks with phase checklists and progress tracking.',
  },
  {
    title: 'Real-time findings',
    description: 'Submit CVSS-scored findings as you discover them; triage validates before client delivery.',
  },
  {
    title: 'Compliance reports',
    description: 'Executive summaries and technical reports generated for audit-ready handoff.',
  },
  {
    title: 'Retest workflow',
    description: 'Free retest period to verify fixes and confirm remediation quality.',
  },
];

export default function ResearcherPTaaSWorkspace() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState('all');

  const {
    data: engagements,
    isLoading,
    error: engagementsError,
    refetch,
  } = useApiQuery<PTaaSEngagement[]>('/ptaas/researcher/engagements', {
    enabled: !!user,
  });

  const filteredEngagements = useMemo(() => {
    const list = engagements || [];
    if (statusFilter === 'all') return list;
    return list.filter((entry) => entry.status === statusFilter);
  }, [engagements, statusFilter]);

  const activeCount = (engagements || []).filter((e) => e.status === 'IN_PROGRESS').length;
  const metrics = [
    {
      label: 'Assigned engagements',
      value: String((engagements || []).length),
      helper: `${activeCount} currently in progress`,
    },
    {
      label: 'Active testing',
      value: String(activeCount),
      helper: 'Open the engagement workspace to continue',
    },
    {
      label: 'Completed',
      value: String((engagements || []).filter((e) => e.status === 'COMPLETED').length),
      helper: 'Closed engagements with final reports',
    },
    {
      label: 'Methodologies',
      value: '4',
      helper: 'OWASP · PTES · NIST · Custom',
    },
  ];

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Command Desk"
          subtitle="Run penetration testing engagements with structured methodologies, live findings, and compliance-ready deliverables."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            <Banner
              tone="blue"
              icon="🛡️"
              badge="Penetration Testing as a Service"
              title="Professional pentesting on demand"
              subtitle="Assigned engagements, methodology-driven testing, finding submission, and retest verification — all in one operational desk."
              asideTitle="Engagement-first delivery"
              asideDescription="Select an assignment to open the full testing workspace with findings, checklists, and collaboration."
            />

            {engagementsError ? (
              <Alert variant="warning" title="PTaaS data unavailable">
                {engagementsError.message}
              </Alert>
            ) : null}

            <MetricGrid items={metrics} />

            <ProgramHighlights items={highlights} tone="blue" />

            <ProgramGuide guide={ptaasProgramGuide} tone="blue" defaultOpen />

            <SectionCard
              title="My PTaaS engagements"
              description="Open an assignment to access findings, checklists, collaboration, and deliverables."
              action={
                <Button variant="outline" onClick={() => void refetch()}>
                  Refresh
                </Button>
              }
            >
              <div className="mb-5 flex flex-wrap gap-2">
                {[
                  { value: 'all', label: 'All' },
                  { value: 'DRAFT', label: 'Draft' },
                  { value: 'IN_PROGRESS', label: 'In progress' },
                  { value: 'COMPLETED', label: 'Completed' },
                ].map((filter) => (
                  <button
                    key={filter.value}
                    type="button"
                    onClick={() => setStatusFilter(filter.value)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      statusFilter === filter.value
                        ? 'bg-[#0f4c81] text-white'
                        : 'border border-[#dbe3ec] bg-[#f7f9fc] text-[#475467] hover:border-[#b8d9ef] dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {isLoading ? (
                <div className="flex justify-center py-12">
                  <Spinner size="lg" />
                </div>
              ) : filteredEngagements.length ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  {filteredEngagements.map((engagement) => (
                    <WorkflowPickerCard
                      key={engagement.id}
                      tone="blue"
                      selected={false}
                      onClick={() => router.push(`/researcher/programs/ptaas/${engagement.id}`)}
                      title={engagement.name}
                      description={engagement.description || 'No description provided.'}
                      status={engagement.status}
                      metrics={[
                        {
                          label: 'Methodology',
                          value: formatStatusLabel(engagement.testing_methodology || 'custom'),
                        },
                        {
                          label: 'Timeline',
                          value: engagement.duration_days
                            ? `${engagement.duration_days} days`
                            : formatWorkflowDate(engagement.start_date, 'TBD'),
                        },
                      ]}
                      footer={
                        <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
                          <span className="text-[#556273] dark:text-gray-400">
                            {engagement.pricing_model
                              ? formatStatusLabel(engagement.pricing_model)
                              : 'Pricing not set'}
                            {engagement.base_price != null
                              ? ` · ${formatCurrency(engagement.base_price)}`
                              : ''}
                          </span>
                          <span className="font-semibold text-[#0f4c81]">Open workspace →</span>
                        </div>
                      }
                    />
                  ))}
                </div>
              ) : (
                <EmptyCollection
                  title="No PTaaS engagements yet"
                  description="When an organization assigns you to a penetration test, it will appear here with full workspace access."
                  hint="Check invitations and organization outreach"
                />
              )}
            </SectionCard>

            <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
              <SectionCard title="Engagement lifecycle" description="How PTaaS engagements move from assignment to retest.">
                <WorkflowTimeline steps={ptaasWorkflow} />
              </SectionCard>

              <SectionCard title="Resources" description="Guides and methodology references for your next engagement.">
                <div className="space-y-3">
                  <Link
                    href="/researcher/programs/ptaas/guide"
                    className="flex items-center justify-between rounded-[20px] border border-[#dbe3ec] bg-[#f7f9fc] px-4 py-3 text-sm font-semibold text-[#0f4c81] transition hover:border-[#b8d9ef] dark:border-gray-700 dark:bg-gray-800 dark:text-blue-300"
                  >
                    PTaaS researcher guide
                    <span>→</span>
                  </Link>
                  <div className="rounded-[20px] border border-[#dbe3ec] bg-[#fbfcfd] px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#728092] dark:text-gray-400">
                      Supported frameworks
                    </p>
                    <p className="mt-2 text-sm text-[#334155] dark:text-gray-300">
                      OWASP WSTG · PTES · NIST SP 800-115 · Custom hybrid
                    </p>
                  </div>
                </div>
              </SectionCard>
            </div>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
