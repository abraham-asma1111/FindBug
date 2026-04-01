'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCompactNumber, formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface ResearcherSubmission {
  id?: string;
  report_number?: string;
  title: string;
  status?: string;
  assigned_severity?: string | null;
  submitted_at?: string | null;
  bounty_amount?: number | null;
  program_name?: string | null;
  cvss_score?: number | null;
}

interface ResearcherDashboardData {
  overview: {
    total_submissions: number;
    submissions_by_status: Record<string, number>;
    active_programs: number;
  };
  earnings: {
    total_earnings: number;
    pending_earnings: number;
    paid_earnings: number;
  };
  reputation: {
    score: number;
    rank: number;
    total_researchers: number;
    percentile: number;
  };
  recent_submissions: ResearcherSubmission[];
  monthly_trend: Array<{
    month: string;
    label?: string;
    submissions: number;
    earnings: number;
  }>;
}

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
  const [data, setData] = useState<ResearcherDashboardData | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<SubmissionTab>('new');

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/dashboard/researcher');
        if (!cancelled) {
          setData(response.data);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load researcher dashboard.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const monthlyTrend = buildTwelveMonthTrend(data?.monthly_trend ?? []);
  const maxMonthlySubmissions = monthlyTrend.reduce((highest, entry) => {
    return Math.max(highest, entry.submissions);
  }, 1);
  const recentSubmissions = data?.recent_submissions ?? [];
  const filteredSubmissions = recentSubmissions.filter(
    (submission) => normalizeSubmissionStatus(submission.status) === activeTab
  );

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
                    <th className="pb-3 font-semibold text-[#2d2a26]">STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    Array.from({ length: 4 }).map((_, index) => (
                      <tr key={`loading-${index}`} className="border-b border-[#efe7de] last:border-0">
                        <td className="py-4 pr-4" colSpan={7}>
                          <div className="h-8 animate-pulse rounded-xl bg-[#f3ede6]" />
                        </td>
                      </tr>
                    ))
                  ) : filteredSubmissions.length ? (
                    filteredSubmissions.map((submission) => (
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
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-10 text-center">
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
                  {data ? `${data.reputation.percentile}%` : '...'}
                </p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Paid Earnings</p>
                <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                  {isLoading ? '...' : formatCurrency(data?.earnings.paid_earnings)}
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
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
