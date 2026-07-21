'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import api from '@/lib/api';

export default function MyProgressPage() {
  const [stats, setStats] = useState<any>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [s, r] = await Promise.all([api.get('/simulation/my-progress'), api.get('/simulation/my-reports')]);
      setStats(s.data); setReports(r.data.reports);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const getRankStyle = (title: string) => {
    const m: Record<string, string> = {
      'Newbie': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      'Learner': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'Explorer': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      'Bug Hunter': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      'Security Researcher': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'Elite Hacker': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'Red Team Operator': 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    return m[title] || m['Newbie'];
  };

  const statusBadge = (s: string) => {
    if (s === 'validated') return <span className="px-2 py-0.5 text-[10px] rounded border bg-emerald-500/20 text-emerald-400 border-emerald-500/30">VALIDATED</span>;
    if (s === 'invalid') return <span className="px-2 py-0.5 text-[10px] rounded border bg-red-500/20 text-red-400 border-red-500/30">INVALID</span>;
    return <span className="px-2 py-0.5 text-[10px] rounded border bg-amber-500/20 text-amber-400 border-amber-500/30">PENDING</span>;
  };

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500"></div></div>;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <Link href="/researcher/simulation" className="text-emerald-500 hover:text-emerald-400 text-sm">← Back to Catalog</Link>
        <h1 className="text-2xl font-bold text-white mt-3">My Progress</h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#161616] border border-gray-800 rounded-xl p-5 text-center">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2">Rank</p>
          <span className={`px-3 py-1 rounded-lg border text-sm font-medium ${getRankStyle(stats?.rank_title)}`}>{stats?.rank_title || 'Newbie'}</span>
        </div>
        <div className="bg-[#161616] border border-gray-800 rounded-xl p-5">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2">XP Earned</p>
          <p className="text-3xl font-bold text-emerald-400">{stats?.xp_earned ?? stats?.xp ?? 0}</p>
          {(stats?.xp_spent_on_hints ?? 0) > 0 && (
            <p className="text-[10px] text-gray-500 mt-1">
              Balance {stats.xp_balance} · {stats.xp_spent_on_hints} spent on hints
            </p>
          )}
        </div>
        <div className="bg-[#161616] border border-gray-800 rounded-xl p-5">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2">Solved</p>
          <p className="text-3xl font-bold text-white">{stats?.challenges_completed || 0}</p>
        </div>
        <div className="bg-[#161616] border border-gray-800 rounded-xl p-5">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2">Streak</p>
          <p className="text-3xl font-bold text-amber-400">{stats?.current_streak || 0}</p>
        </div>
      </div>

      <div className="bg-[#161616] border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-gray-800">
          <h2 className="text-lg font-semibold text-white">Practice Reports</h2>
          <p className="text-xs text-gray-500 mt-1">Submitted exploits and awarded XP</p>
        </div>
        {reports.length === 0 ? (
          <div className="p-12 text-center text-gray-500 text-sm">No reports submitted yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-400">
              <thead className="bg-gray-800/50 text-[10px] uppercase text-gray-500">
                <tr>
                  <th className="px-5 py-3">Challenge</th><th className="px-5 py-3">Title</th>
                  <th className="px-5 py-3">Status</th><th className="px-5 py-3">Score</th>
                  <th className="px-5 py-3">XP</th><th className="px-5 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-800/30">
                    <td className="px-5 py-3 text-gray-300 font-medium">{r.challenge_name}</td>
                    <td className="px-5 py-3 text-gray-400 truncate max-w-[180px]">{r.title}</td>
                    <td className="px-5 py-3">{statusBadge(r.status)}</td>
                    <td className="px-5 py-3">{r.score > 0 ? `${r.score}%` : '-'}</td>
                    <td className="px-5 py-3"><span className={r.xp_awarded > 0 ? 'text-emerald-400 font-medium' : 'text-gray-600'}>{r.xp_awarded > 0 ? `+${r.xp_awarded}` : '-'}</span></td>
                    <td className="px-5 py-3 text-gray-500">{new Date(r.submitted_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
