'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import api from '@/lib/api';

export default function AdminSimulationWriteups() {
  const user = useAuthStore((state) => state.user);
  const [solutions, setSolutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.documentElement.classList.add('dark');
    fetchSolutions();
  }, []);

  const fetchSolutions = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/simulation/admin/solutions?pending_only=true');
      setSolutions(data.solutions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const approve = async (id: string, approved: boolean) => {
    try {
      await api.put(`/simulation/admin/solutions/${id}/approve`, { is_approved: approved });
      fetchSolutions();
    } catch {
      alert('Failed to update writeup');
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin', 'staff', 'triage_specialist']}>
      <PortalShell navItems={getPortalNavItems(user?.role ?? 'admin')} user={user!} title="Community Writeups" subtitle="Moderate academy solutions">
        <div className="max-w-5xl mx-auto space-y-6 pb-12">
          <Link href="/admin/simulation" className="text-primary-500 hover:text-primary-400 text-sm">← Challenges</Link>
          <h1 className="text-2xl font-bold text-white">Pending Writeups</h1>

          {loading ? (
            <div className="flex justify-center py-16"><div className="animate-spin h-10 w-10 border-t-2 border-primary-500 rounded-full" /></div>
          ) : solutions.length === 0 ? (
            <p className="text-gray-500 py-12 text-center">No writeups awaiting approval.</p>
          ) : (
            <ul className="space-y-4">
              {solutions.map((s) => (
                <li key={s.id} className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
                  <div className="flex justify-between items-start gap-4 mb-3">
                    <div>
                      <h2 className="text-white font-medium">{s.title}</h2>
                      <p className="text-gray-500 text-xs mt-1">{s.challenge_name} · {s.author}</p>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button onClick={() => approve(s.id, true)} className="px-3 py-1.5 bg-emerald-600 text-white text-xs rounded-lg">Approve</button>
                      <button onClick={() => approve(s.id, false)} className="px-3 py-1.5 bg-gray-700 text-gray-300 text-xs rounded-lg">Reject</button>
                    </div>
                  </div>
                  {s.content && <pre className="text-gray-400 text-xs whitespace-pre-wrap bg-gray-950 p-3 rounded-lg border border-gray-800 max-h-48 overflow-y-auto">{s.content}</pre>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
