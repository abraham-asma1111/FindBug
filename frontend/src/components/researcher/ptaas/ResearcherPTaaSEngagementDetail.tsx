'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import Alert from '@/components/ui/Alert';
import Spinner from '@/components/ui/Spinner';
import { 
  Calendar, Users, AlertCircle, CheckCircle, Clock, 
  Target, TrendingUp, Flag, RefreshCcw
} from 'lucide-react';
import ResearcherPTaaSRetestResultModal from '@/components/researcher/ptaas/ResearcherPTaaSRetestResultModal';
import {
  MetricGrid,
  SectionCard,
  StatusBadge,
  WorkflowTabs,
  formatStatusLabel,
  formatWorkflowDate,
} from '@/components/researcher/workflows/shared';

function normalizeApiError(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail;
  if (!detail) return error?.message || fallback;

  if (Array.isArray(detail)) {
    const lines = detail.map((item: any) => {
      if (typeof item === 'string') return item;
      const field = Array.isArray(item?.loc) ? item.loc.slice(1).join('.') : 'field';
      return `${field}: ${item?.msg || 'Invalid value'}`;
    });
    return lines.join('\n');
  }

  if (typeof detail === 'object') {
    if (typeof detail.message === 'string') return detail.message;
    try {
      return JSON.stringify(detail);
    } catch {
      return fallback;
    }
  }

  return String(detail);
}

interface PTaaSEngagement {
  id: string;
  name: string;
  description: string;
  status: string;
  testing_methodology: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  scope: any;
  deliverables: any;
  team_size: number;
  assigned_researchers: string[];
  pricing_model: string;
  base_price: number;
  compliance_requirements: string[];
  organization_id: string;
  created_at: string;
}

interface Finding {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

interface ResearcherPTaaSEngagementDetailProps {
  engagementId: string;
}

const statusConfig = {
  DRAFT: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  IN_PROGRESS: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
  COMPLETED: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  CANCELLED: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function ResearcherPTaaSEngagementDetail({ engagementId }: ResearcherPTaaSEngagementDetailProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [showFindingModal, setShowFindingModal] = useState(false);
  const [showRetestModal, setShowRetestModal] = useState(false);
  const [selectedRetestFindingId, setSelectedRetestFindingId] = useState<string | null>(null);
  const [acceptedNDA, setAcceptedNDA] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pageError, setPageError] = useState('');
  const [pageSuccess, setPageSuccess] = useState('');

  // Finding form state
  const [findingForm, setFindingForm] = useState({
    title: '',
    severity: 'Medium',
    vulnerability_type: 'Web Application',
    affected_component: '',
    description: '',
    reproduction_steps: '',
    impact_analysis: '',
    business_impact: 'Medium',
    technical_confidentiality: 'Medium',
    technical_integrity: 'Medium',
    technical_availability: 'Medium',
    remediation: '',
    remediation_priority: 'Medium',
    remediation_effort: 'Medium',
    remediation_steps: '',
    proof_of_exploit: ''
  });

  const { data: engagement, isLoading, error, refetch } = useApiQuery<PTaaSEngagement>({
    endpoint: `/ptaas/researcher/engagements/${engagementId}`
  });

  const { data: findings, refetch: refetchFindings } = useApiQuery<Finding[] | null>({
    endpoint: `/ptaas/engagements/${engagementId}/findings`,
    refetchInterval: 30000,
  });

  // IMPORTANT: hooks must run on every render (no early-return before useMemo).
  const findingsCount = findings?.length ?? 0;
  const retestCount = findings?.filter(f => f.status?.toUpperCase() === 'RETEST_REQUESTED').length ?? 0;
  const tabItems = useMemo(
    () =>
      [
        { value: 'overview', label: 'Overview' },
        { value: 'scope', label: 'Scope & Assets' },
        { value: 'testing', label: 'Testing' },
        // Findings tab shows badge with retest count if any pending
        { value: 'findings', label: retestCount > 0 ? `Findings 🔄${retestCount}` : 'Findings', badge: findingsCount },
        { value: 'team', label: 'Team' },
      ],
    [findingsCount, retestCount]
  );

  const handleAcceptEngagement = async () => {
    if (!acceptedNDA) {
      setPageError('Please accept the NDA and testing rules.');
      return;
    }

    setIsAccepting(true);
    try {
      setPageError('');
      setPageSuccess('');
      await api.post(`/ptaas/researcher/engagements/${engagementId}/accept`, {});
      setPageSuccess('Engagement accepted successfully. You can now start testing and submitting findings.');
      setShowAcceptModal(false);
      refetch();
    } catch (error: any) {
      setPageError(normalizeApiError(error, 'Failed to accept engagement.'));
    } finally {
      setIsAccepting(false);
    }
  };

  const handleSubmitFinding = async () => {
    setIsSubmitting(true);
    try {
      setPageError('');
      setPageSuccess('');
      if (findingForm.proof_of_exploit.length < 50) {
        setPageError('proof_of_exploit must be at least 50 characters.');
        return;
      }
      if (findingForm.impact_analysis.length < 50) {
        setPageError('impact_analysis must be at least 50 characters.');
        return;
      }
      if (findingForm.remediation.length < 50) {
        setPageError('remediation must be at least 50 characters.');
        return;
      }
      if (!findingForm.affected_component.trim()) {
        setPageError('affected_component is required.');
        return;
      }
      if (!findingForm.vulnerability_type.trim()) {
        setPageError('vulnerability_type is required.');
        return;
      }
      const remediationSteps = findingForm.remediation_steps
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean);
      if (remediationSteps.length === 0) {
        setPageError('At least one remediation step is required.');
        return;
      }
      await api.post(`/ptaas/findings`, {
        engagement_id: engagementId,
        title: findingForm.title,
        severity: findingForm.severity,
        vulnerability_type: findingForm.vulnerability_type,
        affected_component: findingForm.affected_component,
        description: findingForm.description,
        reproduction_steps: findingForm.reproduction_steps,
        proof_of_exploit: findingForm.proof_of_exploit,
        impact_analysis: findingForm.impact_analysis,
        business_impact: findingForm.business_impact,
        technical_impact: {
          confidentiality: findingForm.technical_confidentiality,
          integrity: findingForm.technical_integrity,
          availability: findingForm.technical_availability,
        },
        remediation: findingForm.remediation,
        remediation_priority: findingForm.remediation_priority,
        remediation_effort: findingForm.remediation_effort,
        remediation_steps: remediationSteps,
      });
      setPageSuccess('Finding submitted successfully.');
      setShowFindingModal(false);
      await refetchFindings();
      refetch();
      setActiveTab('findings');
      setFindingForm({
        title: '',
        severity: 'Medium',
        vulnerability_type: 'Web Application',
        affected_component: '',
        description: '',
        reproduction_steps: '',
        impact_analysis: '',
        business_impact: 'Medium',
        technical_confidentiality: 'Medium',
        technical_integrity: 'Medium',
        technical_availability: 'Medium',
        remediation: '',
        remediation_priority: 'Medium',
        remediation_effort: 'Medium',
        remediation_steps: '',
        proof_of_exploit: ''
      });
    } catch (error: any) {
      setPageError(normalizeApiError(error, 'Failed to submit finding.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !engagement) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Failed to load engagement</h3>
            <p className="text-sm text-red-700">{error?.message || 'Engagement not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.DRAFT;
  const StatusIcon = statusInfo.icon;

  const metrics = [
    {
      label: 'Methodology',
      value: formatStatusLabel(engagement.testing_methodology),
      helper: 'Testing framework assigned',
    },
    {
      label: 'Team size',
      value: String(engagement.team_size ?? 0),
      helper: 'Assigned researchers',
    },
    {
      label: 'Findings',
      value: String(findings?.length || 0),
      helper: 'Submitted in this engagement',
    },
    {
      label: 'Duration',
      value: engagement.duration_days ? `${engagement.duration_days} days` : 'TBD',
      helper: `${formatWorkflowDate(engagement.start_date, 'Start TBD')} → ${formatWorkflowDate(engagement.end_date, 'End TBD')}`,
    },
  ];

  return (
    <div className="space-y-6">
      <SectionCard
        title={engagement.name}
        description={engagement.description}
        action={
          <div className="flex items-center gap-2">
            <StatusBadge status={statusInfo.label} />
            {engagement.status === 'DRAFT' ? (
              <Button size="sm" onClick={() => setShowAcceptModal(true)}>
                <CheckCircle className="mr-1 h-4 w-4" />
                Accept engagement
              </Button>
            ) : null}
          </div>
        }
      >
        <MetricGrid items={metrics} />
      </SectionCard>

      {pageError ? (
        <Alert variant="error" title="PTaaS workflow issue">
          {pageError}
        </Alert>
      ) : null}

      {pageSuccess ? (
        <Alert variant="success" title="PTaaS updated">
          {pageSuccess}
        </Alert>
      ) : null}

      <WorkflowTabs
        tone="blue"
        active={activeTab as any}
        onChange={(value) => setActiveTab(value)}
        items={tabItems as any}
      />

      <SectionCard title={formatStatusLabel(activeTab)} description="Engagement workspace panel.">
        {activeTab === 'overview' && <OverviewTab engagement={engagement} />}
        {activeTab === 'scope' && <ScopeTab engagement={engagement} />}
        {activeTab === 'testing' && <TestingTab engagement={engagement} />}
        {activeTab === 'findings' && (
          <FindingsTab
            findings={findings}
            onSubmit={() => setShowFindingModal(true)}
            onSubmitRetest={(id) => {
              setSelectedRetestFindingId(id);
              setShowRetestModal(true);
            }}
            engagementId={engagementId}
          />
        )}
        {activeTab === 'team' && <TeamTab engagement={engagement} />}
      </SectionCard>

      {/* Accept Engagement Modal */}
      <Modal
        isOpen={showAcceptModal}
        onClose={() => setShowAcceptModal(false)}
        title="Accept Engagement"
      >
        <div className="space-y-4">
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">Non-Disclosure Agreement (NDA)</h4>
                <p className="text-sm text-blue-700 mb-3">
                  By accepting this engagement, you agree to:
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Keep all engagement details confidential</li>
                  <li>• Not disclose any vulnerabilities publicly</li>
                  <li>• Follow the defined scope and testing rules</li>
                  <li>• Report findings only through the platform</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={acceptedNDA}
              onChange={(e) => setAcceptedNDA(e.target.checked)}
              className="mt-1"
            />
            <label className="text-sm text-[#2d2a26]">
              I have read and agree to the NDA and testing rules
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setShowAcceptModal(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleAcceptEngagement}
              disabled={!acceptedNDA}
              isLoading={isAccepting}
              className="flex-1"
            >
              Accept Engagement
            </Button>
          </div>
        </div>
      </Modal>

      {/* Submit Finding Modal */}
      <Modal
        isOpen={showFindingModal}
        onClose={() => setShowFindingModal(false)}
        title="Submit Finding"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Title
            </label>
            <input
              type="text"
              value={findingForm.title}
              onChange={(e) => setFindingForm({ ...findingForm, title: e.target.value })}
              className="w-full rounded-xl border border-[#e6ddd4] bg-white px-3 py-2 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-[#111111] dark:text-gray-100"
              placeholder="Brief title of the vulnerability"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Severity
            </label>
            <Select
              value={findingForm.severity}
              onChange={(e) => setFindingForm({ ...findingForm, severity: e.target.value })}
              options={[
                { value: 'Critical', label: 'Critical' },
                { value: 'High', label: 'High' },
                { value: 'Medium', label: 'Medium' },
                { value: 'Low', label: 'Low' },
                { value: 'Info', label: 'Info' },
              ]}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Vulnerability Type
            </label>
            <input
              type="text"
              value={findingForm.vulnerability_type}
              onChange={(e) => setFindingForm({ ...findingForm, vulnerability_type: e.target.value })}
              className="w-full rounded-xl border border-[#e6ddd4] bg-white px-3 py-2 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-[#111111] dark:text-gray-100"
              placeholder="e.g., SQL Injection"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Affected Component
            </label>
            <input
              type="text"
              value={findingForm.affected_component}
              onChange={(e) => setFindingForm({ ...findingForm, affected_component: e.target.value })}
              className="w-full rounded-xl border border-[#e6ddd4] bg-white px-3 py-2 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-[#111111] dark:text-gray-100"
              placeholder="e.g., /api/v1/auth/login"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Description
            </label>
            <Textarea
              value={findingForm.description}
              onChange={(e) => setFindingForm({ ...findingForm, description: e.target.value })}
              rows={3}
              placeholder="Detailed description of the vulnerability"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Steps to Reproduce
            </label>
            <Textarea
              value={findingForm.reproduction_steps}
              onChange={(e) => setFindingForm({ ...findingForm, reproduction_steps: e.target.value })}
              rows={3}
              placeholder="Step-by-step reproduction instructions"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Impact Analysis
            </label>
            <Textarea
              value={findingForm.impact_analysis}
              onChange={(e) => setFindingForm({ ...findingForm, impact_analysis: e.target.value })}
              rows={2}
              placeholder="Business and technical impact"
            />
            <p className="mt-1 text-xs text-[#8b8177]">
              {findingForm.impact_analysis.length}/50 minimum characters
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">Business Impact</label>
              <Select
                value={findingForm.business_impact}
                onChange={(e) => setFindingForm({ ...findingForm, business_impact: e.target.value })}
                options={[
                  { value: 'Critical', label: 'Critical' },
                  { value: 'High', label: 'High' },
                  { value: 'Medium', label: 'Medium' },
                  { value: 'Low', label: 'Low' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">Remediation Priority</label>
              <Select
                value={findingForm.remediation_priority}
                onChange={(e) => setFindingForm({ ...findingForm, remediation_priority: e.target.value })}
                options={[
                  { value: 'Immediate', label: 'Immediate' },
                  { value: 'High', label: 'High' },
                  { value: 'Medium', label: 'Medium' },
                  { value: 'Low', label: 'Low' },
                ]}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-[#8b8177] mb-1">Tech impact: C</label>
              <Select value={findingForm.technical_confidentiality} onChange={(e) => setFindingForm({ ...findingForm, technical_confidentiality: e.target.value })} options={[{ value: 'Low', label: 'Low' }, { value: 'Medium', label: 'Medium' }, { value: 'High', label: 'High' }]} />
            </div>
            <div>
              <label className="block text-xs font-medium text-[#8b8177] mb-1">Tech impact: I</label>
              <Select value={findingForm.technical_integrity} onChange={(e) => setFindingForm({ ...findingForm, technical_integrity: e.target.value })} options={[{ value: 'Low', label: 'Low' }, { value: 'Medium', label: 'Medium' }, { value: 'High', label: 'High' }]} />
            </div>
            <div>
              <label className="block text-xs font-medium text-[#8b8177] mb-1">Tech impact: A</label>
              <Select value={findingForm.technical_availability} onChange={(e) => setFindingForm({ ...findingForm, technical_availability: e.target.value })} options={[{ value: 'Low', label: 'Low' }, { value: 'Medium', label: 'Medium' }, { value: 'High', label: 'High' }]} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Proof of Exploit (min 50 chars)</label>
            <Textarea
              value={findingForm.proof_of_exploit}
              onChange={(e) => setFindingForm({ ...findingForm, proof_of_exploit: e.target.value })}
              rows={3}
              placeholder="Provide clear PoC evidence, payloads, and observed behavior..."
            />
            <p className="mt-1 text-xs text-[#8b8177]">
              {findingForm.proof_of_exploit.length}/50 minimum characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Remediation (min 50 chars)</label>
            <Textarea
              value={findingForm.remediation}
              onChange={(e) => setFindingForm({ ...findingForm, remediation: e.target.value })}
              rows={3}
              placeholder="Provide concrete remediation guidance..."
            />
            <p className="mt-1 text-xs text-[#8b8177]">
              {findingForm.remediation.length}/50 minimum characters
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">Remediation Effort</label>
              <Select
                value={findingForm.remediation_effort}
                onChange={(e) => setFindingForm({ ...findingForm, remediation_effort: e.target.value })}
                options={[
                  { value: 'Low', label: 'Low' },
                  { value: 'Medium', label: 'Medium' },
                  { value: 'High', label: 'High' },
                  { value: 'Very High', label: 'Very High' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#2d2a26] mb-1">Remediation Steps (one per line)</label>
              <Textarea
                value={findingForm.remediation_steps}
                onChange={(e) => setFindingForm({ ...findingForm, remediation_steps: e.target.value })}
                rows={3}
                placeholder="1. Step one&#10;2. Step two"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
            <Button variant="outline" onClick={() => setShowFindingModal(false)} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleSubmitFinding}
              disabled={isSubmitting || !findingForm.title}
              isLoading={isSubmitting}
              className="flex-1"
            >
              Submit Finding
            </Button>
          </div>
        </div>
      </Modal>

      {showRetestModal && selectedRetestFindingId && (
        <ResearcherPTaaSRetestResultModal
          isOpen={showRetestModal}
          onClose={() => { setShowRetestModal(false); setSelectedRetestFindingId(null); }}
          findingId={selectedRetestFindingId}
          onSuccess={refetchFindings}
        />
      )}
    </div>
  );
}

// Overview Tab
function OverviewTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Engagement Details</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Start Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">
                {new Date(engagement.start_date).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-[#8b8177]">End Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">
                {new Date(engagement.end_date).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
          </div>
          {engagement.compliance_requirements && engagement.compliance_requirements.length > 0 && (
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Compliance Requirements</label>
              <ul className="mt-2 space-y-1">
                {engagement.compliance_requirements.map((req, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-[#2d2a26]">
                    <span className="text-blue-500">•</span>
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Scope Tab
function ScopeTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26]">Scope & Target Assets</h3>
      <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
        <pre className="text-sm text-[#2d2a26] whitespace-pre-wrap">
          {engagement.scope ? JSON.stringify(engagement.scope, null, 2) : 'No scope details available'}
        </pre>
      </div>
    </div>
  );
}

// Testing Tab
function TestingTab({ engagement }: { engagement: PTaaSEngagement }) {
  const methodologyPhases: Record<string, string[]> = {
    OWASP: ['Information Gathering', 'Configuration Testing', 'Identity Management', 'Authentication', 'Authorization', 'Session Management', 'Input Validation', 'Error Handling', 'Cryptography', 'Business Logic', 'Client-Side Testing'],
    PTES: ['Pre-engagement Interactions', 'Intelligence Gathering', 'Threat Modeling', 'Vulnerability Analysis', 'Exploitation', 'Post Exploitation', 'Reporting'],
    NIST: ['Planning', 'Discovery', 'Attack & Penetration', 'Reporting', 'Compliance Validation'],
  };

  const phases = methodologyPhases[engagement.testing_methodology] || [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">
          Testing Methodology: {engagement.testing_methodology}
        </h3>
        <div className="space-y-2">
          {phases.map((phase, idx) => (
            <div key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-[#e6ddd4] bg-[#faf6f1]">
              <input type="checkbox" className="w-4 h-4" />
              <span className="text-sm text-[#2d2a26]">{phase}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Findings Tab
function FindingsTab({
  findings,
  onSubmit,
  onSubmitRetest,
  engagementId,
}: {
  findings: Finding[] | null | undefined;
  onSubmit: () => void;
  onSubmitRetest: (id: string) => void;
  engagementId: string;
}) {
  const router = useRouter();

  const statusBadge = (status: string) => {
    const s = status?.toUpperCase();
    if (s === 'RETEST_REQUESTED') return 'bg-orange-100 text-orange-700 border border-orange-300';
    if (s === 'VERIFIED') return 'bg-green-100 text-green-700';
    if (s === 'CLOSED') return 'bg-gray-100 text-gray-600';
    if (s === 'SUBMITTED') return 'bg-blue-100 text-blue-700';
    if (s === 'TRIAGED') return 'bg-purple-100 text-purple-700';
    if (s === 'IN_PROGRESS') return 'bg-yellow-100 text-yellow-700';
    if (s === 'REJECTED') return 'bg-red-100 text-red-700';
    return 'bg-blue-100 text-blue-700';
  };

  const statusLabel = (status: string) => {
    const s = status?.toUpperCase();
    if (s === 'RETEST_REQUESTED') return '🔄 Retest Requested';
    if (s === 'VERIFIED') return '✅ Verified';
    if (s === 'CLOSED') return '💰 Bounty Approved';
    return status?.replace(/_/g, ' ');
  };

  if (!findings || findings.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
          <Flag className="h-8 w-8 text-[#8b8177]" />
        </div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">No findings submitted yet</h3>
        <p className="text-sm text-[#6d6760] mb-6">Start testing and submit your first security finding</p>
        <Button onClick={onSubmit}>
          <Flag className="h-4 w-4 mr-1" />
          Submit Finding
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Submitted Findings ({findings.length})</h3>
        <Button size="sm" onClick={onSubmit}>
          <Flag className="h-4 w-4 mr-1" />
          Submit Finding
        </Button>
      </div>
      <div className="space-y-3">
        {findings.map((finding) => {
          const isRetest = finding.status?.toUpperCase() === 'RETEST_REQUESTED';
          return (
            <div
              key={finding.id}
              className={`p-4 rounded-xl border transition-all ${
                isRetest
                  ? 'border-orange-300 bg-orange-50'
                  : 'border-[#e6ddd4] bg-[#faf6f1] hover:bg-white cursor-pointer'
              }`}
              onClick={isRetest ? undefined : () => router.push(`/researcher/programs/ptaas/${engagementId}/findings/${finding.id}`)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {isRetest && <RefreshCcw className="h-4 w-4 text-orange-600 flex-shrink-0 animate-spin-slow" />}
                    <h4 className="font-medium text-[#2d2a26] truncate">{finding.title}</h4>
                  </div>
                  <p className="text-sm text-[#6d6760]">
                    Submitted {new Date(finding.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    finding.severity?.toLowerCase() === 'critical' ? 'bg-red-100 text-red-700' :
                    finding.severity?.toLowerCase() === 'high' ? 'bg-orange-100 text-orange-700' :
                    finding.severity?.toLowerCase() === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {finding.severity}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${statusBadge(finding.status)}`}>
                    {statusLabel(finding.status)}
                  </span>
                  {isRetest && (
                    <Button
                      size="sm"
                      className="bg-orange-600 hover:bg-orange-700 text-white ml-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSubmitRetest(finding.id);
                      }}
                    >
                      <RefreshCcw className="h-3.5 w-3.5 mr-1" />
                      Submit Retest
                    </Button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


// Team Tab
function TeamTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26]">Team Members</h3>
      <p className="text-sm text-[#6d6760]">
        {engagement.team_size} team member(s) assigned to this engagement
      </p>
      <div className="space-y-3">
        {engagement.assigned_researchers.map((researcherId, idx) => (
          <div key={idx} className="p-4 rounded-xl border border-[#e6ddd4] bg-[#faf6f1]">
            <p className="text-sm font-medium text-[#2d2a26]">Researcher {idx + 1}</p>
            <p className="text-xs text-[#8b8177] mt-1">{researcherId}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
