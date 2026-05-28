'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Calendar, Shield, CheckCircle, AlertCircle, Save } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import {
  cvssScoreToFormValue,
  formatCvssLabel,
  hasCvssScore,
  parseNumeric,
  type CvssScore,
} from '@/lib/numbers';

const bountyToFormValue = cvssScoreToFormValue;
import { ptaasDbStatusToQueueStatus } from '@/lib/triageRoutes';

interface PTaaSFinding {
  id: string;
  engagement_id: string;
  title: string;
  description: string;
  severity: string;
  cvss_score?: CvssScore;
  affected_component?: string;
  proof_of_exploit?: string;
  exploit_code?: string;
  impact_analysis?: string;
  business_impact?: string;
  remediation?: string;
  remediation_steps?: string[];
  code_fix_example?: string;
  vulnerability_type?: string;
  cwe_id?: string;
  owasp_category?: string;
  attack_vector?: string;
  attack_complexity?: string;
  validated?: boolean;
  status: string;
  retest_notes?: string;
  reproduction_steps?: string;
  references?: string[];
  bounty_amount?: number | string | null;
  bounty_status?: string | null;
  discovered_at: string;
  created_at?: string;
}

const cardClass = 'bg-[#1E293B] rounded-lg border border-[#334155] p-6';
const sectionTitleClass = 'text-lg font-semibold text-[#F8FAFC] mb-4';
const bodyTextClass = 'text-sm text-[#CBD5E1] whitespace-pre-wrap';
const labelClass = 'text-xs font-semibold uppercase tracking-wider text-[#94A3B8]';
const valueClass = 'mt-1 text-sm text-[#F8FAFC]';

const severityColors: Record<string, string> = {
  critical: 'bg-[#EF4444] text-white',
  high: 'bg-[#F59E0B] text-white',
  medium: 'bg-[#F59E0B] text-white',
  low: 'bg-[#3B82F6] text-white',
  info: 'bg-[#94A3B8] text-white',
};

function FindingCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className={cardClass}>
      <h2 className={sectionTitleClass}>{title}</h2>
      {children}
    </div>
  );
}

interface TriagePtaasReportDetailProps {
  findingId: string;
}

export default function TriagePtaasReportDetail({ findingId }: TriagePtaasReportDetailProps) {
  const user = useAuthStore((state) => state.user);
  const [triageStatus, setTriageStatus] = useState('');
  const [assignedSeverity, setAssignedSeverity] = useState('');
  const [cvssScore, setCvssScore] = useState('');
  const [triageNotes, setTriageNotes] = useState('');
  const [bountyAmount, setBountyAmount] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: finding, isLoading, error, refetch } = useApiQuery<PTaaSFinding>(
    `/ptaas/findings/${findingId}`,
    { enabled: !!findingId }
  );

  useEffect(() => {
    if (!finding) return;
    setTriageStatus(ptaasDbStatusToQueueStatus(finding.status));
    setAssignedSeverity((finding.severity || 'medium').toLowerCase());
    setCvssScore(cvssScoreToFormValue(finding.cvss_score));
    setTriageNotes(finding.retest_notes || '');
    setBountyAmount(bountyToFormValue(finding.bounty_amount));
  }, [finding]);

  const handleSaveTriage = async () => {
    if (!triageStatus) {
      alert('Please select a status');
      return;
    }
    setIsSaving(true);
    try {
      const cvss = parseNumeric(cvssScore);
      const bounty = parseNumeric(bountyAmount);
      await api.post(`/triage/reports/${findingId}/update`, {
        status: triageStatus,
        assigned_severity: assignedSeverity || undefined,
        cvss_score: cvss ?? undefined,
        triage_notes: triageNotes || undefined,
        bounty_amount: bounty ?? undefined,
      });
      await refetch();
      alert('PTaaS finding triaged successfully');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      alert(message || 'Failed to save triage');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAssignToMe = async () => {
    setIsAssigning(true);
    try {
      await api.post(`/triage/reports/${findingId}/update`, { status: 'triaged' });
      await refetch();
      alert('Assigned to you — status set to In Progress');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      alert(message || 'Failed to assign finding');
    } finally {
      setIsAssigning(false);
    }
  };

  if (!user) return null;

  const severityKey = finding?.severity?.toLowerCase() || 'info';
  const queueStatus = finding ? ptaasDbStatusToQueueStatus(finding.status) : 'new';
  const isAssigned = queueStatus === 'triaged';

  return (
    <PortalShell
      user={user}
      title="Report Details"
      subtitle="PTaaS finding — same triage workflow as bug bounty"
      navItems={getPortalNavItems(user.role)}
      headerAlign="left"
      hideThemeToggle
    >
      <div className="mb-6 flex items-center gap-2">
        <Link href="/triage/queue" className="text-[#3B82F6] hover:underline text-sm">
          Queue
        </Link>
        <span className="text-[#94A3B8]">/</span>
        <span className="text-[#94A3B8] text-sm">PTaaS Finding</span>
      </div>

      {isLoading ? (
        <div className={`${cardClass} text-center`}>
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-[#334155] border-t-[#F8FAFC]" />
          <p className="mt-4 text-[#94A3B8]">Loading finding...</p>
        </div>
      ) : error ? (
        <div className={cardClass}>
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
            <p className="text-[#EF4444]">
              Error loading finding: {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </div>
        </div>
      ) : !finding ? (
        <div className={`${cardClass} text-center`}>
          <p className="text-sm font-semibold text-[#94A3B8]">Finding not found</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className={cardClass}>
            <p className="text-xs font-mono text-[#3B82F6] mb-2">
              PTAAS-{finding.id.slice(0, 8).toUpperCase()}
            </p>
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span
                className={`px-3 py-1 rounded text-xs font-bold uppercase ${severityColors[severityKey] || severityColors.info}`}
              >
                {finding.severity}
                {hasCvssScore(finding.cvss_score) && ` · ${formatCvssLabel(finding.cvss_score)}`}
              </span>
              <span className="px-3 py-1 rounded text-xs font-bold uppercase bg-[#334155] text-[#F8FAFC]">
                {queueStatus === 'new'
                  ? 'New'
                  : queueStatus === 'triaged'
                    ? 'In Progress'
                    : queueStatus === 'valid'
                      ? 'Valid'
                      : queueStatus === 'invalid'
                        ? 'Invalid'
                        : queueStatus}
              </span>
              {finding.validated && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded text-xs font-bold uppercase bg-[#22C55E] text-white">
                  <CheckCircle className="h-3 w-3" />
                  Validated
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-[#F8FAFC] mb-2">{finding.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-[#94A3B8]">
              <span className="inline-flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {new Date(finding.discovered_at || finding.created_at || '').toLocaleDateString()}
              </span>
              {finding.vulnerability_type && (
                <span className="inline-flex items-center gap-1">
                  <Shield className="h-4 w-4" />
                  {finding.vulnerability_type}
                </span>
              )}
            </div>
          </div>

          <div className={cardClass}>
            <h2 className={sectionTitleClass}>Triage Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <Select
                label="Status"
                value={triageStatus}
                onChange={(e) => setTriageStatus(e.target.value)}
                options={[
                  { value: 'new', label: 'New' },
                  { value: 'triaged', label: 'In Progress' },
                  { value: 'valid', label: 'Valid' },
                  { value: 'invalid', label: 'Invalid' },
                  { value: 'resolved', label: 'Resolved' },
                ]}
              />
              <Select
                label="Assigned Severity"
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
              <div>
                <label className="block text-sm font-medium text-[#94A3B8] mb-2">CVSS Score (0-10)</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={cvssScore}
                  onChange={(e) => setCvssScore(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                  Bounty Amount (ETB)
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={bountyAmount}
                  onChange={(e) => setBountyAmount(e.target.value)}
                  placeholder="Auto-filled from engagement base price on Valid"
                  className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC]"
                />
                <p className="mt-1 text-xs text-[#94A3B8]">
                  Set when marking Valid — organization approves via wallet, then Finance pays out.
                </p>
              </div>
            </div>
            <Textarea
              label="Triage Notes"
              value={triageNotes}
              onChange={(e) => setTriageNotes(e.target.value)}
              rows={4}
              className="bg-[#0f172a] border-[#334155] text-[#F8FAFC] placeholder:text-[#64748B]"
            />
            <div className="flex flex-wrap gap-3 mt-4">
              <Button onClick={handleSaveTriage} disabled={isSaving} className="gap-2">
                <Save className="h-4 w-4" />
                {isSaving ? 'Saving...' : 'Save Triage'}
              </Button>
              <Button
                onClick={handleAssignToMe}
                disabled={isAssigning || isAssigned}
                variant="outline"
                className="gap-2"
              >
                {isAssigned ? 'Assigned' : isAssigning ? 'Assigning...' : 'Assign to Me'}
              </Button>
              <Link href="/triage/queue">
                <Button variant="outline" className="gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Back to queue
                </Button>
              </Link>
            </div>
          </div>

          <FindingCard title="Description">
            <p className={bodyTextClass}>{finding.description}</p>
          </FindingCard>

          {finding.affected_component && (
            <FindingCard title="Affected Component">
              <p className={bodyTextClass}>{finding.affected_component}</p>
            </FindingCard>
          )}

          {finding.proof_of_exploit && (
            <FindingCard title="Proof of Exploit">
              <p className={`${bodyTextClass} mb-4`}>{finding.proof_of_exploit}</p>
              {finding.exploit_code && (
                <pre className="rounded-lg bg-[#0f172a] border border-[#334155] p-4 text-xs text-[#CBD5E1] overflow-x-auto">
                  <code>{finding.exploit_code}</code>
                </pre>
              )}
            </FindingCard>
          )}

          {finding.reproduction_steps && (
            <FindingCard title="Reproduction Steps">
              <p className={bodyTextClass}>{finding.reproduction_steps}</p>
            </FindingCard>
          )}

          {finding.impact_analysis && (
            <FindingCard title="Impact Analysis">
              <p className={`${bodyTextClass} mb-4`}>{finding.impact_analysis}</p>
              {finding.business_impact && (
                <div className="pt-4 border-t border-[#334155]">
                  <span className={labelClass}>Business Impact</span>
                  <p className={valueClass}>{finding.business_impact}</p>
                </div>
              )}
            </FindingCard>
          )}

          {finding.remediation && (
            <FindingCard title="Remediation">
              <p className={bodyTextClass}>{finding.remediation}</p>
            </FindingCard>
          )}

          {finding.references && finding.references.length > 0 && (
            <FindingCard title="References">
              <ul className="space-y-2">
                {finding.references.map((ref, index) => (
                  <li key={index}>
                    <a
                      href={ref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-[#3B82F6] hover:underline break-all"
                    >
                      {ref}
                    </a>
                  </li>
                ))}
              </ul>
            </FindingCard>
          )}
        </div>
      )}
    </PortalShell>
  );
}
