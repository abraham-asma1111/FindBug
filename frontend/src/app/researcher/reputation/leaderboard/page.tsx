'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Spinner from '@/components/ui/Spinner';
import { api } from '@/lib/api';
import { formatCompactNumber, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

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

function getRankBadge(rank: number) {
  if (rank === 1) {
    return (
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#ffd700] to-[#ffed4e] shadow-md">
        <span className="text-lg font-bold text-[#2d2a26]">{rank}</span>
      </div>
    );
  }
  if (rank === 2) {
    return (
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#c0c0c0] to-[#e8e8e8] shadow-md">
        <span className="text-lg font-bold text-[#2d2a26]">{rank}</span>
      </div>
    );
  }
  if (rank === 3) {
    return (
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#cd7f32] to-[#e8a87c] shadow-md">
        <span className="text-lg font-bold text-white">{rank}</span>
      </div>
    );
  }
  return (
    <div className="flex h-12 w-12 items-center justify-center">
      <span className="text-base font-semibold text-[#6d6760] dark:text-gray-400">#{rank}</span>
    </div>
  );
}

function getRowBackground(rank: number) {
  if (rank === 1) return 'bg-[#fef9e7] dark:bg-amber-950/20';
  if (rank === 2) return 'bg-[#f5f5f5] dark:bg-gray-800/50';
  if (rank === 3) return 'bg-[#fef5e7] dark:bg-orange-950/20';
  return rank % 2 === 0 ? 'bg-white dark:bg-[#111111]' : 'bg-[#fcfaf7] dark:bg-gray-900/40';
}

export default function ResearcherLeaderboardPage() {
  const user = useAuthStore((state) => state.user);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('2026 - Q2');

  useEffect(() => {
    let cancelled = false;

    const loadLeaderboard = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/leaderboard', { params: { limit: 50 } });

        if (!cancelled) {
          setLeaderboard(response.data?.leaderboard || []);
          setError('');
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const message =
            err && typeof err === 'object' && 'response' in err
              ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
              : undefined;
          setError(message || 'Failed to load leaderboard data.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadLeaderboard();

    return () => {
      cancelled = true;
    };
  }, [selectedPeriod]);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Leaderboard"
          subtitle="Top researchers ranked by reputation score and validated contributions."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318] dark:border-red-900 dark:bg-red-950/30 dark:text-red-200">
              {error}
            </div>
          ) : null}

          <section className="mb-8 rounded-[32px] border border-[#d8cfc6] dark:border-gray-800 bg-[radial-gradient(circle_at_top_left,_rgba(239,35,48,0.12),_transparent_38%),linear-gradient(135deg,_#fffaf3,_#f5efe7)] dark:bg-[radial-gradient(circle_at_top_left,rgba(239,35,48,0.15),transparent_38%),linear-gradient(135deg,#1a1a1a,#151515)] p-6 shadow-sm lg:p-8">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#8b8177] dark:text-gray-400">
                  Global Rankings
                </p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight text-[#2d2a26] dark:text-gray-100">
                  See where you stand among the community
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-[#5f5851] dark:text-gray-300">
                  Rankings reflect reputation earned from validated reports. Climb by submitting high-quality
                  findings across bug bounty, PTaaS, and specialized engagements.
                </p>
                <Link
                  href="/researcher/reputation"
                  className="mt-5 inline-flex items-center rounded-full border border-[#d4c9be] bg-white px-5 py-2.5 text-sm font-semibold text-[#4f4943] transition hover:bg-[#faf3ea] dark:border-gray-700 dark:bg-[#111111] dark:text-gray-200 dark:hover:bg-gray-800"
                >
                  View my reputation
                </Link>
              </div>
              <div className="flex items-center gap-3">
                <label htmlFor="leaderboard-period" className="sr-only">
                  Leaderboard period
                </label>
                <select
                  id="leaderboard-period"
                  value={selectedPeriod}
                  onChange={(e) => setSelectedPeriod(e.target.value)}
                  className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2.5 text-sm font-medium text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2] dark:border-gray-700 dark:bg-[#111111] dark:text-gray-200"
                >
                  <option value="2026 - Q2">2026 - Q2</option>
                  <option value="2026 - Q1">2026 - Q1</option>
                  <option value="2025 - Q4">2025 - Q4</option>
                  <option value="2025 - Q3">2025 - Q3</option>
                  <option value="All Time">All Time</option>
                </select>
              </div>
            </div>
          </section>

          <div className="overflow-hidden rounded-[28px] border border-[#e6ddd4] bg-white shadow-sm dark:border-gray-800 dark:bg-[#111111]">
            <div className="grid grid-cols-[100px_1fr_120px] gap-4 border-b border-[#e6ddd4] bg-[#faf6f1] px-6 py-4 dark:border-gray-800 dark:bg-gray-900/60">
              <div className="text-xs font-bold uppercase tracking-wider text-[#6d6760] dark:text-gray-400">
                Rank
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-[#6d6760] dark:text-gray-400">
                Hunter
              </div>
              <div className="text-right text-xs font-bold uppercase tracking-wider text-[#6d6760] dark:text-gray-400">
                Points
              </div>
            </div>

            {isLoading ? (
              <div className="flex justify-center px-6 py-16">
                <Spinner size="lg" />
              </div>
            ) : leaderboard.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <p className="text-sm text-[#6d6760] dark:text-gray-400">No leaderboard data available.</p>
              </div>
            ) : (
              leaderboard.map((entry) => (
                <div
                  key={entry.researcher_id}
                  className={`grid grid-cols-[100px_1fr_120px] gap-4 border-b border-[#e6ddd4] px-6 py-4 transition last:border-b-0 hover:bg-[#fcfaf7] dark:border-gray-800 dark:hover:bg-gray-900/50 ${getRowBackground(entry.rank)}`}
                >
                  <div className="flex items-center">{getRankBadge(entry.rank)}</div>
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#2d2a26] to-[#6d6760] text-sm font-bold text-white">
                      {entry.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-[#2d2a26] dark:text-gray-100">
                        {entry.username}
                      </p>
                      <p className="text-xs text-[#8b8177] dark:text-gray-400">
                        {formatCompactNumber(entry.stats.valid_reports)} valid reports ·{' '}
                        {entry.stats.success_rate.toFixed(0)}% success
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-end">
                    <span className="text-xl font-bold text-[#2d2a26] dark:text-gray-100">
                      {Math.round(entry.reputation_score)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {user.researcher ? (
            <div className="mt-6 rounded-[28px] border-2 border-[#2d2a26] bg-[#fcfaf7] p-6 dark:border-gray-600 dark:bg-gray-900/60">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#2d2a26] to-[#6d6760] text-lg font-bold text-white">
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-[#8b8177] dark:text-gray-400">
                      Your position
                    </p>
                    <p className="text-lg font-bold text-[#2d2a26] dark:text-gray-100">
                      {user.researcher.rank ? `#${user.researcher.rank}` : 'Unranked'}
                    </p>
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <p className="text-xs font-semibold uppercase tracking-wider text-[#8b8177] dark:text-gray-400">
                    Your points
                  </p>
                  <p className="text-2xl font-bold text-[#2d2a26] dark:text-gray-100">
                    {Math.round(user.researcher.reputation_score || 0)}
                  </p>
                </div>
              </div>
            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
