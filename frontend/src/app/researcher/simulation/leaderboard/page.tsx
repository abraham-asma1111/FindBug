'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import api from '@/lib/api';

export default function LeaderboardPage() {
  const user = useAuthStore((state) => state.user);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchLeaderboard(); }, []);

  const fetchLeaderboard = async () => {
    try { const res = await api.get('/simulation/leaderboard'); setLeaderboard(res.data.leaderboard); }
    catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const rankColor = (t: string) => {
    const m: Record<string, string> = { 'Newbie': 'text-gray-400', 'Learner': 'text-blue-400', 'Explorer': 'text-cyan-400', 'Bug Hunter': 'text-emerald-400', 'Security Researcher': 'text-purple-400', 'Elite Hacker': 'text-amber-400', 'Red Team Operator': 'text-red-500 font-bold' };
    return m[t] || m['Newbie'];
  };

  const posStyle = (r: number) => {
    if (r === 1) return 'bg-amber-500/20 border-amber-500/40 text-amber-400';
    if (r === 2) return 'bg-gray-300/20 border-gray-300/40 text-gray-300';
    if (r === 3) return 'bg-orange-700/20 border-orange-700/40 text-orange-500';
    return 'bg-gray-800/50 border-gray-700 text-gray-500';
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <Link href="/researcher/simulation" className="text-emerald-500 hover:text-emerald-400 text-sm">← Back to Catalog</Link>
        <h1 className="text-2xl font-bold text-white mt-3">Hall of Fame</h1>
        <p className="text-gray-500 text-sm mt-1">Top researchers ranked by total XP.</p>
      </div>

      <div className="bg-[#161616] border border-gray-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500"></div></div>
        ) : leaderboard.length === 0 ? (
          <div className="text-center py-20"><p className="text-gray-500">No researchers have earned XP yet.</p></div>
        ) : (
          <div className="divide-y divide-gray-800">
            {leaderboard.map((r) => (
              <div key={r.rank} className={`flex items-center p-5 hover:bg-gray-800/40 transition-colors ${r.username === user?.email ? 'bg-emerald-900/10' : ''}`}>
                <div className="w-14 flex justify-center">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold border ${posStyle(r.rank)}`}>{r.rank}</div>
                </div>
                <div className="flex-1 ml-3">
                  <span className="text-gray-200 font-semibold">{r.username}</span>
                  <div className={`text-sm mt-0.5 ${rankColor(r.rank_title)}`}>{r.rank_title}</div>
                </div>
                <div className="flex items-center gap-6 text-right">
                  <div><div className="text-[10px] text-gray-600 uppercase mb-0.5">Labs</div><div className="text-gray-300">{r.challenges_completed}</div></div>
                  <div className="w-20"><div className="text-[10px] text-emerald-600 uppercase mb-0.5">XP</div><div className="text-xl font-bold text-emerald-400">{r.xp}</div></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
