'use client';

import React from 'react';

export type VerificationStatusType =
  | 'unverified'
  | 'pending'
  | 'verified'
  | 'failed'
  | 'suspended'
  | 'expired';

interface Props {
  status: VerificationStatusType | string;
  size?: 'sm' | 'md';
  showLabel?: boolean;
}

const CONFIG: Record<string, { label: string; icon: string; bg: string; text: string; border: string; pulse?: boolean }> = {
  verified: {
    label: 'Verified',
    icon: '✓',
    bg: 'rgba(16,185,129,0.12)',
    text: '#10b981',
    border: 'rgba(16,185,129,0.35)',
  },
  pending: {
    label: 'Pending',
    icon: '⏳',
    bg: 'rgba(245,158,11,0.12)',
    text: '#f59e0b',
    border: 'rgba(245,158,11,0.35)',
    pulse: true,
  },
  failed: {
    label: 'Failed',
    icon: '✗',
    bg: 'rgba(239,68,68,0.12)',
    text: '#ef4444',
    border: 'rgba(239,68,68,0.35)',
  },
  suspended: {
    label: 'Suspended',
    icon: '⚠',
    bg: 'rgba(249,115,22,0.12)',
    text: '#f97316',
    border: 'rgba(249,115,22,0.35)',
  },
  expired: {
    label: 'Expired',
    icon: '⌛',
    bg: 'rgba(107,114,128,0.12)',
    text: '#6b7280',
    border: 'rgba(107,114,128,0.35)',
  },
  unverified: {
    label: 'Unverified',
    icon: '○',
    bg: 'rgba(107,114,128,0.08)',
    text: '#9ca3af',
    border: 'rgba(107,114,128,0.25)',
  },
};

export default function VerificationStatusBadge({
  status,
  size = 'md',
  showLabel = true,
}: Props) {
  const cfg = CONFIG[status] ?? CONFIG.unverified;
  const isSmall = size === 'sm';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: isSmall ? 4 : 6,
        padding: isSmall ? '2px 8px' : '4px 12px',
        borderRadius: 999,
        border: `1px solid ${cfg.border}`,
        background: cfg.bg,
        color: cfg.text,
        fontSize: isSmall ? 11 : 12,
        fontWeight: 600,
        letterSpacing: '0.02em',
        whiteSpace: 'nowrap',
        animation: cfg.pulse ? 'pulse-badge 2s ease-in-out infinite' : undefined,
      }}
    >
      <span style={{ fontSize: isSmall ? 10 : 12 }}>{cfg.icon}</span>
      {showLabel && <span>{cfg.label}</span>}
      <style>{`
        @keyframes pulse-badge {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.65; }
        }
      `}</style>
    </span>
  );
}
