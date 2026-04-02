'use client';

import Link from 'next/link';
import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import {
  formatCompactNumber,
  formatCurrency,
  formatDateTime,
  getPortalNavItems,
} from '@/lib/portal';
import { type ResearcherDashboardData, useResearcherDashboardData } from '@/hooks/useResearcherDashboardData';
import { useAuthStore } from '@/store/authStore';

const submissionTabs = ['new', 'triaged', 'valid', 'invalid', 'closed'] as const;
type SubmissionTab = (typeof submissionTabs)[number];

const statusTone: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  triaged: 'bg-[#faf1e1] text-[#9a6412]',
  valid: 'bg-[#eef7ef] text-[#24613a]',
  invalid: 'bg-[#fff2f1] text-[#b42318]',
  closed: 'bg-[#f3ede6] text-[#5f5851]',
  resolved: 'bg-[#f3ede6] text-[#5f5851]',
};

const severityTone: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-[#2d2a26]',
  low: 'bg-[#2d78a8] text-white',
  info: 'bg-[#5f5851] text-white',
};

function normalizeSubmissionStatus(status?: string | null): SubmissionTab | null {
  const value = status?.toLowerCase();

  if (value === 'new' || value === 'triaged' || value === 'valid' || value === 'invalid') {
    return value;
  }

  if (value === 'closed' || value === 'resolved') {
    return 'closed';
  }

  return null;
}

function formatSubmissionStatus(status?: string | null): string {
  const normalized = normalizeSubmissionStatus(status);

  if (!normalized) {
    return status || '-';
  }

  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
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

function formatMetricLabel(value?: string | null): string {
  if (!value) {
    return 'Unknown';
  }

  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getNotificationTone(priority?: string | null): string {
  switch (priority?.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'bg-[#fff2f1] text-[#b42318]';
    case 'medium':
      return 'bg-[#faf1e1] text-[#9a6412]';
    default:
      return 'bg-[#eef5fb] text-[#2d78a8]';
  }
}

function getSubmissionWorkflow(status?: string | null): {
  nextStep: string;
  actionLabel: string;
  href: string;
} {
  switch (normalizeSubmissionStatus(status)) {
    case 'new':
      return {
        nextStep: 'Complete the evidence package and watch for first triage contact.',
        actionLabel: 'Open report',
        href: '/researcher/reports',
      };
    case 'triaged':
      return {
        nextStep: 'Review triage feedback and respond with clarifications or more proof.',
        actionLabel: 'Review triage',
        href: '/researcher/reports',
      };
    case 'valid':
      return {
        nextStep: 'Track remediation and bounty approval from the report detail flow.',
        actionLabel: 'Track payout',
        href: '/researcher/reports',
      };
    case 'invalid':
      return {
        nextStep: 'Read the decision carefully and capture lessons for your next submission.',
        actionLabel: 'Review notes',
        href: '/researcher/reports',
      };
    case 'closed':
      return {
        nextStep: 'Keep the final state as portfolio and earnings history.',
        actionLabel: 'View history',
        href: '/researcher/reports',
      };
    default:
      return {
        nextStep: 'Open the report workflow and inspect the current handoff state.',
        actionLabel: 'Open workflow',
        href: '/researcher/reports',
      };
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

  if (normalizedType.includes('payment') || normalizedType.includes('wallet') || normalizedType.includes('payout')) {
    return '/researcher/earnings';
  }

  if (normalizedType.includes('simulation')) {
    return '/researcher/simulation';
  }

  return '/researcher/reports';
}

function buildTwelveMonthTrend(
  trend: ResearcherDashboardData['monthly_trend']
): ResearcherDashboardData['monthly_trend'] {
  const trendByMonth = new Map(trend.map((entry) => [entry.month, entry]));
  const months: ResearcherDashboardData['monthly_trend'] = [];
  const now = new Date();
  const currentMonthStart = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));

  for (let index = 11; index >= 0; index -= 1) {
    const monthStart = new Date(
      Date.UTC(currentMonthStart.getUTCFullYear(), currentMonthStart.getUTCMonth() - index, 1)
    );
    const monthKey = `${monthStart.getUTCFullYear()}-${String(monthStart.getUTCMonth() + 1).padStart(2, '0')}`;
    const existingEntry = trendByMonth.get(monthKey);

    months.push({
      month: monthKey,
      label: monthStart.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' }),
      submissions: existingEntry?.submissions ?? 0,
      earnings: existingEntry?.earnings ?? 0,
    });
  }

  return months;
}

export default function ResearcherDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const {
    data,
    notifications,
    unreadNotifications,
    unreadMessages,
    wallet,
    performance,
    myReputation,
    simulation,
    error,
    secondaryWarnings,
    isLoading,
  } = useResearcherDashboardData();
  const [activeTab, setActiveTab] = useState<SubmissionTab>('new');

  const monthlyTrend = buildTwelveMonthTrend(data?.monthly_trend ?? []);
  const maxMonthlySubmissions = monthlyTrend.reduce((highest, entry) => {
    return Math.max(highest, entry.submissions);
  }, 1);
  const recentSubmissions = data?.recent_submissions ?? [];
  const filteredSubmissions = recentSubmissions.filter(
    (submission) => normalizeSubmissionStatus(submission.status) === activeTab
  );
  const unavailableWidgets = new Set(secondaryWarnings);
  const notificationsUnavailable = unavailableWidgets.has('notifications');
  const messagesUnavailable = unavailableWidgets.has('messages');
  const walletUnavailable = unavailableWidgets.has('wallet');
  const performanceUnavailable = unavailableWidgets.has('performance');
  const simulationUnavailable = unavailableWidgets.has('simulation');
  const simulationStatEntries = Object.entries(simulation?.stats || {})
    .filter(([, value]) => typeof value === 'number')
    .slice(0, 4)
    .map(([key, value]) => ({
      key,
      label: formatMetricLabel(key),
      value: formatCompactNumber(Number(value)),
    }));
  const workflowModules = [
    {
      href: '/researcher/engagements',
      module: 'Engagements',
      signal: isLoading ? '...' : `${formatCompactNumber(data?.overview.active_programs)} active`,
      workflow: 'Review joined programs, invitations, and matching opportunities before drafting findings.',
      actionText: 'Open engagements',
    },
    {
      href: '/researcher/reports',
      module: 'Reports',
      signal: isLoading ? '...' : `${data?.overview.submissions_by_status?.new || 0} still new`,
      workflow: 'Submit new findings, answer triage requests, and keep evidence attached to each report.',
      actionText: 'Open reports',
    },
    {
      href: '/researcher/earnings',
      module: 'Earnings',
      signal: isLoading
        ? '...'
        : walletUnavailable
          ? 'Service unavailable'
          : formatCurrency(wallet?.available_balance ?? data?.earnings.pending_earnings),
      workflow: 'Check balance, payout blockers, and KYC state before requesting a withdrawal.',
      actionText: 'Open earnings',
    },
    {
      href: '/researcher/messages',
      module: 'Messages',
      signal: isLoading ? '...' : messagesUnavailable ? 'Service unavailable' : `${formatCompactNumber(unreadMessages)} unread`,
      workflow: 'Handle follow-ups from triage and organizations without leaving the portal workflow.',
      actionText: 'Open inbox',
    },
    {
      href: '/researcher/reputation',
      module: 'Reputation',
      signal: isLoading ? '...' : `#${myReputation?.rank_info?.rank || data?.reputation.rank || '-'}`,
      workflow: myReputation?.rank_info
        ? `Top ${Math.round(myReputation.rank_info.percentile)}% of researchers`
        : 'Current leaderboard position',
      actionText: 'Open reputation',
    },
    {
      href: '/researcher/simulation',
      module: 'Simulation',
      signal: simulationUnavailable ? 'Service unavailable' : simulationStatEntries[0]?.value || 'Private',
      workflow: simulationUnavailable
        ? 'The training service did not answer. Retry from the simulation module.'
        : simulationStatEntries[0]?.label || 'Training metrics stay private to you',
      actionText: 'Open simulation',
    },
  ];

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Overview"
          subtitle="Track submission throughput, earnings, and reputation from the first cross-role bug bounty slice."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Total Submissions"
            value={isLoading ? '...' : formatCompactNumber(data?.overview.total_submissions)}
            helper="Lifetime reports submitted"
          />
          <StatCard
            label="Active Programs"
            value={isLoading ? '...' : formatCompactNumber(data?.overview.active_programs)}
            helper="Programs you are currently active in"
          />
          <StatCard
            label="Total Earnings"
            value={isLoading ? '...' : formatCurrency(data?.earnings.total_earnings)}
            helper={`Pending ${formatCurrency(data?.earnings.pending_earnings)}`}
          />
          <StatCard
            label="Reputation"
            value={isLoading ? '...' : formatCompactNumber(data?.reputation.score)}
            helper={
              data
                ? `Rank ${data.reputation.rank || '-'} of ${data.reputation.total_researchers || 0}`
                : 'Leaderboard position'
            }
          />
        </div>

        <div className="mt-6">
          <SectionCard
            title="Submission Pipeline"
            description="All your submitted reports with status and rewards."
            headerAlign="center"
          >
            <div className="mb-5 grid grid-cols-2 gap-3 border-b border-[#e6ddd4] pb-4 sm:grid-cols-5">
              {submissionTabs.map((tab) => {
                const isActive = tab === activeTab;

                return (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                    className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                      isActive
                        ? 'justify-center bg-[#ef2330] text-white'
                        : 'justify-center bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                    }`}
                  >
                    <span className="capitalize">{tab}</span>
                  </button>
                );
              })}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[#e6ddd4]">
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">DATE</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">ID</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">REPORT TITLE</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PROGRAM</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">REWARDS</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">CVSS</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">NEXT STEP</th>
                    <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    Array.from({ length: 4 }).map((_, index) => (
                      <tr key={`loading-${index}`} className="border-b border-[#efe7de] last:border-0">
                        <td className="py-4 pr-4" colSpan={9}>
                          <div className="h-8 animate-pulse rounded-xl bg-[#f3ede6]" />
                        </td>
                      </tr>
                    ))
                  ) : filteredSubmissions.length ? (
                    filteredSubmissions.map((submission) => {
                      const workflow = getSubmissionWorkflow(submission.status);

                      return (
                      <tr key={submission.id} className="border-b border-[#e6ddd4] last:border-0">
                        <td className="py-3 pr-4 text-[#6d6760]">
                          {submission.submitted_at
                            ? new Date(submission.submitted_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })
                            : '-'}
                        </td>
                        <td className="py-3 pr-4 text-[#6d6760]">{submission.report_number || '-'}</td>
                        <td className="py-3 pr-4 font-medium text-[#2d2a26]">{submission.title}</td>
                        <td className="py-3 pr-4 text-[#6d6760]">{submission.program_name || '-'}</td>
                        <td className="py-3 pr-4 text-[#6d6760]">
                          {submission.bounty_amount ? formatCurrency(submission.bounty_amount) : '-'}
                        </td>
                        <td className="py-3 pr-4 text-[#6d6760]">
                          {submission.cvss_score ? submission.cvss_score.toFixed(1) : submission.assigned_severity || '-'}
                        </td>
                        <td className="py-3">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${
                              statusTone[normalizeSubmissionStatus(submission.status) || submission.status || ''] ||
                              'bg-[#f3ede6] text-[#5f5851]'
                            }`}
                          >
                            {formatSubmissionStatus(submission.status)}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-sm text-[#6d6760]">{workflow.nextStep}</td>
                        <td className="py-3">
                          <Link
                            href={workflow.href}
                            className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                          >
                            {workflow.actionLabel}
                          </Link>
                        </td>
                      </tr>
                    );
                    })
                  ) : (
                    <tr>
                      <td colSpan={9} className="py-10 text-center">
                        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                          No results found
                        </p>
                        <p className="mt-2 text-sm text-[#6d6760]">
                          No {activeTab} submissions are available in the current dashboard data.
                        </p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
          <SectionCard
            title="Reputation Snapshot"
            description="How you currently rank against the researcher pool."
            headerAlign="center"
          >
            <div className="space-y-4 text-sm text-[#6d6760]">
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Percentile</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                  {myReputation?.rank_info ? `${Math.round(myReputation.rank_info.percentile)}%` : data ? `${data.reputation.percentile}%` : '...'}
                </p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Paid Earnings</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                  {isLoading
                    ? '...'
                    : formatCurrency(myReputation?.profile?.total_earnings ?? data?.earnings.paid_earnings)}
                </p>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            title="Monthly Trend"
            description="Reports submitted during each of the last 12 months."
            headerAlign="center"
          >
            <div className="space-y-3">
              {monthlyTrend.length ? (
                <div className="rounded-[28px] bg-[#faf6f1] p-5">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                        12-month submission view
                      </p>
                      <p className="mt-1 text-sm text-[#6d6760]">
                        Each bar shows how many reports you submitted in that month.
                      </p>
                    </div>
                    <p className="text-right text-xs text-[#8b8177]">
                      Peak month: <span className="font-semibold text-[#2d2a26]">{maxMonthlySubmissions}</span> reports
                    </p>
                  </div>

                  <div className="flex h-72 items-end gap-2">
                    {monthlyTrend.map((entry) => {
                      const barHeight = (entry.submissions / maxMonthlySubmissions) * 100;

                      return (
                        <div key={entry.month} className="flex h-full min-w-0 flex-1 flex-col justify-end">
                          <p className="mb-2 text-center text-xs font-semibold text-[#2d2a26]">
                            {entry.submissions}
                          </p>
                          <div className="flex h-52 items-end justify-center">
                            <div className="flex h-full w-full max-w-[44px] items-end rounded-[18px] bg-white/75 px-1 pb-1 shadow-inner">
                              <div
                                className="w-full rounded-[14px] bg-gradient-to-t from-[#c96d3a] via-[#df8a53] to-[#f4c38b] shadow-[0_14px_30px_rgba(201,109,58,0.18)]"
                                style={{ height: entry.submissions > 0 ? `${Math.max(barHeight, 10)}%` : '4px' }}
                                title={`${entry.month}: ${entry.submissions} reports submitted`}
                              />
                            </div>
                          </div>
                          <p className="mt-3 truncate text-center text-xs font-semibold uppercase tracking-[0.16em] text-[#8b8177]">
                            {formatTrendLabel(entry.month, entry.label)}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading trend data...' : 'No trend data available yet.'}
                </p>
              )}
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
          <SectionCard
            title="Workflow Modules"
            description="Each researcher sidebar module owns a concrete step in the report-to-payout lifecycle."
            headerAlign="center"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[#e6ddd4]">
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">MODULE</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">LIVE SIGNAL</th>
                    <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">WORKFLOW ROLE</th>
                    <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  {workflowModules.map((item) => (
                    <tr key={item.module} className="border-b border-[#e6ddd4] last:border-0">
                      <td className="py-4 pr-4 font-semibold text-[#2d2a26]">{item.module}</td>
                      <td className="py-4 pr-4 text-[#6d6760]">{item.signal}</td>
                      <td className="py-4 pr-4 text-[#6d6760]">{item.workflow}</td>
                      <td className="py-4">
                        <Link
                          href={item.href}
                          className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                        >
                          {item.actionText}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>

          <SectionCard
            title="Operational Signals"
            description="Unread notifications, message pressure, and payout position from the linked workflow services."
            headerAlign="center"
          >
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Notifications</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : notificationsUnavailable ? 'Unavailable' : formatCompactNumber(unreadNotifications)}
                  </p>
                </div>
                <div className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Unread Messages</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : messagesUnavailable ? 'Unavailable' : formatCompactNumber(unreadMessages)}
                  </p>
                </div>
                <div className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Available Wallet</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                    {isLoading
                      ? '...'
                      : walletUnavailable
                        ? 'Unavailable'
                        : formatCurrency(wallet?.available_balance)}
                  </p>
                </div>
              </div>

              <div className="space-y-3 border-t border-[#e6ddd4] pt-4">
                {notificationsUnavailable ? (
                  <div className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
                    Notification service data is unavailable right now. Core report metrics still work; open the reports or messages modules directly if you need to continue workflow.
                  </div>
                ) : notifications.length ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b border-[#e6ddd4]">
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PRIORITY</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">ALERT</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">RECEIVED</th>
                          <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
                        </tr>
                      </thead>
                      <tbody>
                        {notifications.map((notification) => (
                          <tr key={notification.id} className="border-b border-[#e6ddd4] last:border-0">
                            <td className="py-4 pr-4">
                              <span
                                className={`rounded-full px-3 py-1 text-xs font-semibold ${getNotificationTone(
                                  notification.priority
                                )}`}
                              >
                                {formatMetricLabel(notification.priority || notification.type || 'update')}
                              </span>
                            </td>
                            <td className="py-4 pr-4">
                              <p className="font-semibold text-[#2d2a26]">{notification.title}</p>
                              <p className="mt-1 text-[#6d6760]">{notification.message}</p>
                            </td>
                            <td className="py-4 pr-4 text-[#6d6760]">{formatDateTime(notification.created_at)}</td>
                            <td className="py-4">
                              <Link
                                href={getNotificationHref(notification.type, notification.action_url)}
                                className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                              >
                                {notification.action_text || 'Open workflow'}
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-sm text-[#6d6760]">
                    {isLoading ? 'Loading notification feed...' : 'No unread notifications. Your dashboard is clear right now.'}
                  </p>
                )}
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <SectionCard
            title="Performance Focus"
            description="Researcher analytics from the dedicated performance service."
            headerAlign="center"
          >
            <div className="space-y-5">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">6-Month Success Rate</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : performance ? `${Math.round(performance.metrics.success_rate)}%` : 'Unavailable'}
                  </p>
                </div>
                <div className="rounded-2xl bg-[#faf6f1] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">6-Month Paid Earnings</p>
                  <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : performance ? formatCurrency(performance.metrics.earnings) : 'Unavailable'}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Severity Distribution</p>
                <div className="mt-4 space-y-3">
                  {Object.entries(performance?.severity_distribution || {}).map(([severity, count]) => {
                    const total = Object.values(performance?.severity_distribution || {}).reduce(
                      (sum, value) => sum + value,
                      0
                    );
                    const width = total ? (count / total) * 100 : 0;

                    return (
                      <div key={severity} className="grid grid-cols-[88px_minmax(0,1fr)_32px] items-center gap-3">
                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          {formatMetricLabel(severity)}
                        </span>
                        <div className="h-3 overflow-hidden rounded-full bg-[#f3ede6]">
                          <div
                            className={`h-full rounded-full ${severityTone[severity] ? severityTone[severity].split(' ')[0] : 'bg-[#c96d3a]'}`}
                            style={{ width: `${Math.max(width, count ? 10 : 0)}%` }}
                          />
                        </div>
                        <span className="text-right text-sm font-semibold text-[#2d2a26]">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="border-t border-[#e6ddd4] pt-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Top Vulnerability Types</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {(performance?.top_vulnerability_types || []).length ? (
                    performance?.top_vulnerability_types.map((entry) => (
                      <span
                        key={`${entry.type}-${entry.count}`}
                        className="rounded-full bg-[#edf5fb] px-3 py-2 text-xs font-semibold text-[#2d78a8]"
                      >
                        {entry.type || 'Unspecified'} · {entry.count}
                      </span>
                    ))
                  ) : (
                    <p className="text-sm text-[#6d6760]">
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

          <SectionCard
            title="Simulation Snapshot"
            description="Private training metrics from the simulation gateway stay visible only to you."
            headerAlign="center"
          >
            <div className="space-y-5">
              <div className="rounded-3xl bg-[#faf6f1] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Privacy Note</p>
                <p className="mt-3 text-sm leading-6 text-[#6d6760]">
                  {simulation?.privacy_note || 'Simulation scores stay private and are surfaced here only as personal progress signals.'}
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {simulationStatEntries.length ? (
                  simulationStatEntries.map((entry) => (
                    <div key={entry.key} className="rounded-2xl border border-[#e6ddd4] bg-white p-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                        {entry.label}
                      </p>
                      <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">{entry.value}</p>
                    </div>
                  ))
                ) : (
                <div className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-5 text-sm leading-6 text-[#6d6760] sm:col-span-2">
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
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
