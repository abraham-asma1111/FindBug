'use client';

/**
 * Standalone Domain Verification Management Page
 * Route: /organization/programs/[id]/verification
 *
 * Shows all scopes for a program and lets the organization verify each one
 * independently without having to be inside the ProgramDetailModal.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import VerificationStatusBadge from '@/components/organization/programs/VerificationStatusBadge';
import ScopeVerificationWizard from '@/components/organization/programs/ScopeVerificationWizard';

// ─── Types ────────────────────────────────────────────────────────────────────

interface ScopeVerificationEntry {
  scope_id: string;
  asset_type: string;
  asset_identifier: string;
  needs_verification: boolean;
  verification_status: string;
  verified_at?: string;
  method?: string;
}

interface ProgramVerificationSummary {
  all_verified: boolean;
  scopes: ScopeVerificationEntry[];
}

interface ProgramInfo {
  id: string;
  name: string;
  status: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';
const API_BASE = RAW_API_BASE.endsWith('/api/v1')
  ? RAW_API_BASE
  : `${RAW_API_BASE.replace(/\/$/, '')}/api/v1`;

async function apiFetch<T>(path: string): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function ProgramVerificationPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params?.id as string;

  const [summary, setSummary] = useState<ProgramVerificationSummary | null>(null);
  const [program, setProgram] = useState<ProgramInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeWizard, setActiveWizard] = useState<{ id: string; domain: string } | null>(null);

  const loadData = useCallback(async () => {
    if (!programId) return;
    setLoading(true);
    setError(null);
    try {
      const [prog, verSummary] = await Promise.all([
        apiFetch<ProgramInfo>(`/programs/${programId}`),
        apiFetch<ProgramVerificationSummary>(`/programs/${programId}/verification-status`),
      ]);
      setProgram(prog);
      setSummary(verSummary);
    } catch (e: any) {
      setError(e.message || 'Failed to load verification data');
    } finally {
      setLoading(false);
    }
  }, [programId]);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Render ─────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={s.page}>
        <div style={s.spinner} />
        <p style={{ color: '#64748b', marginTop: 20 }}>Loading verification status…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={s.page}>
        <div style={s.errorBox}>
          <p style={{ color: '#fca5a5', margin: 0 }}>⚠ {error}</p>
        </div>
      </div>
    );
  }

  const verifiableScopes = summary?.scopes?.filter(s => s.needs_verification) ?? [];
  const nonVerifiable    = summary?.scopes?.filter(s => !s.needs_verification) ?? [];
  const verifiedCount    = verifiableScopes.filter(s => s.verification_status === 'verified').length;

  return (
    <>
      <div style={s.page}>
        {/* ── Header ── */}
        <div style={s.header}>
          <button onClick={() => router.back()} style={s.backBtn}>← Back</button>
          <div>
            <h1 style={s.heading}>🔐 Domain Verification</h1>
            <p style={s.subheading}>
              Program: <strong style={{ color: '#e2e8f0' }}>{program?.name}</strong>
              {' · '}
              <span style={{ color: program?.status === 'draft' ? '#f59e0b' : '#10b981' }}>
                {program?.status}
              </span>
            </p>
          </div>
        </div>

        {/* ── Overall status bar ── */}
        <div style={{
          ...s.statusBar,
          background: summary?.all_verified ? 'rgba(16,185,129,0.1)' : 'rgba(99,102,241,0.08)',
          borderColor: summary?.all_verified ? 'rgba(16,185,129,0.3)' : 'rgba(99,102,241,0.25)',
        }}>
          {summary?.all_verified ? (
            <span style={{ color: '#10b981', fontWeight: 700 }}>
              ✅ All verifiable scopes are verified — program can be published.
            </span>
          ) : (
            <span style={{ color: '#818cf8', fontWeight: 700 }}>
              🔐 {verifiedCount} / {verifiableScopes.length} scopes verified
              {program?.status === 'draft' && ' — verify all scopes to enable publishing.'}
            </span>
          )}
        </div>

        {/* ── Verifiable scopes ── */}
        {verifiableScopes.length > 0 && (
          <section style={s.section}>
            <h2 style={s.sectionTitle}>Scopes Requiring Verification</h2>
            <div style={s.grid}>
              {verifiableScopes.map(scope => (
                <div key={scope.scope_id} style={s.card}>
                  <div style={s.cardHeader}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={s.assetType}>{scope.asset_type.replace('_', ' ')}</span>
                        <VerificationStatusBadge status={scope.verification_status as any} size="sm" />
                      </div>
                      <p style={s.domain}>{scope.asset_identifier}</p>
                      {scope.verified_at && (
                        <p style={s.verifiedAt}>
                          ✓ Verified on {new Date(scope.verified_at).toLocaleDateString()}
                          {scope.method && ` via ${scope.method.replace('_', ' ')}`}
                        </p>
                      )}
                    </div>
                    {scope.verification_status !== 'verified' && (
                      <button
                        onClick={() => setActiveWizard({ id: scope.scope_id, domain: scope.asset_identifier })}
                        style={s.verifyBtn}
                      >
                        {scope.verification_status === 'failed' || scope.verification_status === 'expired'
                          ? '🔄 Retry'
                          : scope.verification_status === 'pending'
                          ? '▶ Run Check'
                          : '🔐 Start Verification'}
                      </button>
                    )}
                    {scope.verification_status === 'verified' && (
                      <div style={s.verifiedCheck}>✓</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Non-verifiable scopes ── */}
        {nonVerifiable.length > 0 && (
          <section style={s.section}>
            <h2 style={{ ...s.sectionTitle, color: '#475569' }}>
              Other Scopes (No Verification Required)
            </h2>
            <div style={s.grid}>
              {nonVerifiable.map(scope => (
                <div key={scope.scope_id} style={{ ...s.card, opacity: 0.6 }}>
                  <span style={s.assetType}>{scope.asset_type.replace('_', ' ')}</span>
                  <p style={s.domain}>{scope.asset_identifier}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Empty state ── */}
        {(summary?.scopes?.length ?? 0) === 0 && (
          <div style={s.emptyState}>
            <p style={{ fontSize: 40, marginBottom: 12 }}>📋</p>
            <p style={{ color: '#64748b', fontSize: 15 }}>
              No scopes found for this program. Add scopes first.
            </p>
            <button
              onClick={() => router.push(`/organization/programs`)}
              style={s.verifyBtn}
            >
              Go to Programs
            </button>
          </div>
        )}
      </div>

      {/* ── Verification Wizard Overlay ── */}
      {activeWizard && (
        <ScopeVerificationWizard
          scopeId={activeWizard.id}
          domain={activeWizard.domain}
          onClose={() => {
            setActiveWizard(null);
            loadData();
          }}
          onVerified={() => {
            setActiveWizard(null);
            loadData();
          }}
        />
      )}
    </>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const s = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    padding: '40px 24px',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: 28,
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  header: {
    width: '100%',
    maxWidth: 800,
    display: 'flex',
    alignItems: 'flex-start',
    gap: 20,
  },
  backBtn: {
    background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    color: '#94a3b8',
    borderRadius: 8,
    padding: '8px 16px',
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: 600,
    whiteSpace: 'nowrap' as const,
    marginTop: 6,
  },
  heading: {
    color: '#f1f5f9',
    fontSize: 26,
    fontWeight: 800,
    margin: '0 0 4px',
  },
  subheading: {
    color: '#64748b',
    fontSize: 14,
    margin: 0,
  },
  statusBar: {
    width: '100%',
    maxWidth: 800,
    borderRadius: 12,
    border: '1px solid',
    padding: '14px 20px',
    fontSize: 14,
  },
  section: {
    width: '100%',
    maxWidth: 800,
  },
  sectionTitle: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase' as const,
    marginBottom: 14,
  },
  grid: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 12,
  },
  card: {
    background: 'rgba(30,41,59,0.7)',
    border: '1px solid rgba(99,102,241,0.15)',
    borderRadius: 14,
    padding: '18px 20px',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 16,
  },
  assetType: {
    fontSize: 12,
    fontWeight: 700,
    color: '#64748b',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.06em',
    textDecoration: 'none',
  } as React.CSSProperties,
  domain: {
    color: '#e2e8f0',
    fontSize: 15,
    fontWeight: 600,
    margin: '2px 0 0',
    wordBreak: 'break-all' as const,
  },
  verifiedAt: {
    color: '#10b981',
    fontSize: 11,
    marginTop: 4,
    margin: '4px 0 0',
  },
  verifyBtn: {
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    padding: '8px 18px',
    fontSize: 12,
    fontWeight: 700,
    cursor: 'pointer',
    whiteSpace: 'nowrap' as const,
    boxShadow: '0 4px 14px rgba(99,102,241,0.3)',
    flexShrink: 0,
  },
  verifiedCheck: {
    width: 36,
    height: 36,
    borderRadius: '50%',
    background: 'rgba(16,185,129,0.15)',
    border: '2px solid rgba(16,185,129,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#10b981',
    fontWeight: 900,
    fontSize: 18,
    flexShrink: 0,
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '60px 0',
  },
  spinner: {
    width: 48,
    height: 48,
    border: '4px solid rgba(99,102,241,0.15)',
    borderTop: '4px solid #6366f1',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    margin: '0 auto',
  } as React.CSSProperties,
  errorBox: {
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 10,
    padding: '14px 18px',
    maxWidth: 500,
  },
} as const;
