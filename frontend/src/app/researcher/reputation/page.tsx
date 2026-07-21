'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import Spinner from '@/components/ui/Spinner';
import { api } from '@/lib/api';
import {
  formatCompactNumber,
  formatCurrency,
  getPortalNavItems,
} from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

type SeverityKey = 'critical' | 'high' | 'medium' | 'low';

interface ReputationStats {
  total_reports: number;
  valid_reports: number;
  invalid_reports: number;
  duplicate_reports: number;
  success_rate: number;
  by_severity: Record<SeverityKey, number>;
}

interface ResearcherProfileResponse {
  researcher_id: string;
  username?: string | null;
  bio?: string | null;
  reputation_score: number;
  rank?: number | null;
  total_earnings: number;
  stats?: ReputationStats;
  social?: {
    website?: string | null;
    github?: string | null;
    twitter?: string | null;
    linkedin?: string | null;
  };
}

interface ResearcherRankResponse {
  rank?: number | null;
  total_researchers: number;
  percentile: number;
  reputation_score: number;
}

interface MyReputationResponse {
  profile?: ResearcherProfileResponse;
  rank_info?: ResearcherRankResponse;
}

interface LeaderboardEntry {
  rank: number;
  researcher_id: string;
  username: string;
  reputation_score: number;
  total_earnings: number;
  stats: {
    total_reports: number;
    valid_reports: number;
    success_rate: number;
  };
}

interface TopEarnerEntry {
  rank: number;
  researcher_id: string;
  username: string;
  total_earnings: number;
  reputation_score: number;
}

interface ReputationWorkspaceState {
  myReputation: MyReputationResponse | null;
  publicProfile: ResearcherProfileResponse | null;
  publicRank: ResearcherRankResponse | null;
  leaderboard: LeaderboardEntry[];
  topEarners: TopEarnerEntry[];
  warnings: string[];
}

const INITIAL_WORKSPACE_STATE: ReputationWorkspaceState = {
  myReputation: null,
  publicProfile: null,
  publicRank: null,
  leaderboard: [],
  topEarners: [],
  warnings: [],
};

const SEVERITY_STYLES: Record<SeverityKey, { bar: string; text: string }> = {
  critical: { bar: 'bg-[#c2410c]', text: 'text-[#c2410c]' },
  high: { bar: 'bg-[#ea580c]', text: 'text-[#ea580c]' },
  medium: { bar: 'bg-[#d97706]', text: 'text-[#d97706]' },
  low: { bar: 'bg-[#65a30d]', text: 'text-[#65a30d]' },
};

const SCORING_RULES = [
  { label: 'Critical report accepted', points: 50, tone: 'bg-[#fce1da] text-[#a62d1f]' },
  { label: 'High severity accepted', points: 30, tone: 'bg-[#fde7d6] text-[#b45309]' },
  { label: 'Medium severity accepted', points: 20, tone: 'bg-[#fdf0d2] text-[#a16207]' },
  { label: 'Low severity accepted', points: 10, tone: 'bg-[#e8f4df] text-[#4d7c0f]' },
  { label: 'Invalid report', points: -20, tone: 'bg-[#fce3e6] text-[#b42318]' },
  { label: 'Duplicate after 24h', points: -20, tone: 'bg-[#f5e7ef] text-[#9f1239]' },
] as const;

const CONNECTED_PAGES = [
  {
    href: '/researcher/engagements',
    eyebrow: 'Engagements',
    title: 'Join work that raises your standing',
    description:
      'Live programs and PTaaS engagements feed directly into reputation when submissions are validated.',
    accent: 'from-[#fff2de] to-[#fff9f2]',
  },
  {
    href: '/researcher/reports',
    eyebrow: 'Reports',
    title: 'Translate findings into points',
    description:
      'Every high-quality report increases score. Drafts, submissions, and comments live here.',
    accent: 'from-[#ffe8e5] to-[#fff8f6]',
  },
  {
    href: '/researcher/analytics',
    eyebrow: 'Analytics',
    title: 'Understand the trend behind the score',
    description:
      'Use time periods, severity mix, and success rate tools to explain movement in leaderboard placement.',
    accent: 'from-[#eaf4ff] to-[#f8fbff]',
  },
  {
    href: '/researcher/earnings',
    eyebrow: 'Earnings',
    title: 'Follow reputation into payouts',
    description: 'Accepted work flows into wallet, withdrawal, and top-earner tracking.',
    accent: 'from-[#edf8ea] to-[#f8fcf7]',
  },
] as const;

function extractApiErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === 'object') {
    const axiosError = error as {
      response?: { data?: { detail?: string; message?: string } };
      message?: string;
    };
    if (typeof axiosError.response?.data?.detail === 'string') {
      return axiosError.response.data.detail;
    }
    if (typeof axiosError.response?.data?.message === 'string') {
      return axiosError.response.data.message;
    }
    if (typeof axiosError.message === 'string') {
      return axiosError.message;
    }
  }
  return fallback;
}

function formatRank(rank?: number | null): string {
  return rank ? `#${rank}` : 'Unranked';
}

function formatPercentile(percentile?: number | null): string {
  return percentile !== undefined && percentile !== null
    ? `${percentile.toFixed(1)}th percentile`
    : 'Not ranked yet';
}

function normalizeExternalUrl(value?: string | null): string | null {
  if (!value) {
    return null;
  }
  if (value.startsWith('http://') || value.startsWith('https://')) {
    return value;
  }
  return `https://${value}`;
}

export default function ResearcherReputationPage() {
  const user = useAuthStore((state) => state.user);
  const [workspace, setWorkspace] = useState<ReputationWorkspaceState>(INITIAL_WORKSPACE_STATE);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const loadWorkspace = useCallback(async () => {
    setIsLoading(true);
    let nextError = '';
    const nextState: ReputationWorkspaceState = {
      ...INITIAL_WORKSPACE_STATE,
      leaderboard: [],
      topEarners: [],
      warnings: [],
    };

    const [myReputationResult, leaderboardResult, topEarnersResult] = await Promise.allSettled([
      api.get<MyReputationResponse>('/my-reputation'),
      api.get('/leaderboard', { params: { limit: 10 } }),
      api.get('/leaderboard/top-earners', { params: { limit: 5 } }),
    ]);

    if (myReputationResult.status === 'fulfilled') {
      nextState.myReputation = myReputationResult.value.data ?? null;
    } else {
      nextError = extractApiErrorMessage(myReputationResult.reason, 'Failed to load your reputation data.');
      nextState.warnings.push('Personal reputation snapshot is unavailable.');
    }

    if (leaderboardResult.status === 'fulfilled') {
      nextState.leaderboard = leaderboardResult.value.data?.leaderboard || [];
    } else {
      nextState.warnings.push('Leaderboard is unavailable right now.');
    }

    if (topEarnersResult.status === 'fulfilled') {
      nextState.topEarners = topEarnersResult.value.data?.top_earners || [];
    } else {
      nextState.warnings.push('Top earners ranking is unavailable right now.');
    }

    const researcherId = nextState.myReputation?.profile?.researcher_id;
    if (researcherId) {
      const [profileResult, rankResult] = await Promise.allSettled([
        api.get<ResearcherProfileResponse>(`/researchers/${researcherId}/profile`),
        api.get<ResearcherRankResponse>(`/researchers/${researcherId}/rank`),
      ]);
      if (profileResult.status === 'fulfilled') {
        nextState.publicProfile = profileResult.value.data ?? null;
      } else {
        nextState.warnings.push('Public profile preview is unavailable.');
      }
      if (rankResult.status === 'fulfilled') {
        nextState.publicRank = rankResult.value.data ?? null;
      } else {
        nextState.warnings.push('Rank breakdown is unavailable.');
      }
    }

    if (!nextState.myReputation?.profile && !nextError) {
      nextError = 'Your reputation summary is temporarily unavailable.';
    }

    setError(nextError);
    setWorkspace(nextState);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  const profile = workspace.publicProfile ?? workspace.myReputation?.profile ?? null;
  const rankInfo = workspace.publicRank ?? workspace.myReputation?.rank_info ?? null;
  const stats = profile?.stats;
  const currentScore =
    profile?.reputation_score ?? workspace.myReputation?.rank_info?.reputation_score ?? 0;
  const currentRank = rankInfo?.rank ?? profile?.rank ?? null;
  const currentPercentile = rankInfo?.percentile ?? null;
  const totalResearchers = rankInfo?.total_researchers ?? 0;
  const leader = workspace.leaderboard[0];
  const cutoff = workspace.leaderboard[workspace.leaderboard.length - 1];
  const distanceToLeader =
    leader && currentScore < leader.reputation_score
      ? Math.max(0, leader.reputation_score - currentScore)
      : 0;
  const distanceToTopTen =
    cutoff && currentScore < cutoff.reputation_score
      ? Math.max(0, cutoff.reputation_score - currentScore)
      : 0;
  const severityEntries = useMemo(
    () => [
      { key: 'critical' as SeverityKey, label: 'Critical', count: stats?.by_severity?.critical ?? 0 },
      { key: 'high' as SeverityKey, label: 'High', count: stats?.by_severity?.high ?? 0 },
      { key: 'medium' as SeverityKey, label: 'Medium', count: stats?.by_severity?.medium ?? 0 },
      { key: 'low' as SeverityKey, label: 'Low', count: stats?.by_severity?.low ?? 0 },
    ],
    [stats]
  );
  const maxSeverityCount = Math.max(...severityEntries.map((entry) => entry.count), 1);
  const socialLinks = [
    { label: 'Website', url: normalizeExternalUrl(profile?.social?.website) },
    { label: 'GitHub', url: normalizeExternalUrl(profile?.social?.github) },
    { label: 'Twitter', url: normalizeExternalUrl(profile?.social?.twitter) },
    { label: 'LinkedIn', url: normalizeExternalUrl(profile?.social?.linkedin) },
  ].filter((entry): entry is { label: string; url: string } => Boolean(entry.url));

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Reputation"
          subtitle="See how validated work, report quality, and payouts fuel your public standing."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

          {workspace.warnings.length ? (
            <div className="mb-6 rounded-2xl border border-[#ecd8bf] bg-[#fff7ea] p-4 text-sm text-[#8a5b16]">
              {workspace.warnings.join(' ')}
            </div>
          ) : null}

          {isLoading ? (
            <div className="flex min-h-[420px] items-center justify-center rounded-[32px] border border-[#ddd4cb] bg-white">
              <Spinner size="lg" />
            </div>
          ) : (
            <div className="space-y-8">
              <section className="rounded-[32px] border border-[#d8cfc6] bg-[radial-gradient(circle_at_top_left,_rgba(239,35,48,0.16),_transparent_38%),linear-gradient(135deg,_#fffaf3,_#f5efe7)] p-6 shadow-sm lg:p-8">
                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_340px]">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#8b8177] dark:text-gray-400">
                      Researcher Standing
                    </p>
                    <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-[#2d2a26] dark:text-gray-100">
                      {profile?.username || user.fullName || 'Your'} reputation is the trust signal that
                      unlocks opportunities, payouts, and leaderboard recognition.
                    </h2>
                    <p className="mt-4 max-w-2xl text-sm leading-6 text-[#5f5851] dark:text-gray-300">
                      This workspace combines your authenticated reputation snapshot, the public leaderboard,
                      and the profile/rank endpoints described in the roadmap so you can understand every
                      angle of your score.
                    </p>
                    <div className="mt-6 flex flex-wrap gap-3">
                      <Link
                        href="#standing"
                        className="inline-flex items-center rounded-full bg-[#ef2330] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d81c29]"
                      >
                        Current standing
                      </Link>
                      <Link
                        href="#leaderboard"
                        className="inline-flex items-center rounded-full border border-[#d4c9be] bg-white dark:bg-[#111111] px-5 py-2.5 text-sm font-semibold text-[#4f4943] dark:text-gray-200 transition hover:bg-[#faf3ea] dark:hover:bg-gray-800"
                      >
                        Compare leaderboard
                      </Link>
                      <Link
                        href="#profile"
                        className="inline-flex items-center rounded-full border border-[#d4c9be] bg-white dark:bg-[#111111] px-5 py-2.5 text-sm font-semibold text-[#4f4943] dark:text-gray-200 transition hover:bg-[#faf3ea] dark:hover:bg-gray-800"
                      >
                        Public profile preview
                      </Link>
                      <button
                        type="button"
                        onClick={() => void loadWorkspace()}
                        className="inline-flex items-center rounded-full border border-[#d4c9be] bg-transparent px-5 py-2.5 text-sm font-semibold text-[#4f4943] dark:text-gray-200 transition hover:bg-white/80 dark:hover:bg-gray-800"
                      >
                        Refresh data
                      </button>
                    </div>
                  </div>
                  <div className="rounded-[28px] border border-[#eadfd5] bg-white/80 p-5 backdrop-blur dark:bg-gray-800/80 dark:border-gray-700">
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#8b8177] dark:text-gray-400">
                      Reputation status
                    </p>
                    <div className="mt-4 rounded-[24px] bg-[#2d2a26] p-5 text-white">
                      <p className="text-sm text-white/70">
                        {currentScore >= 100
                          ? 'Established signal'
                          : currentScore >= 50
                          ? 'Trusted trajectory'
                          : currentScore > 0
                          ? 'Early momentum'
                          : 'Building baseline'}
                      </p>
                      <p className="mt-3 text-4xl font-semibold tracking-tight">{currentScore.toFixed(1)}</p>
                      <p className="mt-2 text-sm text-white/75">
                        {formatRank(currentRank)} of {formatCompactNumber(totalResearchers || workspace.leaderboard.length)}
                      </p>
                    </div>
                    <div className="mt-4 space-y-3 rounded-[24px] bg-[#f8f2eb] p-4 dark:bg-gray-700">
                      <div className="flex items-center justify-between text-sm text-[#5f5851] dark:text-gray-300">
                        <span>Distance to leader</span>
                        <span className="font-semibold text-[#2d2a26] dark:text-gray-100">
                          {leader ? `${distanceToLeader.toFixed(1)} pts` : 'Unavailable'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-[#5f5851] dark:text-gray-300">
                        <span>Top 10 cutoff gap</span>
                        <span className="font-semibold text-[#2d2a26] dark:text-gray-100">
                          {cutoff ? `${distanceToTopTen.toFixed(1)} pts` : 'Unavailable'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-[#5f5851] dark:text-gray-300">
                        <span>Percentile</span>
                        <span className="font-semibold text-[#2d2a26] dark:text-gray-100">
                          {formatPercentile(currentPercentile)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <div id="standing" className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <StatCard
                  label="Reputation Score"
                  value={currentScore.toFixed(1)}
                  helper="Live score from your current researcher snapshot."
                />
                <StatCard
                  label="Global Rank"
                  value={formatRank(currentRank)}
                  helper="Placement across all ranked researchers."
                />
                <StatCard
                  label="Success Rate"
                  value={`${stats?.success_rate?.toFixed(1) ?? '0.0'}%`}
                  helper="Share of reports that reached valid/resolved."
                />
                <StatCard
                  label="Total Earnings"
                  value={formatCurrency(profile?.total_earnings)}
                  helper="Accepted bounties tied to your public data."
                />
              </div>

              <SectionCard
                title="Score Mechanics"
                description="Rules derived from BR-09/FREQ-11 that trigger when report status changes."
              >
                <div className="grid gap-3 md:grid-cols-2">
                  {SCORING_RULES.map((rule) => (
                    <div
                      key={rule.label}
                      className="rounded-[24px] border border-[#efe5dc] bg-[#fcfaf7] p-4 dark:bg-gray-800 dark:border-gray-700"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26] dark:text-gray-100">{rule.label}</p>
                          <p className="mt-1 text-sm text-[#6d6760] dark:text-gray-300">
                            Reputation moves when triage outcomes are marked valid, invalid, or duplicate.
                          </p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${rule.tone}`}>
                          {rule.points > 0 ? `+${rule.points}` : rule.points}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                title="Connected Workflow Pages"
                description="Jump straight to the module that feeds this reputation surface."
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  {CONNECTED_PAGES.map((page) => (
                    <Link
                      key={page.href}
                      href={page.href}
                      className={`group rounded-[28px] border border-[#e7ddd3] bg-gradient-to-br ${page.accent} p-5 transition hover:-translate-y-0.5 hover:border-[#d6c9bd] hover:shadow-sm dark:bg-gray-800 dark:border-gray-700`}
                    >
                      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#8b8177] dark:text-gray-400">
                        {page.eyebrow}
                      </p>
                      <h3 className="mt-3 text-xl font-semibold tracking-tight text-[#2d2a26] dark:text-gray-100">
                        {page.title}
                      </h3>
                      <p className="mt-3 text-sm leading-6 text-[#5f5851] dark:text-gray-300">{page.description}</p>
                      <span className="mt-5 inline-flex items-center text-sm font-semibold text-[#9d1f1f] dark:text-red-400 transition group-hover:translate-x-1">
                        Open page
                      </span>
                    </Link>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                title="Top Earners"
                description="Alternative leaderboard from `/leaderboard/top-earners`."
              >
                <div className="space-y-3">
                  {workspace.topEarners.length ? (
                    workspace.topEarners.map((entry) => {
                      const isCurrent = entry.researcher_id === profile?.researcher_id;
                      return (
                        <div
                          key={entry.researcher_id}
                          className={`rounded-[24px] p-4 ${
                            isCurrent ? 'bg-[#fff0ee] dark:bg-gray-800' : 'bg-[#faf6f1] dark:bg-gray-800'
                          }`}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <div className="flex flex-wrap items-center gap-2">
                                <p className="text-sm font-semibold text-[#2d2a26] dark:text-gray-100">
                                  #{entry.rank} {entry.username}
                                </p>
                                {isCurrent ? (
                                  <span className="rounded-full bg-[#fde9e7] px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#9d1f1f] dark:bg-red-900 dark:text-red-200">
                                    You
                                  </span>
                                ) : null}
                              </div>
                              <p className="mt-1 text-xs uppercase tracking-[0.18em] text-[#8b8177] dark:text-gray-400">
                                Reputation {entry.reputation_score.toFixed(1)}
                              </p>
                            </div>
                            <p className="text-sm font-semibold text-[#2d2a26] dark:text-gray-100">
                              {formatCurrency(entry.total_earnings)}
                            </p>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-sm text-[#6d6760]">No payout leaderboard entries are available right now.</p>
                  )}
                </div>
              </SectionCard>

              <div id="profile" className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                <SectionCard
                  title="Public Profile Preview"
                  description="Data sourced from `/researchers/{researcher_id}/profile`."
                >
                  <div className="space-y-5">
                    <div className="rounded-[28px] border border-[#ece3da] bg-[#fcfaf7] p-5">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                        Username
                      </p>
                      <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                        {profile?.username || 'Anonymous'}
                      </p>
                      <p className="mt-3 text-sm leading-6 text-[#6d6760]">
                        {profile?.bio?.trim() ||
                          'No public bio is set yet. Organizations only see your stats until you add one.'}
                      </p>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div className="rounded-[24px] bg-[#faf6f1] p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                          Public rank
                        </p>
                        <p className="mt-2 text-xl font-semibold text-[#2d2a26]">{formatRank(profile?.rank)}</p>
                      </div>
                      <div className="rounded-[24px] bg-[#faf6f1] p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                          Public earnings
                        </p>
                        <p className="mt-2 text-xl font-semibold text-[#2d2a26]">
                          {formatCurrency(profile?.total_earnings)}
                        </p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                        Public links
                      </p>
                      {socialLinks.length ? (
                        <div className="mt-3 flex flex-wrap gap-3">
                          {socialLinks.map((entry) => (
                            <a
                              key={entry.label}
                              href={entry.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center rounded-full border border-[#ddd4cb] bg-white dark:bg-[#111111] px-4 py-2 text-sm font-medium text-[#4f4943] dark:text-gray-200 transition hover:bg-[#faf3ea] dark:hover:bg-gray-800"
                            >
                              {entry.label}
                            </a>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-3 text-sm text-[#6d6760]">
                          No public social links are configured yet.
                        </p>
                      )}
                    </div>
                  </div>
                </SectionCard>
                <SectionCard
                  title="Report Quality Mix"
                  description="Severity distribution tied to the reputation history."
                >
                  <div className="space-y-5">
                    <div className="grid gap-3 sm:grid-cols-3">
                      <div className="rounded-[24px] bg-[#faf6f1] p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          Valid
                        </p>
                        <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                          {formatCompactNumber(stats?.valid_reports ?? 0)}
                        </p>
                      </div>
                      <div className="rounded-[24px] bg-[#faf6f1] p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          Invalid
                        </p>
                        <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                          {formatCompactNumber(stats?.invalid_reports ?? 0)}
                        </p>
                      </div>
                      <div className="rounded-[24px] bg-[#faf6f1] p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                          Duplicates
                        </p>
                        <p className="mt-2 text-2xl font-semibold text-[#2d2a26]">
                          {formatCompactNumber(stats?.duplicate_reports ?? 0)}
                        </p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      {severityEntries.map((entry) => (
                        <div key={entry.key}>
                          <div className="mb-2 flex items-center justify-between gap-3">
                            <p className={`text-sm font-semibold ${SEVERITY_STYLES[entry.key].text}`}>
                              {entry.label}
                            </p>
                            <p className="text-sm text-[#6d6760]">{entry.count} reports</p>
                          </div>
                          <div className="h-3 overflow-hidden rounded-full bg-[#efe7de]">
                            <div
                              className={`h-full rounded-full ${SEVERITY_STYLES[entry.key].bar}`}
                              style={{ width: `${(entry.count / maxSeverityCount) * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </SectionCard>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
