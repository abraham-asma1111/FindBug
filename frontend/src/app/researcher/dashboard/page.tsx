'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import {
  formatCompactNumber,
  formatCurrency,
  getPortalNavItems,
} from '@/lib/portal';
import SectionCard from '@/components/dashboard/SectionCard';
import {
  type ResearcherDashboardData,
  type ResearcherSubmission,
  useResearcherDashboardData,
} from '@/hooks/useResearcherDashboardData';
import {
  buildResearcherDashboardAlerts,
  formatDashboardMetricLabel,
  ResearcherDashboardAlertsSection,
  ResearcherDashboardInsightsSection,
  ResearcherDashboardJumpboardSection,
} from '@/components/researcher/dashboard/ResearcherDashboardSections';
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

function getSubmissionWorkflow(submission?: ResearcherSubmission): {
  nextStep: string;
  actionLabel: string;
  href: string;
} {
  const detailHref = submission?.id ? `/researcher/reports/${submission.id}` : '/researcher/reports';

  switch (normalizeSubmissionStatus(submission?.status)) {
    case 'new':
      return {
        nextStep: 'Complete the evidence package and watch for first triage contact.',
        actionLabel: 'Open report',
        href: detailHref,
      };
    case 'triaged':
      return {
        nextStep: 'Review triage feedback and respond with clarifications or more proof.',
        actionLabel: 'Review triage',
        href: detailHref,
      };
    case 'valid':
      return {
        nextStep: 'Track remediation and bounty approval from the report detail flow.',
        actionLabel: 'Track payout',
        href: detailHref,
      };
    case 'invalid':
      return {
        nextStep: 'Read the decision carefully and capture lessons for your next submission.',
        actionLabel: 'Review notes',
        href: detailHref,
      };
    case 'closed':
      return {
        nextStep: 'Keep the final state as portfolio and earnings history.',
        actionLabel: 'View history',
        href: detailHref,
      };
    default:
      return {
        nextStep: 'Open the report workflow and inspect the current handoff state.',
        actionLabel: 'Open workflow',
        href: detailHref,
      };
  }
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
  const recentSubmissions = useMemo(() => {
    return [...(data?.recent_submissions ?? [])].sort((left, right) => {
      const leftTime = left.submitted_at ? new Date(left.submitted_at).getTime() : 0;
      const rightTime = right.submitted_at ? new Date(right.submitted_at).getTime() : 0;
      return rightTime - leftTime;
    });
  }, [data?.recent_submissions]);
  const filteredSubmissions = recentSubmissions.filter(
    (submission) => normalizeSubmissionStatus(submission.status) === activeTab
  );

  const unavailableWidgets = new Set(secondaryWarnings);
  const notificationsUnavailable = unavailableWidgets.has('notifications');
  const messagesUnavailable = unavailableWidgets.has('messages');
  const walletUnavailable = unavailableWidgets.has('wallet');
  const performanceUnavailable = unavailableWidgets.has('performance');
  const simulationUnavailable = unavailableWidgets.has('simulation');
  const reputationUnavailable = unavailableWidgets.has('reputation');

  const overview = data?.overview;
  const earnings = data?.earnings;
  const reputation = data?.reputation;
  const walletAvailable = wallet?.available_balance ?? 0;
  const totalSubmissions = overview?.total_submissions ?? 0;
  const activePrograms = overview?.active_programs ?? 0;
  const newSubmissionCount = overview?.submissions_by_status?.new ?? 0;
  const sixMonthSuccessRate = performance?.metrics?.success_rate ?? 0;
  const rank = myReputation?.rank_info?.rank ?? reputation?.rank ?? null;
  const percentile = myReputation?.rank_info?.percentile ?? reputation?.percentile ?? null;
  const alerts = buildResearcherDashboardAlerts({
    notifications,
    unreadMessages,
    walletAvailable,
    activePrograms,
    secondaryWarnings,
    isLoading,
    messagesUnavailable,
    walletUnavailable,
  });

  const workflowModules = [
    {
      href: '/researcher/engagements',
      module: 'Engagements',
      signal: isLoading ? 'Loading...' : `${formatCompactNumber(activePrograms)} active`,
      workflow: 'Discover programs, respond to invitations, and confirm where you are allowed to submit.',
      actionText: 'Open engagements',
      accent: 'from-[#103c37] via-[#175e55] to-[#23948c]',
    },
    {
      href: '/researcher/reports',
      module: 'Reports',
      signal: isLoading ? 'Loading...' : `${formatCompactNumber(newSubmissionCount)} awaiting progress`,
      workflow: 'Draft, submit, edit, comment on, and track the full report handoff into triage.',
      actionText: 'Open reports',
      accent: 'from-[#52212a] via-[#8e2430] to-[#ef2330]',
    },
    {
      href: '/researcher/earnings',
      module: 'Earnings',
      signal: isLoading
        ? 'Loading...'
        : walletUnavailable
          ? 'Service unavailable'
          : formatCurrency(walletAvailable),
      workflow: 'Inspect balance, payout requests, payout methods, and KYC blockers before cashing out.',
      actionText: 'Open earnings',
      accent: 'from-[#57411d] via-[#956226] to-[#d89b16]',
    },
    {
      href: '/researcher/simulation',
      module: 'Simulation',
      signal: simulationUnavailable ? 'Service unavailable' : 'Open workspace',
      workflow: 'Use training exercises to sharpen skills that feed back into live program results.',
      actionText: 'Open simulation',
      accent: 'from-[#1e2f52] via-[#2d78a8] to-[#6bb3d8]',
    },
    {
      href: '/researcher/analytics',
      module: 'Analytics',
      signal: performanceUnavailable ? 'Service unavailable' : `${Math.round(sixMonthSuccessRate)}% success`,
      workflow: 'Track historical output, severity mix, and long-term patterns in your findings.',
      actionText: 'Open analytics',
      accent: 'from-[#503b2c] via-[#8c6239] to-[#c96d3a]',
    },
    {
      href: '/researcher/reputation',
      module: 'Reputation',
      signal: isLoading ? 'Loading...' : rank ? `Rank #${rank}` : 'Unranked',
      workflow: 'Measure current standing, percentile, and competitive position in the researcher pool.',
      actionText: 'Open reputation',
      accent: 'from-[#3b2346] via-[#694175] to-[#9b6fb0]',
    },
    {
      href: '/researcher/messages',
      module: 'Messages',
      signal: messagesUnavailable ? 'Service unavailable' : `${formatCompactNumber(unreadMessages)} unread`,
      workflow: 'Keep conversation history close to the work: triage clarifications, organizer replies, and follow-up.',
      actionText: 'Open inbox',
      accent: 'from-[#28333d] via-[#405668] to-[#607d94]',
    },
  ];

  const primaryAction = !isLoading && activePrograms === 0
    ? {
        label: 'Next best action',
        title: 'Join a program before starting new live submissions',
        description: 'The roadmap puts discovery first. Pick a public program or accept an invitation to unlock direct report flow.',
        href: '/researcher/engagements',
        actionText: 'Review opportunities',
      }
    : !isLoading && newSubmissionCount > 0
      ? {
          label: 'Next best action',
          title: 'Advance your new reports into triage',
          description: 'Your newest submissions still need evidence follow-up or first triage contact.',
          href: '/researcher/reports',
          actionText: 'Continue reports',
        }
      : !isLoading && !messagesUnavailable && unreadMessages > 0
        ? {
            label: 'Next best action',
            title: 'Reply to pending workflow messages',
            description: 'Inbox pressure is the fastest way for a report to stall. Clear open questions from triage or organizations.',
            href: '/researcher/messages',
            actionText: 'Open inbox',
          }
        : !isLoading && !walletUnavailable && walletAvailable > 0
          ? {
              label: 'Next best action',
              title: 'Review payout readiness',
              description: 'You have available balance. Confirm payout method, KYC status, and withdrawal request details.',
              href: '/researcher/earnings',
              actionText: 'Open earnings',
            }
          : {
              label: 'Next best action',
              title: 'Keep momentum with practice or analytics',
              description: 'If the live queue is clear, use simulation and analytics to improve the next reporting cycle.',
              href: '/researcher/simulation',
              actionText: 'Open simulation',
            };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Researcher Dashboard"
          subtitle="Roadmap-aligned control center for engagements, reports, earnings, and training."
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

          <section className="rounded-[36px] border border-[#d8d0c8] bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(255,255,255,0.72)_35%,rgba(244,195,139,0.28)_75%),linear-gradient(135deg,#f7efe6_0%,#f6e8d3_45%,#efe1cf_100%)] p-6 shadow-sm sm:p-8">
            <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#8b8177]">
                  Researcher Dashboard
                </p>
                <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-[#2d2a26] sm:text-5xl">
                  Operate the discovery-to-payout workflow from one board.
                </h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-[#5f5851] sm:text-base">
                  The roadmap puts this page at the top of the researcher lifecycle: overview cards first,
                  then alerts, recent activity, and direct jumps into engagements, reports, earnings, analytics,
                  messages, reputation, and simulation.
                </p>

                <div className="mt-6 flex flex-wrap gap-3">
                  <Link
                    href="/researcher/engagements"
                    className="inline-flex rounded-full bg-[#2d2a26] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1f1c19]"
                  >
                    Review engagements
                  </Link>
                  <Link
                    href="/researcher/reports"
                    className="inline-flex rounded-full border border-[#c9beb1] bg-white/80 px-5 py-3 text-sm font-semibold text-[#2d2a26] transition hover:border-[#bcae9e] hover:bg-white"
                  >
                    Submit or track reports
                  </Link>
                  <Link
                    href="/researcher/earnings"
                    className="inline-flex rounded-full border border-[#c9beb1] bg-white/60 px-5 py-3 text-sm font-semibold text-[#2d2a26] transition hover:border-[#bcae9e] hover:bg-white"
                  >
                    Open earnings
                  </Link>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <div className="rounded-[28px] bg-[#2d2a26] p-5 text-white shadow-[0_18px_40px_rgba(45,42,38,0.2)]">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/70">Live Queue</p>
                  <p className="mt-3 text-3xl font-semibold">
                    {isLoading ? '...' : formatCompactNumber(newSubmissionCount + unreadMessages + unreadNotifications)}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-white/78">
                    Combined attention load from new submissions, unread messages, and unread notifications.
                  </p>
                </div>
                <div className="rounded-[28px] border border-[#ddd4cb] bg-white/80 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8b8177]">Wallet Ready</p>
                  <p className="mt-3 text-3xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : walletUnavailable ? 'Unavailable' : formatCurrency(walletAvailable)}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                    Available payout balance linked from the researcher earnings workflow.
                  </p>
                </div>
                <div className="rounded-[28px] border border-[#ddd4cb] bg-white/80 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8b8177]">Standing</p>
                  <p className="mt-3 text-3xl font-semibold text-[#2d2a26]">
                    {isLoading ? '...' : rank ? `#${rank}` : 'Private'}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                    {percentile !== null ? `Top ${Math.round(percentile)}% of ranked researchers.` : 'Open reputation for ranking detail.'}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
            <StatCard
              label="Total Submissions"
              value={isLoading ? '...' : formatCompactNumber(totalSubmissions)}
              helper="Lifetime reports submitted"
            />
            <StatCard
              label="Active Programs"
              value={isLoading ? '...' : formatCompactNumber(activePrograms)}
              helper="Joined programs and active tracks"
            />
            <StatCard
              label="Unread Alerts"
              value={isLoading ? '...' : notificationsUnavailable ? 'Unavailable' : formatCompactNumber(unreadNotifications)}
              helper="Unread notifications from linked services"
            />
            <StatCard
              label="Unread Messages"
              value={isLoading ? '...' : messagesUnavailable ? 'Unavailable' : formatCompactNumber(unreadMessages)}
              helper="Open workflow conversations"
            />
            <StatCard
              label="Available Wallet"
              value={isLoading ? '...' : walletUnavailable ? 'Unavailable' : formatCurrency(walletAvailable)}
              helper={`Pending ${formatCurrency(earnings?.pending_earnings ?? 0)}`}
            />
            <StatCard
              label="6-Month Success"
              value={isLoading ? '...' : performanceUnavailable ? 'Unavailable' : `${Math.round(sixMonthSuccessRate)}%`}
              helper={reputationUnavailable ? 'Performance service only' : `Rank ${rank || '-'} in researcher pool`}
            />
          </div>

          <div className="mt-6">
            <ResearcherDashboardAlertsSection alerts={alerts} isLoading={isLoading} />
          </div>

          <div className="mt-6">
            <SectionCard
              title="Recent Activity"
              description="Recent submission movement plus the current handoff status for each report."
              headerAlign="center"
            >
              <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
                <div>
                  <div className="mb-5 grid grid-cols-2 gap-3 border-b border-[#e6ddd4] pb-4 sm:grid-cols-5">
                    {submissionTabs.map((tab) => {
                      const isActive = tab === activeTab;

                      return (
                        <button
                          key={tab}
                          type="button"
                          onClick={() => setActiveTab(tab)}
                          className={`inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition ${
                            isActive
                              ? 'bg-[#ef2330] text-white'
                              : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
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
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">REPORT</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PROGRAM</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">SEVERITY</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
                          <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">NEXT STEP</th>
                          <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
                        </tr>
                      </thead>
                      <tbody>
                        {isLoading ? (
                          Array.from({ length: 4 }).map((_, index) => (
                            <tr key={`dashboard-loading-${index}`} className="border-b border-[#efe7de] last:border-0">
                              <td className="py-4 pr-4" colSpan={7}>
                                <div className="h-8 animate-pulse rounded-xl bg-[#f3ede6]" />
                              </td>
                            </tr>
                          ))
                        ) : filteredSubmissions.length ? (
                          filteredSubmissions.slice(0, 6).map((submission) => {
                            const workflow = getSubmissionWorkflow(submission);

                            return (
                              <tr key={submission.id || submission.report_number || submission.title} className="border-b border-[#e6ddd4] last:border-0">
                                <td className="py-3 pr-4 text-[#6d6760]">
                                  {submission.submitted_at
                                    ? new Date(submission.submitted_at).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric',
                                      })
                                    : '-'}
                                </td>
                                <td className="py-3 pr-4">
                                  <p className="font-medium text-[#2d2a26]">{submission.title}</p>
                                  <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[#8b8177]">
                                    {submission.report_number || 'No report number'}
                                  </p>
                                </td>
                                <td className="py-3 pr-4 text-[#6d6760]">{submission.program_name || '-'}</td>
                                <td className="py-3 pr-4">
                                  <span
                                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                      severityTone[(submission.assigned_severity || '').toLowerCase()] ||
                                      'bg-[#f3ede6] text-[#5f5851]'
                                    }`}
                                  >
                                    {submission.cvss_score
                                      ? `CVSS ${submission.cvss_score.toFixed(1)}`
                                      : formatDashboardMetricLabel(submission.assigned_severity || 'unscored')}
                                  </span>
                                </td>
                                <td className="py-3 pr-4">
                                  <span
                                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                      statusTone[normalizeSubmissionStatus(submission.status) || submission.status || ''] ||
                                      'bg-[#f3ede6] text-[#5f5851]'
                                    }`}
                                  >
                                    {formatSubmissionStatus(submission.status)}
                                  </span>
                                </td>
                                <td className="py-3 pr-4 text-[#6d6760]">{workflow.nextStep}</td>
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
                            <td colSpan={7} className="py-10 text-center">
                              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                                No recent activity
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
                </div>

                <div className="space-y-4">
                  <div className="rounded-[28px] bg-[#faf6f1] p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                      Submission Status Mix
                    </p>
                    <div className="mt-4 space-y-3">
                      {submissionTabs.map((tab) => (
                        <div key={`count-${tab}`} className="flex items-center justify-between rounded-2xl bg-white px-4 py-3">
                          <span className="text-sm font-semibold capitalize text-[#2d2a26]">{tab}</span>
                          <span className="text-sm font-semibold text-[#6d6760]">
                            {isLoading ? '...' : formatCompactNumber(overview?.submissions_by_status?.[tab] ?? 0)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-[28px] bg-[#2d2a26] p-5 text-white">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">
                      {primaryAction.label}
                    </p>
                    <h3 className="mt-4 text-2xl font-semibold leading-tight">{primaryAction.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-white/80">{primaryAction.description}</p>
                    <Link
                      href={primaryAction.href}
                      className="mt-5 inline-flex rounded-full bg-white px-5 py-3 text-sm font-semibold text-[#2d2a26] transition hover:bg-[#f5efe8]"
                    >
                      {primaryAction.actionText}
                    </Link>
                  </div>
                </div>
              </div>
            </SectionCard>
          </div>

          <div className="mt-6">
            <ResearcherDashboardJumpboardSection workflowModules={workflowModules} />
          </div>

          <ResearcherDashboardInsightsSection
            isLoading={isLoading}
            performanceUnavailable={performanceUnavailable}
            simulationUnavailable={simulationUnavailable}
            earnings={earnings}
            performance={performance}
            myReputation={myReputation}
            reputation={reputation}
            monthlyTrend={monthlyTrend}
            maxMonthlySubmissions={maxMonthlySubmissions}
            simulation={simulation}
          />
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
