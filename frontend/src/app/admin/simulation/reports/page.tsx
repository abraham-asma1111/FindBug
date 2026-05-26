'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import api from '@/lib/api';

export default function AdminSimulationReports() {
  const user = useAuthStore((state) => state.user);
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [score, setScore] = useState(88);
  const [xp, setXp] = useState(100);
  const [feedback, setFeedback] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/simulation/admin/reports?status=submitted');
      setReports(data.reports || []);
    } catch (err) {
      console.error('Failed to fetch reports', err);
    } finally {
      setLoading(false);
    }
  };

  const openReview = (report: any) => {
    setSelectedReport(report);
    setScore(report.score || 70);
    setXp(report.xp_awarded || 100);
    setFeedback(report.feedback || '');
    setIsValid(true);
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReport) return;
    setIsSubmitting(true);
    try {
      await api.put(`/simulation/admin/reports/${selectedReport.id}/review`, {
        is_valid: isValid,
        score,
        xp: isValid ? xp : 0,
        feedback,
      });
      setSelectedReport(null);
      fetchReports();
    } catch (err) {
      console.error('Failed to submit review', err);
      alert('Failed to submit review');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin', 'staff', 'triage_specialist']}>
      <PortalShell navItems={getPortalNavItems(user?.role ?? 'admin')} user={user!} title="Practice Reports Queue" subtitle="Review researcher submissions and award XP">
        <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-in fade-in duration-500">
          <div className="flex items-center gap-4 mb-6">
            <Link href="/admin/simulation" className="text-primary-500 hover:text-primary-400 text-sm font-medium">
              ← Back to Challenge Management
            </Link>
          </div>

          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white">Practice Reports Queue</h1>
            <p className="text-gray-400 mt-1">Pending simulation exploit reports from the academy.</p>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden shadow-sm">
            {loading ? (
              <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500" />
              </div>
            ) : reports.length === 0 ? (
              <div className="text-center py-32 bg-gray-900/30">
                <h3 className="text-xl font-medium text-white mb-2">Queue is Empty</h3>
                <p className="text-gray-500">No practice reports are waiting for review.</p>
              </div>
            ) : (
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-800/50 text-gray-400 uppercase text-xs">
                  <tr>
                    <th className="px-6 py-3">Challenge</th>
                    <th className="px-6 py-3">Researcher</th>
                    <th className="px-6 py-3">Title</th>
                    <th className="px-6 py-3">Auto score</th>
                    <th className="px-6 py-3">Submitted</th>
                    <th className="px-6 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {reports.map((r) => (
                    <tr key={r.id} className="border-t border-gray-800 hover:bg-gray-800/30">
                      <td className="px-6 py-4 text-white">{r.challenge_name}</td>
                      <td className="px-6 py-4 text-gray-400">{r.researcher_email || '—'}</td>
                      <td className="px-6 py-4 text-gray-300">{r.title}</td>
                      <td className="px-6 py-4 text-amber-400">{r.score ?? '—'}%</td>
                      <td className="px-6 py-4 text-gray-500">{r.submitted_at ? new Date(r.submitted_at).toLocaleString() : '—'}</td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => openReview(r)} className="px-4 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-medium">
                          Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {selectedReport && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
                <div className="p-6 border-b border-gray-800 flex justify-between items-center bg-gray-800/30">
                  <h2 className="text-xl font-bold text-white">Review Practice Report</h2>
                  <button type="button" onClick={() => setSelectedReport(null)} className="text-gray-400 hover:text-white">✕</button>
                </div>
                <div className="p-6 overflow-y-auto">
                  <p className="text-gray-500 text-sm mb-1">Challenge</p>
                  <p className="text-white font-medium mb-4">{selectedReport.challenge_name}</p>
                  <p className="text-gray-500 text-sm mb-1">Researcher</p>
                  <p className="text-gray-300 mb-4">{selectedReport.researcher_email}</p>
                  <p className="text-gray-500 text-sm mb-1">Steps / PoC</p>
                  <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4 text-gray-300 font-mono text-xs whitespace-pre-wrap mb-4 max-h-40 overflow-y-auto">
                    {selectedReport.steps_to_reproduce}
                    {'\n\n'}
                    {selectedReport.poc}
                  </pre>
                  {selectedReport.feedback && (
                    <>
                      <p className="text-gray-500 text-sm mb-1">Automated preview</p>
                      <pre className="bg-gray-950 border border-gray-800 rounded-lg p-3 text-gray-400 text-xs whitespace-pre-wrap mb-6">{selectedReport.feedback}</pre>
                    </>
                  )}
                  <form onSubmit={handleReviewSubmit} className="space-y-4 border-t border-gray-800 pt-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Verdict</label>
                        <select
                          value={isValid ? 'valid' : 'invalid'}
                          onChange={(e) => setIsValid(e.target.value === 'valid')}
                          className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white"
                        >
                          <option value="valid">Valid — award XP</option>
                          <option value="invalid">Invalid</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Score (0–100)</label>
                        <input type="number" min={0} max={100} value={score} onChange={(e) => setScore(Number(e.target.value))} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm text-emerald-400 mb-2 font-medium">XP to award</label>
                      <input type="number" value={xp} onChange={(e) => setXp(Number(e.target.value))} className="w-full bg-emerald-950/20 border border-emerald-500/30 rounded-lg px-4 py-2 text-emerald-400 font-bold" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Feedback</label>
                      <textarea rows={4} value={feedback} onChange={(e) => setFeedback(e.target.value)} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-3 text-white" />
                    </div>
                    <div className="flex justify-end gap-3">
                      <button type="button" onClick={() => setSelectedReport(null)} className="px-6 py-2.5 bg-gray-800 text-white rounded-lg">Cancel</button>
                      <button type="submit" disabled={isSubmitting} className="px-6 py-2.5 bg-primary-600 text-white rounded-lg disabled:opacity-50">
                        {isSubmitting ? 'Saving...' : 'Submit evaluation'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}
        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
