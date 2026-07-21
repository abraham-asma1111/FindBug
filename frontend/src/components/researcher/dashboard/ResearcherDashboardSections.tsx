import Link from 'next/link';
import SectionCard from '@/components/dashboard/SectionCard';
import { formatCompactNumber, formatCurrency } from '@/lib/portal';
import {
  type MyReputationData,
  type NotificationItem,
  type ResearcherDashboardData,
  type ResearcherPerformanceData,
  type SimulationStatsData,
} from '@/hooks/useResearcherDashboardData';

type AlertTone = 'critical' | 'warning' | 'info' | 'success';

export interface DashboardAlert {
  id: string;
  label: string;
  title: string;
  description: string;
  href: string;
  actionText: string;
  tone: AlertTone;
}

export interface DashboardWorkflowModule {
  href: string;
  module: string;
  signal: string;
  workflow: string;
  actionText: string;
  accent: string;
}

interface BuildResearcherDashboardAlertsParams {
  notifications: NotificationItem[];
  unreadMessages: number;
  walletAvailable: number;
  activePrograms: number;
  secondaryWarnings: string[];
  isLoading: boolean;
  messagesUnavailable: boolean;
  walletUnavailable: boolean;
}

interface ResearcherDashboardAlertsSectionProps {
  alerts: DashboardAlert[];
  isLoading: boolean;
}

interface ResearcherDashboardJumpboardSectionProps {
  workflowModules: DashboardWorkflowModule[];
}

interface ResearcherDashboardInsightsSectionProps {
  isLoading: boolean;
  performanceUnavailable: boolean;
  simulationUnavailable: boolean;
  earnings?: ResearcherDashboardData['earnings'];
  performance: ResearcherPerformanceData | null;
  myReputation: MyReputationData | null;
  reputation?: ResearcherDashboardData['reputation'];
  monthlyTrend: ResearcherDashboardData['monthly_trend'];
  maxMonthlySubmissions: number;
  simulation: SimulationStatsData | null;
}

const alertToneStyles: Record<AlertTone, { panel: string; badge: string; action: string }> = {
  critical: {
    panel: 'border-[#f2c0bc] dark:border-red-900 bg-[#fff2f1] dark:bg-[#111111]',
    badge: 'bg-[#b42318] text-white',
    action: 'border-[#e7b4b0] dark:border-red-800 text-[#7a1b12] dark:text-red-400 hover:bg-white/70 dark:hover:bg-neutral-800',
  },
  warning: {
    panel: 'border-[#ead6ac] dark:border-yellow-900 bg-[#fff8e8] dark:bg-[#111111]',
    badge: 'bg-[#9a6412] text-white',
    action: 'border-[#e7d3a2] dark:border-yellow-800 text-[#7a5210] dark:text-yellow-400 hover:bg-white/70 dark:hover:bg-neutral-800',
  },
  info: {
    panel: 'border-[#c9dceb] dark:border-blue-900 bg-[#f1f7fb] dark:bg-[#111111]',
    badge: 'bg-[#2d78a8] text-white',
    action: 'border-[#c2d7e7] dark:border-blue-800 text-[#225f84] dark:text-blue-400 hover:bg-white/70 dark:hover:bg-neutral-800',
  },
  success: {
    panel: 'border-[#c9dfcf] dark:border-green-900 bg-[#f1f8f2] dark:bg-[#111111]',
    badge: 'bg-[#24613a] text-white',
    action: 'border-[#c3dcc9] dark:border-green-800 text-[#1f5232] dark:text-green-400 hover:bg-white/70 dark:hover:bg-neutral-800',
  },
};

const severityTone: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-[#2d2a26]',
  low: 'bg-[#2d78a8] text-white',
  info: 'bg-[#5f5851] text-white',
};

export function formatDashboardMetricLabel(value?: string | null): string {
  if (!value) {
    return 'Unknown';
  }

  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatTrendLabel(month: string, label?: string): string {
  if (label) {
    return label;
  }

  const parsedMonth = new Date(`${month}-01T00:00:00Z`);

  if (Number.isNaN(parsedMonth.getTime())) {
    return month;
  }

  return parsedMonth.toLocaleDateString('en-US', { month: 'short' });
}

function getNotificationTone(priority?: string | null): AlertTone {
  switch (priority?.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'critical';
    case 'medium':
      return 'warning';
    default:
      return 'info';
  }
}

function getNotificationHref(type?: string | null, actionUrl?: string | null): string {
  if (actionUrl?.startsWith('/')) {
    return actionUrl;
  }

  const normalizedType = type?.toLowerCase() || '';

  if (normalizedType.includes('message')) {
    return '/researcher/messages';
  }

  if (
    normalizedType.includes('payment') ||
    normalizedType.includes('wallet') ||
    normalizedType.includes('payout')
  ) {
    return '/researcher/earnings';
  }

  if (normalizedType.includes('simulation')) {
    return '/researcher/simulation';
  }

  if (normalizedType.includes('program') || normalizedType.includes('engagement')) {
    return '/researcher/engagements';
  }

  return '/researcher/reports';
}

export function buildResearcherDashboardAlerts({
  notifications,
  unreadMessages,
  walletAvailable,
  activePrograms,
  secondaryWarnings,
  isLoading,
  messagesUnavailable,
  walletUnavailable,
}: BuildResearcherDashboardAlertsParams): DashboardAlert[] {
  const notificationAlerts: DashboardAlert[] = notifications.slice(0, 2).map((notification) => ({
    id: `notification-${notification.id}`,
    label: formatDashboardMetricLabel(notification.priority || notification.type || 'update'),
    title: notification.title,
    description: notification.message,
    href: getNotificationHref(notification.type, notification.action_url),
    actionText: notification.action_text || 'Open workflow',
    tone: getNotificationTone(notification.priority),
  }));

  const derivedAlerts: DashboardAlert[] = [];

  if (!isLoading && !messagesUnavailable && unreadMessages > 0) {
    derivedAlerts.push({
      id: 'unread-messages',
      label: 'Messages',
      title: `${formatCompactNumber(unreadMessages)} unread conversation updates`,
      description: 'Researcher follow-ups and triage questions are waiting in the inbox.',
      href: '/researcher/messages',
      actionText: 'Open inbox',
      tone: 'warning',
    });
  }

  if (!isLoading && !walletUnavailable && walletAvailable > 0) {
    derivedAlerts.push({
      id: 'wallet-ready',
      label: 'Earnings',
      title: `${formatCurrency(walletAvailable)} available for withdrawal`,
      description: 'Review payout methods and KYC blockers before requesting a withdrawal.',
      href: '/researcher/earnings',
      actionText: 'Review payouts',
      tone: 'success',
    });
  }

  if (!isLoading && activePrograms === 0) {
    derivedAlerts.push({
      id: 'join-program',
      label: 'Engagements',
      title: 'No active program participation yet',
      description: 'Join a public program or accept an invitation to unlock report submission paths.',
      href: '/researcher/engagements',
      actionText: 'Browse opportunities',
      tone: 'info',
    });
  }

  if (!isLoading && secondaryWarnings.length) {
    derivedAlerts.push({
      id: 'service-warnings',
      label: 'Service status',
      title: 'Some linked dashboard widgets are unavailable',
      description: `Unavailable right now: ${secondaryWarnings.map((item) => formatDashboardMetricLabel(item)).join(', ')}. Open the owning workflow module directly if needed.`,
      href: '/researcher/reports',
      actionText: 'Open reports',
      tone: 'critical',
    });
  }

  return [...notificationAlerts, ...derivedAlerts].slice(0, 4);
}

export function ResearcherDashboardAlertsSection({
  alerts,
  isLoading,
}: ResearcherDashboardAlertsSectionProps) {
  return (
    <SectionCard
      title="Alerts and Inbox"
      description="Immediate blockers and follow-ups pulled from notifications, messages, wallet status, and workflow service health."
      headerAlign="center"
    >
      {alerts.length ? (
        <div className="grid gap-4 xl:grid-cols-2">
          {alerts.map((alert) => {
            const styles = alertToneStyles[alert.tone];

            return (
              <div key={alert.id} className={`rounded-[28px] border p-5 ${styles.panel}`}>
                <div className="flex items-start justify-between gap-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${styles.badge}`}
                  >
                    {alert.label}
                  </span>
                  <Link
                    href={alert.href}
                    className={`inline-flex rounded-full border px-4 py-2 text-xs font-semibold transition ${styles.action}`}
                  >
                    {alert.actionText}
                  </Link>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-[#2d2a26] dark:text-white">{alert.title}</h3>
                <p className="mt-2 text-sm leading-6 text-[#5f5851] dark:text-gray-300">{alert.description}</p>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="rounded-[28px] border border-dashed border-[#d8d0c8] dark:border-gray-700 bg-[#fcfaf7] dark:bg-[#111111] p-6 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177] dark:text-gray-400">All Clear</p>
          <p className="mt-3 text-sm leading-6 text-[#6d6760] dark:text-gray-300">
            {isLoading
              ? 'Loading alert state...'
              : 'No urgent workflow alerts are blocking you right now. Continue with reports, reputation, or simulation.'}
          </p>
        </div>
      )}
    </SectionCard>
  );
}

export function ResearcherDashboardJumpboardSection({
  workflowModules,
}: ResearcherDashboardJumpboardSectionProps) {
  return (
    <SectionCard
      title="Workflow Jumpboard"
      description="The researcher sidebar modules mapped directly to the roadmap ownership model and backend API families."
      headerAlign="center"
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {workflowModules.map((item) => (
          <div
            key={item.module}
            className={`rounded-[30px] bg-gradient-to-br ${item.accent} p-[1px] shadow-[0_18px_34px_rgba(45,42,38,0.08)]`}
          >
            <div className="h-full rounded-[29px] bg-white/95 dark:bg-[#111111] p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400 dark:text-gray-400">
                    {item.module}
                  </p>
                  <p className="mt-3 text-2xl font-semibold tracking-tight text-[#2d2a26] dark:text-white dark:text-white">
                    {item.signal}
                  </p>
                </div>
                <span className="rounded-full bg-[#f3ede6] dark:bg-neutral-800 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#5f5851] dark:text-gray-300 dark:text-gray-300">
                  Live signal
                </span>
              </div>
              <p className="mt-4 text-sm leading-6 text-[#6d6760] dark:text-gray-300 dark:text-gray-400">{item.workflow}</p>
              <Link
                href={item.href}
                className="mt-5 inline-flex rounded-full border border-[#d8d0c8] dark:border-gray-700 px-4 py-2 text-xs font-semibold text-[#2d2a26] dark:text-white dark:text-white transition hover:border-[#c8bfb6] dark:hover:border-gray-600 hover:bg-[#fcfaf7] dark:hover:bg-neutral-800"
              >
                {item.actionText}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

export function ResearcherDashboardInsightsSection({
  isLoading,
  performanceUnavailable,
  simulationUnavailable,
  earnings,
  performance,
  myReputation,
  reputation,
  monthlyTrend,
  maxMonthlySubmissions,
  simulation,
}: ResearcherDashboardInsightsSectionProps) {
  const severityDistribution = performance?.severity_distribution || {};
  const totalSeverityReports = Object.values(severityDistribution).reduce((sum, value) => sum + value, 0);
  const simulationStatEntries = Object.entries(simulation?.stats || {})
    .filter(([, value]) => typeof value === 'number')
    .slice(0, 4)
    .map(([key, value]) => ({
      key,
      label: formatDashboardMetricLabel(key),
      value: formatCompactNumber(Number(value)),
    }));

  return (
    <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
      <SectionCard
        title="Performance Snapshot"
        description="Analytics, severity mix, and specialization signals from the linked researcher performance service."
        headerAlign="center"
      >
        <div className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl bg-[#faf6f1] dark:bg-[#111111] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                Success Rate
              </p>
              <p className="mt-2 text-2xl font-semibold text-[#2d2a26] dark:text-white">
                {isLoading
                  ? '...'
                  : performanceUnavailable
                    ? 'Unavailable'
                    : `${Math.round(performance?.metrics.success_rate ?? 0)}%`}
              </p>
            </div>
            <div className="rounded-2xl bg-[#faf6f1] dark:bg-[#111111] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                Paid Earnings
              </p>
              <p className="mt-2 text-2xl font-semibold text-[#2d2a26] dark:text-white">
                {isLoading
                  ? '...'
                  : formatCurrency(performance?.metrics.earnings ?? earnings?.paid_earnings ?? 0)}
              </p>
            </div>
            <div className="rounded-2xl bg-[#faf6f1] dark:bg-[#111111] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                Reputation Score
              </p>
              <p className="mt-2 text-2xl font-semibold text-[#2d2a26] dark:text-white">
                {isLoading
                  ? '...'
                  : formatCompactNumber(
                      myReputation?.profile?.reputation_score ?? reputation?.score ?? 0
                    )}
              </p>
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
              Severity Distribution
            </p>
            <div className="mt-4 space-y-3">
              {Object.entries(severityDistribution).length ? (
                Object.entries(severityDistribution).map(([severity, count]) => {
                  const width = totalSeverityReports ? (count / totalSeverityReports) * 100 : 0;

                  return (
                    <div key={severity} className="grid grid-cols-[88px_minmax(0,1fr)_36px] items-center gap-3">
                      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                        {formatDashboardMetricLabel(severity)}
                      </span>
                      <div className="h-3 overflow-hidden rounded-full bg-[#f3ede6] dark:bg-neutral-800">
                        <div
                          className={`h-full rounded-full ${
                            severityTone[severity]?.split(' ')[0] || 'bg-[#c96d3a]'
                          }`}
                          style={{ width: `${Math.max(width, count ? 10 : 0)}%` }}
                        />
                      </div>
                      <span className="text-right text-sm font-semibold text-[#2d2a26] dark:text-white">{count}</span>
                    </div>
                  );
                })
              ) : (
                <div className="rounded-2xl border border-dashed border-[#d8d0c8] dark:border-gray-700 bg-[#fcfaf7] dark:bg-[#111111] p-4 text-sm text-[#6d6760] dark:text-gray-300">
                  {isLoading
                    ? 'Loading severity data...'
                    : performanceUnavailable
                      ? 'Performance analytics are unavailable right now.'
                      : 'No severity distribution is available yet.'}
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-[#e6ddd4] dark:border-gray-800 pt-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
              Top Vulnerability Types
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {(performance?.top_vulnerability_types || []).length ? (
                performance?.top_vulnerability_types.map((entry) => (
                  <span
                    key={`${entry.type}-${entry.count}`}
                    className="rounded-full bg-[#edf5fb] dark:bg-blue-900/30 px-3 py-2 text-xs font-semibold text-[#2d78a8] dark:text-blue-400"
                  >
                    {entry.type || 'Unspecified'} · {entry.count}
                  </span>
                ))
              ) : (
                <p className="text-sm text-[#6d6760] dark:text-gray-300">
                  {isLoading
                    ? 'Loading specialization data...'
                    : performanceUnavailable
                      ? 'Performance analytics are unavailable right now.'
                      : 'No specialization pattern is available yet.'}
                </p>
              )}
            </div>
          </div>
        </div>
      </SectionCard>

      <div className="space-y-6">
        <SectionCard
          title="Monthly Momentum"
          description="Rolling 12-month submission history from the researcher dashboard service."
          headerAlign="center"
        >
          {monthlyTrend.length ? (
            <div className="rounded-[28px] bg-[#faf6f1] dark:bg-[#111111] p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177] dark:text-gray-400">
                    Submission trend
                  </p>
                  <p className="mt-1 text-sm text-[#6d6760] dark:text-gray-300">
                    Each bar shows how many reports you submitted in that month.
                  </p>
                </div>
                <p className="text-right text-xs text-[#8b8177] dark:text-gray-400">
                  Peak month:{' '}
                  <span className="font-semibold text-[#2d2a26] dark:text-white">{maxMonthlySubmissions}</span>
                </p>
              </div>

              <div className="flex h-64 items-end gap-2">
                {monthlyTrend.map((entry) => {
                  const barHeight = (entry.submissions / maxMonthlySubmissions) * 100;

                  return (
                    <div key={entry.month} className="flex h-full min-w-0 flex-1 flex-col justify-end">
                      <p className="mb-2 text-center text-xs font-semibold text-[#2d2a26] dark:text-white">
                        {entry.submissions}
                      </p>
                      <div className="flex h-44 items-end justify-center">
                        <div className="flex h-full w-full max-w-[42px] items-end rounded-[18px] bg-white/75 dark:bg-neutral-800 px-1 pb-1 shadow-inner">
                          <div
                            className="w-full rounded-[14px] bg-gradient-to-t from-[#c96d3a] via-[#df8a53] to-[#f4c38b] shadow-[0_14px_30px_rgba(201,109,58,0.18)]"
                            style={{
                              height: entry.submissions > 0 ? `${Math.max(barHeight, 10)}%` : '4px',
                            }}
                            title={`${entry.month}: ${entry.submissions} reports submitted`}
                          />
                        </div>
                      </div>
                      <p className="mt-3 truncate text-center text-xs font-semibold uppercase tracking-[0.16em] text-[#8b8177] dark:text-gray-400">
                        {formatTrendLabel(entry.month, entry.label)}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="text-sm text-[#6d6760] dark:text-gray-300">
              {isLoading ? 'Loading trend data...' : 'No trend data available yet.'}
            </p>
          )}
        </SectionCard>

        <SectionCard
          title="Simulation Snapshot"
          description="Private training metrics remain a personal feedback loop for your live reporting workflow."
          headerAlign="center"
        >
          <div className="space-y-4">
            <div className="rounded-3xl bg-[#faf6f1] dark:bg-[#111111] p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                Privacy Note
              </p>
              <p className="mt-3 text-sm leading-6 text-[#6d6760] dark:text-gray-300">
                {simulation?.privacy_note ||
                  'Simulation scores stay private and surface here only as personal progress signals.'}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {simulationStatEntries.length ? (
                simulationStatEntries.map((entry) => (
                  <div key={entry.key} className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                      {entry.label}
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-[#2d2a26] dark:text-white">{entry.value}</p>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-[#d8d0c8] dark:border-gray-700 bg-[#fcfaf7] dark:bg-[#111111] p-5 text-sm leading-6 text-[#6d6760] dark:text-gray-300 sm:col-span-2">
                  {isLoading
                    ? 'Loading private simulation metrics...'
                    : simulationUnavailable
                      ? 'Simulation metrics are unavailable right now. Open the simulation workspace to retry the service.'
                      : 'No simulation metrics were returned. Open the simulation module to initialize practice activity.'}
                </div>
              )}
            </div>

            <Link
              href="/researcher/simulation"
              className="inline-flex rounded-full bg-[#2d2a26] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1f1c19]"
            >
              Open Simulation Workspace
            </Link>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
