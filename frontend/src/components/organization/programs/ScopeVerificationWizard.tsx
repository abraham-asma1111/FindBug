'use client';

import React, { useState, useCallback } from 'react';
import VerificationStatusBadge, { VerificationStatusType } from './VerificationStatusBadge';

// ── Types ────────────────────────────────────────────────────────────────────

interface VerificationRecord {
  id?: string;
  scope_id: string;
  domain: string;
  root_domain: string;
  verification_method: string;
  verification_status: string;
  verification_token?: string;
  verified_at?: string;
  expires_at?: string;
  attempt_count?: number;
  failure_reason?: string;
  dns_record_name?: string;
  dns_record_value?: string;
  file_verification_url?: string;
  instructions?: {
    method: string;
    steps: string[];
    record_name?: string;
    record_type?: string;
    record_value?: string;
    file_url?: string;
    file_content?: string;
    expires_in?: string;
  };
}

interface Props {
  scopeId: string;
  domain: string;
  existingRecord?: VerificationRecord | null;
  onClose: () => void;
  onVerified?: () => void;
}

type WizardStep = 'method' | 'instructions' | 'checking' | 'result';

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';
const API_BASE = RAW_API_BASE.endsWith('/api/v1')
  ? RAW_API_BASE
  : `${RAW_API_BASE.replace(/\/$/, '')}/api/v1`;

async function apiPost<T>(path: string, body?: object): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ── Sub-components ────────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button
      onClick={copy}
      style={{
        padding: '4px 10px',
        background: copied ? 'rgba(16,185,129,0.15)' : 'rgba(99,102,241,0.12)',
        border: `1px solid ${copied ? 'rgba(16,185,129,0.4)' : 'rgba(99,102,241,0.3)'}`,
        borderRadius: 6,
        color: copied ? '#10b981' : '#818cf8',
        fontSize: 11,
        fontWeight: 600,
        cursor: 'pointer',
        transition: 'all 0.2s',
      }}
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

function CodeBlock({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 4, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        background: 'rgba(15,23,42,0.6)',
        border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: 8,
        padding: '10px 14px',
      }}>
        <code style={{ flex: 1, fontFamily: 'monospace', fontSize: 13, color: '#e2e8f0', wordBreak: 'break-all' }}>
          {value}
        </code>
        <CopyButton text={value} />
      </div>
    </div>
  );
}

// ── Wizard ────────────────────────────────────────────────────────────────────

export default function ScopeVerificationWizard({ scopeId, domain, existingRecord, onClose, onVerified }: Props) {
  const [step, setStep] = useState<WizardStep>(existingRecord && existingRecord.verification_status !== 'unverified' ? 'instructions' : 'method');
  const [method, setMethod] = useState<'dns_txt' | 'file_based'>(
    (existingRecord?.verification_method as any) || 'dns_txt'
  );
  const [record, setRecord] = useState<VerificationRecord | null>(existingRecord || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInitiate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost<VerificationRecord>(`/scopes/${scopeId}/verification/initiate`, { method });
      setRecord(data);
      setStep('instructions');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [scopeId, method]);

  const handleCheck = useCallback(async () => {
    setStep('checking');
    setError(null);
    try {
      const data = await apiPost<VerificationRecord>(`/scopes/${scopeId}/verification/check`);
      setRecord(data);
      setStep('result');
      if (data.verification_status === 'verified' && onVerified) {
        onVerified();
      }
    } catch (e: any) {
      setError(e.message);
      setStep('result');
    }
  }, [scopeId, onVerified]);

  const handleRegenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost<VerificationRecord>(`/scopes/${scopeId}/verification/regenerate`, { method });
      setRecord(data);
      setStep('instructions');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [scopeId, method]);

  const s = styles;

  return (
    <div style={s.overlay}>
      <div style={s.modal}>
        {/* Header */}
        <div style={s.header}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
              <span style={s.headerIcon}>🔐</span>
              <h2 style={s.title}>Domain Verification</h2>
            </div>
            <p style={s.subtitle}>Prove ownership of <strong style={{ color: '#e2e8f0' }}>{domain}</strong></p>
          </div>
          {record && (
            <VerificationStatusBadge status={record.verification_status as VerificationStatusType} />
          )}
        </div>

        {/* Progress dots */}
        <div style={s.progressRow}>
          {(['method', 'instructions', 'result'] as const).map((s2, i) => (
            <React.Fragment key={s2}>
              <div style={{
                ...s.dot,
                background: step === s2 ? '#6366f1' : (i < ['method','instructions','result'].indexOf(step) ? '#10b981' : 'rgba(255,255,255,0.1)'),
              }} />
              {i < 2 && <div style={s.dotLine} />}
            </React.Fragment>
          ))}
        </div>

        {/* ── Step: Method Selection ── */}
        {step === 'method' && (
          <div style={s.body}>
            <p style={s.desc}>Choose how to verify domain ownership:</p>
            <div style={s.methodGrid}>
              {/* DNS TXT */}
              <button
                onClick={() => setMethod('dns_txt')}
                style={{ ...s.methodCard, ...(method === 'dns_txt' ? s.methodCardActive : {}) }}
              >
                <div style={s.methodIcon}>🌐</div>
                <div style={s.methodName}>DNS TXT Record</div>
                <div style={s.methodDesc}>Add a TXT record to your domain's DNS. Works with any DNS provider.</div>
                <div style={s.methodBadge}>Recommended</div>
              </button>
              {/* File */}
              <button
                onClick={() => setMethod('file_based')}
                style={{ ...s.methodCard, ...(method === 'file_based' ? s.methodCardActive : {}) }}
              >
                <div style={s.methodIcon}>📄</div>
                <div style={s.methodName}>File Upload</div>
                <div style={s.methodDesc}>Place a verification file at a well-known URL on your web server.</div>
                <div style={s.methodBadge}>Alternative</div>
              </button>
            </div>
            {error && <div style={s.error}>{error}</div>}
            <div style={s.footer}>
              <button onClick={onClose} style={s.btnSecondary}>Cancel</button>
              <button onClick={handleInitiate} disabled={loading} style={s.btnPrimary}>
                {loading ? 'Generating token…' : 'Continue →'}
              </button>
            </div>
          </div>
        )}

        {/* ── Step: Instructions ── */}
        {step === 'instructions' && record && (
          <div style={s.body}>
            {method === 'dns_txt' || record.verification_method === 'dns_txt' ? (
              <>
                <p style={s.desc}>Add this TXT record to your DNS provider for <strong>{record.root_domain}</strong>:</p>
                <div style={s.infoBox}>
                  <CodeBlock label="Host / Name" value={record.dns_record_name || record.root_domain} />
                  <CodeBlock label="Type" value="TXT" />
                  <CodeBlock label="Value" value={record.dns_record_value || `ptaas-verification=${record.verification_token}`} />
                  <CodeBlock label="TTL" value="300 (5 minutes)" />
                </div>
                <div style={s.tipBox}>
                  <span style={{ color: '#f59e0b', marginRight: 6 }}>⚠</span>
                  DNS changes can take up to 24–48 hours to propagate globally. Once added, click <strong>Run Verification</strong>.
                </div>
              </>
            ) : (
              <>
                <p style={s.desc}>Create this file on your web server (HTTPS required):</p>
                <div style={s.infoBox}>
                  <CodeBlock label="File URL" value={record.file_verification_url || `https://${record.root_domain}/.well-known/ptaas-verification.txt`} />
                  <CodeBlock label="File Content (exact)" value={record.verification_token || ''} />
                </div>
                <div style={s.tipBox}>
                  <span style={{ color: '#f59e0b', marginRight: 6 }}>⚠</span>
                  The file must be accessible via HTTPS, return HTTP 200, and contain <strong>only</strong> the token.
                </div>
              </>
            )}

            <div style={{ ...s.infoBox, marginTop: 8, fontSize: 12, color: '#64748b' }}>
              Token expires in <strong style={{ color: '#94a3b8' }}>48 hours</strong>. Don't see the record? Try regenerating the token.
            </div>

            {error && <div style={s.error}>{error}</div>}

            <div style={s.footer}>
              <button onClick={handleRegenerate} disabled={loading} style={s.btnSecondary}>
                🔄 Regenerate Token
              </button>
              <button onClick={handleCheck} style={s.btnPrimary}>
                ▶ Run Verification
              </button>
            </div>
          </div>
        )}

        {/* ── Step: Checking ── */}
        {step === 'checking' && (
          <div style={{ ...s.body, textAlign: 'center', padding: '48px 32px' }}>
            <div style={s.spinner} />
            <p style={{ color: '#94a3b8', marginTop: 20, fontSize: 15 }}>
              {method === 'dns_txt' ? 'Looking up DNS TXT records…' : 'Fetching verification file…'}
            </p>
            <p style={{ color: '#475569', fontSize: 13, marginTop: 8 }}>This may take a few seconds.</p>
          </div>
        )}

        {/* ── Step: Result ── */}
        {step === 'result' && record && (
          <div style={s.body}>
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              {record.verification_status === 'verified' ? (
                <>
                  <div style={{ fontSize: 56, marginBottom: 12 }}>✅</div>
                  <h3 style={{ color: '#10b981', fontSize: 20, fontWeight: 700, margin: '0 0 8px' }}>Domain Verified!</h3>
                  <p style={{ color: '#64748b', fontSize: 14 }}>
                    <strong style={{ color: '#e2e8f0' }}>{record.domain}</strong> ownership confirmed.
                    Your program can now be published.
                  </p>
                </>
              ) : (
                <>
                  <div style={{ fontSize: 56, marginBottom: 12 }}>❌</div>
                  <h3 style={{ color: '#ef4444', fontSize: 20, fontWeight: 700, margin: '0 0 8px' }}>Verification Failed</h3>
                  <div style={s.failBox}>
                    <p style={{ color: '#fca5a5', fontSize: 13, margin: 0 }}>{error || record.failure_reason || 'Verification check failed.'}</p>
                  </div>
                  <p style={{ color: '#64748b', fontSize: 13, marginTop: 12 }}>
                    Attempts: <strong style={{ color: '#94a3b8' }}>{record.attempt_count}</strong> of 5 per hour allowed.
                  </p>
                </>
              )}
            </div>

            <div style={s.footer}>
              {record.verification_status === 'verified' ? (
                <button onClick={onClose} style={s.btnPrimary}>Done ✓</button>
              ) : (
                <>
                  <button onClick={() => setStep('instructions')} style={s.btnSecondary}>← Back to Instructions</button>
                  <button onClick={handleRegenerate} style={s.btnSecondary}>🔄 New Token</button>
                  <button onClick={handleCheck} style={s.btnPrimary}>Retry ▶</button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: {
    position: 'fixed' as const,
    inset: 0,
    background: 'rgba(0,0,0,0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: 20,
  },
  modal: {
    background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: 20,
    width: '100%',
    maxWidth: 560,
    boxShadow: '0 24px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.1)',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    padding: '24px 28px 0',
  },
  headerIcon: { fontSize: 24 },
  title: {
    color: '#f1f5f9',
    fontSize: 20,
    fontWeight: 700,
    margin: 0,
  },
  subtitle: { color: '#64748b', fontSize: 13, margin: 0 },
  progressRow: {
    display: 'flex',
    alignItems: 'center',
    padding: '16px 28px 0',
    gap: 0,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: '50%',
    transition: 'background 0.3s',
  },
  dotLine: {
    flex: 1,
    height: 1,
    background: 'rgba(255,255,255,0.08)',
  },
  body: { padding: '20px 28px 28px' },
  desc: { color: '#94a3b8', fontSize: 14, marginBottom: 20 },
  infoBox: {
    background: 'rgba(15,23,42,0.5)',
    border: '1px solid rgba(99,102,241,0.15)',
    borderRadius: 12,
    padding: '16px 18px',
    marginBottom: 12,
  },
  tipBox: {
    background: 'rgba(245,158,11,0.08)',
    border: '1px solid rgba(245,158,11,0.2)',
    borderRadius: 8,
    padding: '10px 14px',
    fontSize: 13,
    color: '#94a3b8',
    marginBottom: 12,
  },
  failBox: {
    background: 'rgba(239,68,68,0.08)',
    border: '1px solid rgba(239,68,68,0.2)',
    borderRadius: 10,
    padding: '14px 16px',
    marginTop: 12,
    textAlign: 'left' as const,
  },
  methodGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
    marginBottom: 20,
  },
  methodCard: {
    background: 'rgba(30,41,59,0.6)',
    border: '2px solid rgba(99,102,241,0.1)',
    borderRadius: 14,
    padding: '20px 16px',
    cursor: 'pointer',
    textAlign: 'left' as const,
    transition: 'all 0.2s',
    outline: 'none',
  },
  methodCardActive: {
    border: '2px solid #6366f1',
    background: 'rgba(99,102,241,0.1)',
  },
  methodIcon: { fontSize: 28, marginBottom: 10 },
  methodName: { color: '#e2e8f0', fontWeight: 700, fontSize: 14, marginBottom: 6 },
  methodDesc: { color: '#64748b', fontSize: 12, lineHeight: 1.5, marginBottom: 10 },
  methodBadge: {
    display: 'inline-block',
    background: 'rgba(99,102,241,0.15)',
    color: '#818cf8',
    fontSize: 10,
    fontWeight: 700,
    borderRadius: 4,
    padding: '2px 8px',
    letterSpacing: '0.04em',
  },
  footer: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 10,
    marginTop: 20,
    flexWrap: 'wrap' as const,
  },
  btnPrimary: {
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#fff',
    border: 'none',
    borderRadius: 10,
    padding: '10px 22px',
    fontWeight: 700,
    fontSize: 14,
    cursor: 'pointer',
    boxShadow: '0 4px 16px rgba(99,102,241,0.3)',
  },
  btnSecondary: {
    background: 'rgba(255,255,255,0.05)',
    color: '#94a3b8',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 10,
    padding: '10px 18px',
    fontWeight: 600,
    fontSize: 13,
    cursor: 'pointer',
  },
  error: {
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.25)',
    borderRadius: 8,
    color: '#fca5a5',
    padding: '10px 14px',
    fontSize: 13,
    marginBottom: 12,
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
} as const;
