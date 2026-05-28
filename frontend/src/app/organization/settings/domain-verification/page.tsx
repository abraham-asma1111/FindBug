'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { useAuthStore } from '@/store/authStore';
import { getPortalNavItems } from '@/lib/portal';
import { api } from '@/lib/api';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

type Method = 'dns' | 'file';
type ProgramFilter = 'all' | 'verified' | 'needs_action';

interface VerifiedResponse {
  domain_verified: boolean;
  verified_domains: string[];
  verification_status: string;
  phase1_submitted?: boolean;
  admin_approval_required?: boolean;
  reconciled_verified_domains?: boolean;
}

interface StartResponse {
  method: Method;
  domain: string;
  verification_token: string;
  instructions: string;
}

interface PhaseOnePayload {
  business_license_url: string;
  tax_id: string;
  legal_name: string;
  attest_owns_assets: boolean;
  attest_accepts_liability: boolean;
}

interface PhaseThreeProgramSummary {
  program_id: string;
  program_name: string;
  program_status: string;
  all_verified: boolean;
  verifiable_scope_count: number;
  verified_scope_count: number;
  pending_assets: Array<{
    scope_id: string;
    asset_identifier: string;
    asset_type: string;
    verification_status: string;
  }>;
}

interface PhaseThreeSummaryResponse {
  success: boolean;
  total_programs: number;
  total_verifiable_scopes: number;
  total_verified_scopes: number;
  all_scopes_verified: boolean;
  programs: PhaseThreeProgramSummary[];
}

export default function OrganizationDomainVerificationPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const [hasAccessToken, setHasAccessToken] = useState(false);
  const [domain, setDomain] = useState('');
  const [method, setMethod] = useState<Method>('dns');
  const [startData, setStartData] = useState<StartResponse | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isSubmittingPhase1, setIsSubmittingPhase1] = useState(false);
  const [isRunningPhase4, setIsRunningPhase4] = useState(false);
  const [showAllPrograms, setShowAllPrograms] = useState(false);
  const [programSearch, setProgramSearch] = useState('');
  const [programFilter, setProgramFilter] = useState<ProgramFilter>('all');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [phase1Message, setPhase1Message] = useState<string | null>(null);
  const [phase1, setPhase1] = useState<PhaseOnePayload>({
    business_license_url: '',
    tax_id: '',
    legal_name: '',
    attest_owns_assets: false,
    attest_accepts_liability: false,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    setHasAccessToken(!!localStorage.getItem('access_token'));
  }, []);

  const { data, refetch } = useApiQuery<VerifiedResponse>('/domain/verified', {
    enabled: !!user || hasAccessToken,
  });
  const { data: phase3Data, refetch: refetchPhase3 } = useApiQuery<PhaseThreeSummaryResponse>('/domain/verify/phase3-summary', {
    enabled: !!user || hasAccessToken,
  });

  const suggestedDomain = useMemo(() => {
    const website = (user as any)?.organization?.website as string | undefined;
    if (!website) return '';
    try {
      const u = website.startsWith('http') ? new URL(website) : new URL(`https://${website}`);
      return u.hostname.replace(/^www\./, '');
    } catch {
      return '';
    }
  }, [user]);

  const filteredPrograms = useMemo(() => {
    const query = programSearch.trim().toLowerCase();
    const programs = (phase3Data?.programs || []).filter((program) => {
      if (programFilter === 'verified') return program.all_verified;
      if (programFilter === 'needs_action') return !program.all_verified;
      return true;
    });
    if (!query) return programs;
    return programs.filter((program) => {
      const nameMatch = (program.program_name || '').toLowerCase().includes(query);
      const pendingMatch = (program.pending_assets || []).some((asset) =>
        (asset.asset_identifier || '').toLowerCase().includes(query)
      );
      return nameMatch || pendingMatch;
    });
  }, [phase3Data, programSearch, programFilter]);

  const programCounts = useMemo(() => {
    const programs = phase3Data?.programs || [];
    const verified = programs.filter((p) => p.all_verified).length;
    const needsAction = programs.length - verified;
    return { all: programs.length, verified, needsAction };
  }, [phase3Data]);

  async function handleStart() {
    if (!domain.trim()) {
      setError('Domain is required.');
      return;
    }
    setError(null);
    setSuccess(null);
    setIsStarting(true);
    try {
      const res = await api.post<StartResponse>('/domain/verify/start', {
        domain: domain.trim(),
        method,
      });
      setStartData(res.data);
      setSuccess('Verification challenge created. Complete setup then click Verify.');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to start domain verification.');
    } finally {
      setIsStarting(false);
    }
  }

  async function handlePhase1Submit() {
    if (!phase1.business_license_url || !phase1.tax_id || !phase1.legal_name) {
      setError('Business license URL, legal name, and tax ID are required.');
      return;
    }
    if (!phase1.attest_owns_assets || !phase1.attest_accepts_liability) {
      setError('Both legal attestations are required.');
      return;
    }
    setError(null);
    setSuccess(null);
    setPhase1Message(null);
    setIsSubmittingPhase1(true);
    try {
      const res = await api.post('/domain/verify/phase1', phase1);
      setPhase1Message(res.data?.message || 'Phase 1 submitted successfully.');
      await refetch();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to submit legal verification.');
    } finally {
      setIsSubmittingPhase1(false);
    }
  }

  async function handleVerify() {
    if (!domain.trim()) return;
    setError(null);
    setSuccess(null);
    setIsCompleting(true);
    try {
      const res = await api.post('/domain/verify/complete', {
        domain: domain.trim(),
        method,
      });
      setSuccess(res.data?.message || 'Domain verified successfully.');
      setStartData(null);
      await refetch();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Verification failed.');
    } finally {
      setIsCompleting(false);
    }
  }

  async function handleRunPhase4() {
    setError(null);
    setSuccess(null);
    setIsRunningPhase4(true);
    try {
      const res = await api.post('/domain/verify/phase4/reverify-now');
      const checked = res.data?.results?.checked ?? 0;
      const suspended = res.data?.results?.suspended ?? 0;
      setSuccess(`Phase 4 reverification completed. Checked ${checked} scopes; suspended ${suspended}.`);
      await Promise.all([refetch(), refetchPhase3()]);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to run phase 4 reverification.');
    } finally {
      setIsRunningPhase4(false);
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0F172A] p-6 text-[#F8FAFC]">
        <div className="mx-auto max-w-3xl rounded-xl border border-[#334155] bg-[#1E293B] p-6">
          <h2 className="text-lg font-semibold">Loading organization session...</h2>
          <p className="mt-2 text-sm text-[#94A3B8]">
            If this does not resolve, sign in again to refresh your organization profile.
          </p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      <PortalShell
        user={user}
        title="Domain Verification"
        subtitle="Verify organization ownership before publishing sensitive scope."
        navItems={getPortalNavItems(user.role)}
      >
        <div className="space-y-5">
          <button
            onClick={() => router.push('/organization/settings')}
            className="inline-flex items-center gap-1 rounded-md border border-[#334155] bg-[#0F172A] px-3 py-1.5 text-sm text-[#94A3B8] transition-colors hover:border-[#475569] hover:text-[#F8FAFC]"
          >
            ← Back to Settings
          </button>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-[#334155] bg-gradient-to-b from-[#1E293B] to-[#172033] p-4 shadow-[0_8px_24px_rgba(2,6,23,0.35)]">
              <p className="text-xs uppercase tracking-wide text-[#94A3B8]">Verification status</p>
              <p className="mt-1 text-lg font-semibold capitalize text-[#F8FAFC]">{data?.verification_status || 'pending'}</p>
              {data?.admin_approval_required && (
                <p className="mt-1 text-[11px] text-[#FDE68A]">Awaiting admin approval</p>
              )}
            </div>
            <div className="rounded-2xl border border-[#334155] bg-gradient-to-b from-[#1E293B] to-[#172033] p-4 shadow-[0_8px_24px_rgba(2,6,23,0.35)]">
              <p className="text-xs uppercase tracking-wide text-[#94A3B8]">Domain verified</p>
              <p className={`mt-1 text-lg font-semibold ${data?.domain_verified ? 'text-[#10B981]' : 'text-[#F59E0B]'}`}>
                {data?.domain_verified ? 'Yes' : 'No'}
              </p>
              {!data?.domain_verified && data?.admin_approval_required && (
                <p className="mt-1 text-[11px] text-[#FDE68A]">Proof submitted, waiting for admin confirmation.</p>
              )}
            </div>
            <div className="rounded-2xl border border-[#334155] bg-gradient-to-b from-[#1E293B] to-[#172033] p-4 shadow-[0_8px_24px_rgba(2,6,23,0.35)]">
              <p className="text-xs uppercase tracking-wide text-[#94A3B8]">Verified domains</p>
              <p className="mt-1 text-lg font-semibold text-[#F8FAFC]">{data?.verified_domains?.length || 0}</p>
              <p className="mt-1 text-[11px] text-[#94A3B8]">
                Domains currently attached to this organization as ownership-proven assets.
              </p>
            </div>
          </div>
          {data?.domain_verified && (data?.verified_domains?.length || 0) === 0 && (
            <div className="rounded-xl border border-[#7C2D12] bg-[#451A03]/40 p-3 text-xs text-[#FDBA74]">
              Domain verification is marked as true, but no domain list exists yet on organization profile.
              Re-run Phase 2 verification to attach the domain explicitly.
            </div>
          )}
          {data?.reconciled_verified_domains && (
            <div className="rounded-xl border border-[#065F46] bg-[#022C22]/40 p-3 text-xs text-[#A7F3D0]">
              Verified domains were reconciled from your organization website record to keep data consistent.
            </div>
          )}

          <div className="rounded-2xl border border-[#334155] bg-[#111827] p-5 shadow-[0_10px_30px_rgba(2,6,23,0.4)]">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-base font-semibold text-[#F8FAFC]">4-Phase Verification Workflow</h3>
              <span className="rounded-full border border-[#334155] bg-[#0B1220] px-3 py-1 text-[11px] text-[#94A3B8]">
                Industry-grade controls
              </span>
            </div>
            <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
              <div className="rounded-xl border border-[#334155] bg-[#1E293B] p-3 text-[#CBD5E1]">
                <p className="font-medium text-[#F8FAFC]">Phase 1 — Identity & Legal</p>
                <p className="mt-1 text-xs">Business registration URL, tax ID, legal name, and 2 liability attestations.</p>
              </div>
              <div className="rounded-xl border border-[#334155] bg-[#1E293B] p-3 text-[#CBD5E1]">
                <p className="font-medium text-[#F8FAFC]">Phase 2 — Domain Ownership</p>
                <p className="mt-1 text-xs">DNS TXT or HTTPS file challenge using unique token.</p>
              </div>
              <div className="rounded-xl border border-[#334155] bg-[#1E293B] p-3 text-[#CBD5E1]">
                <p className="font-medium text-[#F8FAFC]">Phase 3 — Scope Validation</p>
                <p className="mt-1 text-xs">Scope-level domain checks must pass before program publish.</p>
              </div>
              <div className="rounded-xl border border-[#334155] bg-[#1E293B] p-3 text-[#CBD5E1]">
                <p className="font-medium text-[#F8FAFC]">Phase 4 — Ongoing Monitoring</p>
                <p className="mt-1 text-xs">Reverification and audit trail enforce continued ownership integrity.</p>
              </div>
            </div>
            <div className="mt-3 rounded-xl border border-[#334155] bg-[#0B1220] p-3 text-xs text-[#CBD5E1]">
              <span className={data?.domain_verified ? 'text-[#10B981]' : 'text-[#F59E0B]'}>
                {data?.domain_verified
                  ? 'Phase 2 complete and admin-approved'
                  : data?.admin_approval_required
                  ? 'Phase 2 proof submitted; admin approval pending'
                  : 'Phase 2 pending'}
              </span>
              {' · '}
              <span className={phase3Data?.all_scopes_verified ? 'text-[#10B981]' : 'text-[#F59E0B]'}>
                {phase3Data?.all_scopes_verified ? 'Phase 3 publish-ready' : 'Phase 3 needs scope action'}
              </span>
            </div>
            {!!data?.verified_domains?.length && (
              <p className="mt-3 text-xs text-[#94A3B8]">Verified domains: {data.verified_domains.join(', ')}</p>
            )}
          </div>

          <div className="rounded-2xl border border-[#334155] bg-[#1E293B] p-5 shadow-[0_10px_30px_rgba(2,6,23,0.4)]">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-lg font-semibold text-[#F8FAFC]">Phase 1 — Identity & Legal Verification</h3>
              <span
                className={`rounded-full border px-3 py-1 text-[11px] ${
                  data?.phase1_submitted
                    ? 'border-[#065F46] bg-[#022C22]/40 text-[#A7F3D0]'
                    : 'border-[#7C2D12] bg-[#451A03]/40 text-[#FDBA74]'
                }`}
              >
                {data?.phase1_submitted ? 'Submitted' : 'Not Submitted'}
              </span>
            </div>
            <p className="mt-1 text-xs text-[#94A3B8]">
              Submit legal identity information and accept liability clauses before domain proof.
            </p>

            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <input
                value={phase1.legal_name}
                onChange={(e) => setPhase1((p) => ({ ...p, legal_name: e.target.value }))}
                placeholder="Official legal entity name"
                className="rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-[#F8FAFC] placeholder-[#64748B] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
              />
              <input
                value={phase1.tax_id}
                onChange={(e) => setPhase1((p) => ({ ...p, tax_id: e.target.value }))}
                placeholder="Tax ID / EIN / VAT"
                className="rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-[#F8FAFC] placeholder-[#64748B] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
              />
            </div>
            <input
              value={phase1.business_license_url}
              onChange={(e) => setPhase1((p) => ({ ...p, business_license_url: e.target.value }))}
              placeholder="Business registration document URL"
              className="mt-3 w-full rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-[#F8FAFC] placeholder-[#64748B] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
            />

            <div className="mt-3 space-y-2 rounded-xl border border-[#334155] bg-[#0B1220] p-3 text-sm text-[#CBD5E1]">
              <label className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={phase1.attest_owns_assets}
                  onChange={(e) => setPhase1((p) => ({ ...p, attest_owns_assets: e.target.checked }))}
                />
                <span>I confirm we own or are authorized to control every asset we will submit in scope.</span>
              </label>
              <label className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={phase1.attest_accepts_liability}
                  onChange={(e) => setPhase1((p) => ({ ...p, attest_accepts_liability: e.target.checked }))}
                />
                <span>I accept legal liability for unauthorized or fraudulent scope submissions.</span>
              </label>
            </div>

            <div className="mt-3">
              <Button onClick={handlePhase1Submit} isLoading={isSubmittingPhase1}>
                Submit Phase 1
              </Button>
            </div>
            {phase1Message && <p className="mt-2 text-sm text-[#10B981]">{phase1Message}</p>}
          </div>

          <div className="rounded-2xl border border-[#334155] bg-[#1E293B] p-5 shadow-[0_10px_30px_rgba(2,6,23,0.4)]">
            <h3 className="text-lg font-semibold text-[#F8FAFC]">Phase 2 — Domain Ownership Proof</h3>
            <p className="mt-1 text-xs text-[#94A3B8]">
              Use your organization website domain or a matching subdomain.
              {suggestedDomain ? ` Suggested: ${suggestedDomain}` : ''}
            </p>

            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder={suggestedDomain || 'example.com'}
                className="rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-[#F8FAFC] placeholder-[#64748B] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
              />
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as Method)}
                className="rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-[#F8FAFC] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
              >
                <option value="dns">DNS TXT</option>
                <option value="file">File-based</option>
              </select>
            </div>

            <div className="mt-3 flex gap-2">
              <Button onClick={handleStart} isLoading={isStarting}>
                Start Verification
              </Button>
              <Button variant="outline" onClick={handleVerify} isLoading={isCompleting} disabled={!startData}>
                Verify Now
              </Button>
            </div>

            {startData && (
              <pre className="mt-3 whitespace-pre-wrap rounded-xl border border-[#334155] bg-[#0B1220] p-3 text-xs leading-5 text-[#CBD5E1]">
                {startData.instructions}
              </pre>
            )}
            {error && <p className="mt-2 text-sm text-[#EF4444]">{error}</p>}
            {success && <p className="mt-2 text-sm text-[#10B981]">{success}</p>}
          </div>

          <div className="rounded-2xl border border-[#334155] bg-[#1E293B] p-5 shadow-[0_10px_30px_rgba(2,6,23,0.4)]">
            <h3 className="text-lg font-semibold text-[#F8FAFC]">Phase 3 — Scope Asset Validation</h3>
            <p className="mt-1 text-xs text-[#94A3B8]">
              Program publishing readiness is calculated from all verifiable scope assets.
            </p>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              <div className="rounded-xl border border-[#334155] bg-[#0B1220] p-3">
                <p className="text-[11px] uppercase tracking-wide text-[#94A3B8]">Programs</p>
                <p className="text-lg font-semibold text-[#F8FAFC]">{phase3Data?.total_programs ?? 0}</p>
              </div>
              <div className="rounded-xl border border-[#334155] bg-[#0B1220] p-3">
                <p className="text-[11px] uppercase tracking-wide text-[#94A3B8]">Verifiable scopes</p>
                <p className="text-lg font-semibold text-[#F8FAFC]">{phase3Data?.total_verifiable_scopes ?? 0}</p>
              </div>
              <div className="rounded-xl border border-[#334155] bg-[#0B1220] p-3">
                <p className="text-[11px] uppercase tracking-wide text-[#94A3B8]">Verified scopes</p>
                <p className="text-lg font-semibold text-[#10B981]">{phase3Data?.total_verified_scopes ?? 0}</p>
              </div>
            </div>

            <div className="mt-3">
              <input
                value={programSearch}
                onChange={(e) => setProgramSearch(e.target.value)}
                placeholder="Search programs or pending asset domains..."
                className="w-full rounded-xl border border-[#475569] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] placeholder-[#64748B] transition-colors focus:border-[#3B82F6] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
              />
            </div>

            <div className="mt-2 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setProgramFilter('all')}
                className={`rounded-full border px-3 py-1 text-xs ${
                  programFilter === 'all'
                    ? 'border-[#3B82F6] bg-[#1D4ED8]/20 text-[#BFDBFE]'
                    : 'border-[#475569] bg-[#0B1220] text-[#CBD5E1]'
                }`}
              >
                All ({programCounts.all})
              </button>
              <button
                type="button"
                onClick={() => setProgramFilter('verified')}
                className={`rounded-full border px-3 py-1 text-xs ${
                  programFilter === 'verified'
                    ? 'border-[#10B981] bg-[#065F46]/30 text-[#A7F3D0]'
                    : 'border-[#475569] bg-[#0B1220] text-[#CBD5E1]'
                }`}
              >
                Fully Verified ({programCounts.verified})
              </button>
              <button
                type="button"
                onClick={() => setProgramFilter('needs_action')}
                className={`rounded-full border px-3 py-1 text-xs ${
                  programFilter === 'needs_action'
                    ? 'border-[#F59E0B] bg-[#78350F]/35 text-[#FDE68A]'
                    : 'border-[#475569] bg-[#0B1220] text-[#CBD5E1]'
                }`}
              >
                Needs Action ({programCounts.needsAction})
              </button>
            </div>

            <div className="mt-3 space-y-2">
              {(showAllPrograms ? filteredPrograms : filteredPrograms.slice(0, 4)).map((program) => (
                <div key={program.program_id} className="rounded-xl border border-[#334155] bg-[#0B1220] p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-[#F8FAFC]">{program.program_name}</p>
                    <span className={`text-xs ${program.all_verified ? 'text-[#10B981]' : 'text-[#F59E0B]'}`}>
                      {program.verified_scope_count}/{program.verifiable_scope_count} verified
                    </span>
                  </div>
                  {!program.all_verified && program.pending_assets.length > 0 && (
                    <p className="mt-1 text-xs text-[#CBD5E1]">
                      Pending: {program.pending_assets.slice(0, 2).map((x) => x.asset_identifier).join(', ')}
                      {program.pending_assets.length > 2 ? ' ...' : ''}
                    </p>
                  )}
                  <div className="mt-2">
                    <Button
                      variant="outline"
                      onClick={() => router.push(`/organization/programs/${program.program_id}/verification`)}
                    >
                      Open Program Verification →
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            {filteredPrograms.length === 0 && (
              <p className="mt-2 text-xs text-[#94A3B8]">No programs matched your search.</p>
            )}
            {filteredPrograms.length > 4 && (
              <div className="mt-3">
                <Button variant="outline" onClick={() => setShowAllPrograms((v) => !v)}>
                  {showAllPrograms
                    ? 'Show less'
                    : `Show all programs (${filteredPrograms.length})`}
                </Button>
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-[#334155] bg-[#1E293B] p-5 shadow-[0_10px_30px_rgba(2,6,23,0.4)]">
            <h3 className="text-lg font-semibold text-[#F8FAFC]">Phase 4 — Ongoing Monitoring</h3>
            <p className="mt-1 text-xs text-[#94A3B8]">
              Run reverification sweep to confirm previously verified assets still prove ownership.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Button onClick={handleRunPhase4} isLoading={isRunningPhase4}>
                Run Reverification Now
              </Button>
              <Button variant="outline" onClick={() => refetchPhase3()}>
                Refresh Phase 3 Data
              </Button>
            </div>
            <p className="mt-2 text-xs text-[#94A3B8]">
              For automatic monitoring, keep APScheduler enabled in your backend deployment.
            </p>
          </div>
        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
