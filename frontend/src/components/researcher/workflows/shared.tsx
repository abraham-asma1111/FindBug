'use client';

import type { ReactNode } from 'react';
import { formatCurrency, formatDateTime } from '@/lib/portal';

export interface WorkflowStep {
  label: string;
  detail: string;
  state?: 'complete' | 'active' | 'upcoming';
}

export type WorkflowTone = 'blue' | 'emerald' | 'indigo' | 'rose' | 'slate';

interface WorkflowToneStyles {
  accentBar: string;
  accentGlow: string;
  accentText: string;
  accentSoft: string;
  accentBorder: string;
  selectedSurface: string;
  hoverSurface: string;
  tabActive: string;
  tabIdle: string;
}

const workflowToneMap: Record<WorkflowTone, WorkflowToneStyles> = {
  blue: {
    accentBar: 'bg-[linear-gradient(90deg,#0f4c81_0%,#4ab3e6_100%)]',
    accentGlow: 'bg-[radial-gradient(circle_at_center,rgba(74,179,230,0.85),rgba(15,76,129,0.18)_40%,transparent_72%)]',
    accentText: 'text-[#0f4c81]',
    accentSoft: 'bg-[#edf7fe]',
    accentBorder: 'border-[#b8d9ef]',
    selectedSurface: 'border-[#8cc5e8] bg-[linear-gradient(180deg,#ffffff_0%,#f2f9fe_100%)] shadow-[0_18px_42px_rgba(15,76,129,0.14)]',
    hoverSurface: 'hover:border-[#b8d9ef] hover:bg-[#f7fbfe]',
    tabActive: 'bg-[#0f4c81] text-white shadow-[0_10px_24px_rgba(15,76,129,0.22)]',
    tabIdle: 'text-[#4d5b6d] hover:bg-[#edf7fe] hover:text-[#0f4c81]',
  },
  emerald: {
    accentBar: 'bg-[linear-gradient(90deg,#0f6b46_0%,#41c58a_100%)]',
    accentGlow: 'bg-[radial-gradient(circle_at_center,rgba(90,211,155,0.85),rgba(15,107,70,0.18)_40%,transparent_72%)]',
    accentText: 'text-[#0f6b46]',
    accentSoft: 'bg-[#effbf5]',
    accentBorder: 'border-[#bde4cf]',
    selectedSurface: 'border-[#93d7b2] bg-[linear-gradient(180deg,#ffffff_0%,#f1fbf5_100%)] shadow-[0_18px_42px_rgba(15,107,70,0.12)]',
    hoverSurface: 'hover:border-[#bde4cf] hover:bg-[#f8fdf9]',
    tabActive: 'bg-[#0f6b46] text-white shadow-[0_10px_24px_rgba(15,107,70,0.2)]',
    tabIdle: 'text-[#4d5b6d] hover:bg-[#effbf5] hover:text-[#0f6b46]',
  },
  indigo: {
    accentBar: 'bg-[linear-gradient(90deg,#243b7b_0%,#5f7cff_100%)]',
    accentGlow: 'bg-[radial-gradient(circle_at_center,rgba(95,124,255,0.85),rgba(36,59,123,0.18)_40%,transparent_72%)]',
    accentText: 'text-[#243b7b]',
    accentSoft: 'bg-[#eef2ff]',
    accentBorder: 'border-[#c6d2ff]',
    selectedSurface: 'border-[#9fb4ff] bg-[linear-gradient(180deg,#ffffff_0%,#f3f6ff_100%)] shadow-[0_18px_42px_rgba(36,59,123,0.14)]',
    hoverSurface: 'hover:border-[#c6d2ff] hover:bg-[#f8f9ff]',
    tabActive: 'bg-[#243b7b] text-white shadow-[0_10px_24px_rgba(36,59,123,0.22)]',
    tabIdle: 'text-[#4d5b6d] hover:bg-[#eef2ff] hover:text-[#243b7b]',
  },
  rose: {
    accentBar: 'bg-[linear-gradient(90deg,#9f1239_0%,#fb7185_100%)]',
    accentGlow: 'bg-[radial-gradient(circle_at_center,rgba(251,113,133,0.85),rgba(159,18,57,0.18)_40%,transparent_72%)]',
    accentText: 'text-[#9f1239]',
    accentSoft: 'bg-[#fff1f4]',
    accentBorder: 'border-[#f5bfd0]',
    selectedSurface: 'border-[#f49db6] bg-[linear-gradient(180deg,#ffffff_0%,#fff5f7_100%)] shadow-[0_18px_42px_rgba(159,18,57,0.14)]',
    hoverSurface: 'hover:border-[#f5bfd0] hover:bg-[#fff8f9]',
    tabActive: 'bg-[#9f1239] text-white shadow-[0_10px_24px_rgba(159,18,57,0.22)]',
    tabIdle: 'text-[#4d5b6d] hover:bg-[#fff1f4] hover:text-[#9f1239]',
  },
  slate: {
    accentBar: 'bg-[linear-gradient(90deg,#0f172a_0%,#475569_100%)]',
    accentGlow: 'bg-[radial-gradient(circle_at_center,rgba(148,163,184,0.8),rgba(15,23,42,0.18)_40%,transparent_72%)]',
    accentText: 'text-[#0f172a]',
    accentSoft: 'bg-[#f5f7fa]',
    accentBorder: 'border-[#d6dee7]',
    selectedSurface: 'border-[#c7d2de] bg-[linear-gradient(180deg,#ffffff_0%,#f7f9fb_100%)] shadow-[0_18px_42px_rgba(15,23,42,0.1)]',
    hoverSurface: 'hover:border-[#d6dee7] hover:bg-[#fafbfd]',
    tabActive: 'bg-[#0f172a] text-white shadow-[0_10px_24px_rgba(15,23,42,0.18)]',
    tabIdle: 'text-[#4d5b6d] hover:bg-[#f5f7fa] hover:text-[#0f172a]',
  },
};

function getWorkflowToneStyles(tone: WorkflowTone): WorkflowToneStyles {
  return workflowToneMap[tone];
}

export function formatStatusLabel(value?: string | null): string {
  if (!value) {
    return 'Not available';
  }

  return value
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function formatWorkflowDate(value?: string | null, fallback = 'Not scheduled'): string {
  if (!value) {
    return fallback;
  }

  return formatDateTime(value);
}

export function formatWorkflowMoney(value?: number | string | null, fallback = 'Not disclosed'): string {
  if (value === null || value === undefined || value === '') {
    return fallback;
  }

  return formatCurrency(Number(value));
}

export function toLines(value?: string | null): string[] {
  if (!value) {
    return [];
  }

  return value
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export function toList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((entry) => String(entry)).filter(Boolean);
  }

  if (typeof value === 'string') {
    return toLines(value);
  }

  return [];
}

export function stringifyStructuredValue(value: unknown): string {
  if (!value) {
    return 'Not provided';
  }

  if (typeof value === 'string') {
    return value;
  }

  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function getStatusTone(status?: string | null): string {
  switch (status?.toLowerCase()) {
    case 'critical':
      return 'border-[#f1b5bc] bg-[#fff1f3] text-[#b42318]';
    case 'high':
      return 'border-[#f4c6a3] bg-[#fff5eb] text-[#b54708]';
    case 'medium':
      return 'border-[#f2dda1] bg-[#fff9e7] text-[#946200]';
    case 'low':
    case 'info':
      return 'border-[#cbdff0] bg-[#f2f8fc] text-[#1f5f89]';
    case 'active':
    case 'accepted':
    case 'assigned':
    case 'in_progress':
    case 'validated':
    case 'completed':
    case 'resolved':
    case 'paid':
      return 'border-[#c9e2cf] bg-[#eef7ef] text-[#24613a]';
    case 'pending':
    case 'invited':
    case 'scheduled':
    case 'draft':
    case 'matching':
    case 'submitted':
    case 'triage':
      return 'border-[#ecd4aa] bg-[#faf1e1] text-[#9a6412]';
    case 'declined':
    case 'invalid':
    case 'cancelled':
    case 'archived':
    case 'closed':
    case 'rejected':
      return 'border-[#f2c0bc] bg-[#fff2f1] text-[#b42318]';
    default:
      return 'border-[#d6dee7] bg-[#f5f7fa] text-[#334155]';
  }
}

export function StatusBadge({ status }: { status?: string | null }) {
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${getStatusTone(status)}`}>
      {formatStatusLabel(status)}
    </span>
  );
}

export function Banner({
  title,
  subtitle,
  badge,
  icon,
  tone = 'slate',
}: {
  title: string;
  subtitle: string;
  badge?: string;
  icon: string;
  tone?: WorkflowTone;
}) {
  const toneStyles = getWorkflowToneStyles(tone);

  return (
    <div className="relative overflow-hidden rounded-[32px] border border-[#d5c4eb] bg-gradient-to-br from-[#f6efff] via-[#faf7fc] to-[#f0e7fa] p-8 shadow-[0_22px_60px_rgba(125,57,194,0.15)]">
      <div className="absolute -right-14 -top-16 h-60 w-60 rounded-full bg-[#e5d4f7] opacity-40 blur-3xl" />
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(125,57,194,0.08)_0%,rgba(193,118,255,0.05)_42%,transparent_72%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.6),transparent_55%)]" />

      <div className="relative flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <div className="mb-5 flex items-center gap-3">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-[#d5c4eb] bg-white text-2xl shadow-[0_4px_12px_rgba(125,57,194,0.12)]">
              {icon}
            </span>
            {badge ? (
              <span className="inline-flex rounded-full border border-[#d5c4eb] bg-white/80 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-[#7d39c2] shadow-sm">
                {badge}
              </span>
            ) : null}
          </div>
          <h2 className="text-3xl font-semibold tracking-[-0.02em] text-[#2d2a26] sm:text-[2rem]">{title}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-[#5f5851]">{subtitle}</p>
        </div>

        <div className="rounded-[24px] border border-[#d5c4eb] bg-white/90 p-4 backdrop-blur-sm shadow-sm lg:max-w-xs">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-[#8b8177]">Delivery Mode</p>
          <p className="mt-2 text-sm font-semibold text-[#2d2a26]">Live assigned workflow</p>
          <p className="mt-2 text-sm leading-6 text-[#6d6760]">
            Operational data, submissions, and workflow state stay on this page instead of static copy.
          </p>
        </div>
      </div>
    </div>
  );
}

export function SectionCard({
  title,
  description,
  action,
  children,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-[28px] border border-[#dbe3ec] dark:border-gray-700 bg-white dark:bg-[#111111] p-6 shadow-[0_2px_6px_rgba(15,23,42,0.03),0_16px_36px_rgba(15,23,42,0.06)]">
      <div className="flex flex-col gap-4 border-b border-[#ecf0f5] dark:border-gray-700 pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold tracking-[-0.01em] text-[#0f172a] dark:text-slate-100">{title}</h3>
          {description ? <p className="mt-1 text-sm leading-6 text-[#556273] dark:text-slate-400">{description}</p> : null}
        </div>
        {action}
      </div>
      <div className="pt-6">{children}</div>
    </section>
  );
}

export function MetricGrid({
  items,
}: {
  items: Array<{ label: string; value: string; helper?: string }>;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="overflow-hidden rounded-[24px] border border-[#dbe3ec] dark:border-gray-700 bg-[linear-gradient(180deg,#ffffff_0%,#f7f9fc_100%)] dark:bg-gray-800 p-5 shadow-[0_2px_4px_rgba(15,23,42,0.03)]"
        >
          <div className="mb-4 h-1.5 w-14 rounded-full bg-[linear-gradient(90deg,#0f172a_0%,#94a3b8_100%)] dark:bg-[linear-gradient(90deg,#7d39c2_0%,#c176ff_100%)]" />
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-[#728092] dark:text-slate-400">{item.label}</p>
          <p className="mt-3 text-[1.7rem] font-semibold tracking-[-0.03em] text-[#0f172a] dark:text-slate-100">{item.value}</p>
          {item.helper ? <p className="mt-2 text-sm leading-6 text-[#556273] dark:text-slate-400">{item.helper}</p> : null}
        </div>
      ))}
    </div>
  );
}

export function WorkflowTimeline({ steps }: { steps: WorkflowStep[] }) {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => {
        const tone =
          step.state === 'complete'
            ? 'border-[#c9e2cf] bg-[#eef7ef] text-[#24613a] dark:border-green-700 dark:bg-green-900/30 dark:text-green-400'
            : step.state === 'active'
              ? 'border-[#f7c3aa] bg-[#fff3ee] text-[#b54708] dark:border-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
              : 'border-[#d6dee7] bg-[#f5f7fa] text-[#556273] dark:border-gray-700 dark:bg-gray-800 dark:text-slate-400';

        return (
          <div key={`${step.label}-${index}`} className="relative flex gap-4">
            {index < steps.length - 1 ? <div className="absolute left-[17px] top-10 h-[calc(100%-8px)] w-px bg-[#dbe3ec] dark:bg-gray-700" /> : null}
            <div className={`relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-sm font-semibold ${tone}`}>
              {step.state === 'complete' ? '✓' : index + 1}
            </div>
            <div className="min-w-0 rounded-[22px] border border-[#e9eef5] dark:border-gray-700 bg-[#fbfcfd] dark:bg-gray-800 px-4 py-3">
              <p className="text-sm font-semibold text-[#0f172a] dark:text-slate-100">{step.label}</p>
              <p className="mt-1 text-sm leading-6 text-[#556273] dark:text-slate-400">{step.detail}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function EmptyCollection({
  title,
  description,
  hint,
}: {
  title: string;
  description: string;
  hint?: string;
}) {
  return (
    <div className="rounded-[24px] border border-dashed border-[#cfd8e3] dark:border-gray-600 bg-[linear-gradient(180deg,#fcfdff_0%,#f6f8fb_100%)] dark:bg-gray-800/50 px-6 py-10 text-center">
      <div className="mx-auto mb-4 h-12 w-12 rounded-2xl border border-[#dbe3ec] dark:border-gray-700 bg-white dark:bg-gray-800 shadow-[0_8px_18px_rgba(15,23,42,0.06)]" />
      <h4 className="text-base font-semibold text-[#0f172a] dark:text-slate-100">{title}</h4>
      <p className="mt-2 text-sm leading-6 text-[#556273] dark:text-slate-400">{description}</p>
      {hint ? <p className="mt-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#728092] dark:text-slate-500">{hint}</p> : null}
    </div>
  );
}

export function PillList({ items }: { items: string[] }) {
  if (!items.length) {
    return <p className="text-sm text-[#728092] dark:text-slate-500">Not provided.</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          key={item}
          className="rounded-full border border-[#dbe3ec] dark:border-gray-700 bg-[#f7f9fc] dark:bg-gray-800 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-[#475467] dark:text-slate-300"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export function WorkflowTabs<T extends string>({
  items,
  active,
  onChange,
  tone = 'slate',
}: {
  items: Array<{ value: T; label: string; badge?: string | number }>;
  active: T;
  onChange: (value: T) => void;
  tone?: WorkflowTone;
}) {
  const toneStyles = getWorkflowToneStyles(tone);

  return (
    <div className="flex flex-wrap gap-2 rounded-[24px] border border-[#dbe3ec] bg-white dark:bg-[#111111] p-2 shadow-[0_2px_4px_rgba(15,23,42,0.03)]">
      {items.map((item) => {
        const isActive = item.value === active;

        return (
          <button
            key={item.value}
            type="button"
            onClick={() => onChange(item.value)}
            className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-semibold transition ${isActive ? toneStyles.tabActive : toneStyles.tabIdle}`}
          >
            <span>{item.label}</span>
            {item.badge !== undefined ? (
              <span
                className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${isActive ? 'bg-white/15 text-white' : 'bg-[#eef2f6] text-[#475467]'}`}
              >
                {item.badge}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}

export function WorkflowPickerCard({
  title,
  description,
  status,
  selected,
  onClick,
  tone = 'slate',
  metrics,
  footer,
  children,
}: {
  title: string;
  description?: string;
  status?: string | null;
  selected?: boolean;
  onClick?: () => void;
  tone?: WorkflowTone;
  metrics?: Array<{ label: string; value: string }>;
  footer?: ReactNode;
  children?: ReactNode;
}) {
  const toneStyles = getWorkflowToneStyles(tone);
  const Component = onClick ? 'button' : 'div';

  return (
    <Component
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`group relative overflow-hidden rounded-[24px] border p-5 text-left transition ${
        selected
          ? toneStyles.selectedSurface
          : `border-[#dbe3ec] bg-white shadow-[0_2px_4px_rgba(15,23,42,0.03)] ${toneStyles.hoverSurface}`
      }`}
    >
      <div className={`absolute inset-x-0 top-0 h-1 ${toneStyles.accentBar}`} />
      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-lg font-semibold tracking-[-0.02em] text-[#0f172a]">{title}</p>
            {description ? <p className="mt-2 text-sm leading-6 text-[#556273]">{description}</p> : null}
          </div>
          {status ? <StatusBadge status={status} /> : null}
        </div>

        {metrics?.length ? (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {metrics.map((metric) => (
              <div key={`${metric.label}-${metric.value}`} className={`rounded-[18px] border px-4 py-3 ${toneStyles.accentBorder} ${toneStyles.accentSoft}`}>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#728092]">{metric.label}</p>
                <p className="mt-1 text-sm font-semibold text-[#0f172a]">{metric.value}</p>
              </div>
            ))}
          </div>
        ) : null}

        {children ? <div className="mt-5">{children}</div> : null}
        {footer ? <div className="mt-5">{footer}</div> : null}
      </div>
    </Component>
  );
}

export function InfoList({
  items,
}: {
  items: Array<{ label: string; value: string }>;
}) {
  return (
    <dl className="divide-y divide-[#e9eef5] rounded-[20px] border border-[#dbe3ec] bg-[#fbfcfd]">
      {items.map((item) => (
        <div key={`${item.label}-${item.value}`} className="flex items-center justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-[#556273]">{item.label}</dt>
          <dd className="text-sm font-semibold text-[#0f172a] text-right">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function StructuredValueBlock({
  value,
}: {
  value: unknown;
}) {
  return (
    <pre className="overflow-x-auto rounded-[20px] border border-[#dbe3ec] bg-[#f8fafc] p-4 text-xs leading-6 text-[#334155] shadow-[inset_0_1px_0_rgba(255,255,255,0.4)]">
      {stringifyStructuredValue(value)}
    </pre>
  );
}
