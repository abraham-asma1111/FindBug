'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { getPortalNavItems } from '@/lib/portal';
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
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load leaderboard data.');
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
  }, [selectedPeriod]);

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-[#ffd700] to-[#ffed4e] shadow-md">
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-[#2d2a26]">{rank}</span>
            <svg className="w-4 h-4 text-[#2d2a26] -mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
        </div>
      );
    } else if (rank === 2) {
      return (
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-[#c0c0c0] to-[#e8e8e8] shadow-md">
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-[#2d2a26]">{rank}</span>
            <svg className="w-4 h-4 text-[#2d2a26] -mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
        </div>
      );
    } else if (rank === 3) {
      return (
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-[#cd7f32] to-[#e8a87c] shadow-md">
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-white">{rank}</span>
            <svg className="w-4 h-4 text-white -mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
        </div>
      );
    } else {
      return (
        <div className="flex items-center justify-center w-12 h-12">
          <span className="text-base font-semibold text-[#6d6760]">{rank}th</span>
        </div>
      );
    }
  };

  const getRowBackground = (rank: number) => {
    if (rank === 1) return 'bg-[#fef9e7]';
    if (rank === 2) return 'bg-[#f5f5f5]';
    if (rank === 3) return 'bg-[#fef5e7]';
    return rank % 2 === 0 ? 'bg-white' : 'bg-[#fafafa]';
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Leaderboard"
          subtitle="Top researchers ranked by reputation score and contributions"
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

          {/* Header with Period Selector */}
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-[#2d2a26]">LEADERBOARD</h2>
            <div className="flex items-center gap-3">
              <button className="p-2 rounded-full hover:bg-[#f5f5f5] transition">
                <svg className="w-5 h-5 text-[#6d6760]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 rounded-lg border border-[#e6ddd4] bg-white text-sm font-medium text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#2d2a26] focus:border-transparent"
              >
                <option value="2026 - Q2">2026 - Q2</option>
                <option value="2026 - Q1">2026 - Q1</option>
                <option value="2025 - Q4">2025 - Q4</option>
                <option value="2025 - Q3">2025 - Q3</option>
                <option value="All Time">All Time</option>
              </select>
              <button className="p-2 rounded-full hover:bg-[#f5f5f5] transition">
                <svg className="w-5 h-5 text-[#6d6760]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Leaderboard Table */}
          <div className="rounded-2xl border border-[#e6ddd4] overflow-hidden bg-white shadow-sm">
            {/* Table Header */}
            <div className="grid grid-cols-[120px_1fr_120px] gap-4 px-6 py-4 bg-[#faf6f1] border-b border-[#e6ddd4]">
              <div className="text-xs font-bold uppercase tracking-wider text-[#6d6760]">RANK</div>
              <div className="text-xs font-bold uppercase tracking-wider text-[#6d6760]">HUNTER</div>
              <div className="text-xs font-bold uppercase tracking-wider text-[#6d6760] text-right">POINTS</div>
            </div>

            {/* Table Body */}
            <div>
              {isLoading ? (
                <div className="px-6 py-12 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#2d2a26]"></div>
                  <p className="mt-4 text-sm text-[#6d6760]">Loading leaderboard...</p>
                </div>
              ) : leaderboard.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <p className="text-sm text-[#6d6760]">No leaderboard data available.</p>
                </div>
              ) : (
                leaderboard.map((entry) => (
                  <div
                    key={entry.researcher_id}
                    className={`grid grid-cols-[120px_1fr_120px] gap-4 px-6 py-4 border-b border-[#e6ddd4] last:border-b-0 transition hover:bg-[#fcfaf7] ${getRowBackground(entry.rank)}`}
                  >
                    {/* Rank Badge */}
                    <div className="flex items-center">
                      {getRankBadge(entry.rank)}
                    </div>

                    {/* Hunter Info */}
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#2d2a26] to-[#6d6760] flex items-center justify-center text-white font-bold">
                        {entry.username.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-[#2d2a26] hover:underline cursor-pointer">
                          {entry.username}
                        </span>
                        <svg className="w-4 h-4 text-[#0ea5e9]" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>

                    {/* Points */}
                    <div className="flex items-center justify-end">
                      <span className="text-xl font-bold text-[#2d2a26]">
                        {Math.round(entry.reputation_score)}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Your Position Card */}
          {user.researcher && (
            <div className="mt-6 rounded-2xl border-2 border-[#2d2a26] bg-[#fcfaf7] p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#2d2a26] to-[#6d6760] flex items-center justify-center text-white font-bold text-lg">
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-wider text-[#8b8177]">Your Position</p>
                    <p className="text-lg font-bold text-[#2d2a26]">
                      {user.researcher.rank ? `#${user.researcher.rank}` : 'Unranked'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold uppercase tracking-wider text-[#8b8177]">Your Points</p>
                  <p className="text-2xl font-bold text-[#2d2a26]">
                    {Math.round(user.researcher.reputation_score || 0)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
