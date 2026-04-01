'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
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

interface TopEarnerEntry {
  rank: number;
  researcher_id: string;
  username: string;
  total_earnings: number;
  reputation_score: number;
}

export default function ResearcherReputationPage() {
  const user = useAuthStore((state) => state.user);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [topEarners, setTopEarners] = useState<TopEarnerEntry[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadLeaderboard = async () => {
      try {
        setIsLoading(true);
        const [leaderboardResponse, earnersResponse] = await Promise.all([
          api.get('/leaderboard', { params: { limit: 10 } }),
          api.get('/leaderboard/top-earners', { params: { limit: 5 } }),
        ]);

        if (!cancelled) {
          setLeaderboard(leaderboardResponse.data?.leaderboard || []);
          setTopEarners(earnersResponse.data?.top_earners || []);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load reputation data.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadLeaderboard();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Reputation"
          subtitle="Track your standing, credibility, and payout performance across the researcher community."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="grid gap-4 md:grid-cols-3">
          <StatCard
            label="Your Reputation"
            value={String(user.researcher?.reputation_score ?? 0)}
            helper="Current profile score"
          />
          <StatCard
            label="Your Rank"
            value={user.researcher?.rank ? `#${user.researcher.rank}` : 'Unranked'}
            helper="Current placement"
          />
          <StatCard
            label="Your Earnings"
            value={formatCurrency(user.researcher?.total_earnings)}
            helper="Total paid across accepted reports"
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(0,0.75fr)]">
          <SectionCard
            title="Top Researchers"
            description="Reputation-weighted leaderboard returned from `/leaderboard`."
          >
            <div className="space-y-3">
              {leaderboard.length ? (
                leaderboard.map((entry) => (
                  <div key={entry.researcher_id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">
                          #{entry.rank} {entry.username}
                        </p>
                        <p className="mt-1 text-sm text-[#6d6760]">
                          {entry.stats.total_reports} reports · {entry.stats.valid_reports} valid
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-[#2d2a26]">{entry.reputation_score.toFixed(1)} rep</p>
                        <p className="mt-1 text-xs text-[#8b8177]">{entry.stats.success_rate}% success</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading reputation rankings...' : 'No reputation data available.'}
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard
            title="Top Earners"
            description="Alternative ranking focused on payout performance."
          >
            <div className="space-y-3">
              {topEarners.length ? (
                topEarners.map((entry) => (
                  <div key={entry.researcher_id} className="rounded-2xl bg-[#faf6f1] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-[#2d2a26]">
                          #{entry.rank} {entry.username}
                        </p>
                        <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[#8b8177]">
                          Reputation {entry.reputation_score.toFixed(1)}
                        </p>
                      </div>
                      <p className="font-semibold text-[#2d2a26]">{formatCurrency(entry.total_earnings)}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading top earners...' : 'No top-earner data available.'}
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
