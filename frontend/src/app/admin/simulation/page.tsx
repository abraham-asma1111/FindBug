'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import api from '@/lib/api';

const emptyForm = {
  name: '',
  description: '',
  category: 'web',
  vulnerability_type: '',
  difficulty_level: 'beginner',
  severity: 'medium',
  points: 100,
  estimated_time_minutes: 30,
  docker_image: 'findbug/academy-lab',
  exposed_port: 5050,
  tutorial_video_url: '',
  documentation: '',
  expected_vulnerability_type: '',
  expected_severity: 'medium',
  validation_keywords: 'sql,injection',
  is_published: false,
};

export default function AdminSimulationPanel() {
  const user = useAuthStore((state) => state.user);
  const [challenges, setChallenges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
    fetchChallenges();
  }, []);

  const fetchChallenges = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/simulation/admin/challenges');
      setChallenges(data.challenges);
    } catch (err) {
      console.error('Failed to fetch challenges', err);
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (c: any) => {
    setEditingId(c.id);
    const kw = Array.isArray(c.validation_keywords) ? c.validation_keywords.join(',') : '';
    setForm({
      name: c.name || '',
      description: c.description || '',
      category: c.category || 'web',
      vulnerability_type: c.vulnerability_type || '',
      difficulty_level: c.difficulty_level || 'beginner',
      severity: c.severity || 'medium',
      points: c.points || 100,
      estimated_time_minutes: c.estimated_time_minutes || 30,
      docker_image: c.docker_image || '',
      exposed_port: c.exposed_port || 80,
      tutorial_video_url: c.tutorial_video_url || '',
      documentation: c.documentation || '',
      expected_vulnerability_type: c.expected_vulnerability_type || '',
      expected_severity: c.expected_severity || '',
      validation_keywords: kw,
      is_published: !!c.is_published,
    });
    setModalOpen(true);
  };

  const buildPayload = () => {
    const keywords = form.validation_keywords
      ? form.validation_keywords.split(',').map((k) => k.trim()).filter(Boolean)
      : [];
    return {
      ...form,
      points: Number(form.points),
      estimated_time_minutes: Number(form.estimated_time_minutes),
      exposed_port: Number(form.exposed_port),
      validation_keywords: keywords,
      hints: [],
      hint_costs: { '0': 0, '1': 5, '2': 10 },
    };
  };

  const saveChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = buildPayload();
      if (editingId) {
        await api.put(`/simulation/admin/challenges/${editingId}`, payload);
      } else {
        await api.post('/simulation/admin/challenges', payload);
      }
      setModalOpen(false);
      fetchChallenges();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const togglePublish = async (c: any) => {
    try {
      await api.put(`/simulation/admin/challenges/${c.id}`, { is_published: !c.is_published });
      fetchChallenges();
    } catch {
      alert('Failed to update publish status');
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'beginner': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'intermediate': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'advanced': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin', 'staff', 'triage_specialist']}>
      <PortalShell navItems={getPortalNavItems(user?.role ?? 'admin')} user={user!} title="Simulation Control" subtitle="Manage vulnerable labs and review submissions">
        <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-in fade-in duration-500">
          <div className="flex flex-wrap justify-between items-center gap-4 mb-8">
            <div>
              <h1 className="text-2xl font-bold text-white">Challenge Management</h1>
              <p className="text-gray-400 mt-1">Create labs, publish to the academy, and pull Docker images via <code className="text-xs text-gray-500">simulation/docker-compose.yml</code>.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/admin/simulation/reports" className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg border border-primary-500">
                Review Reports
              </Link>
              <Link href="/admin/simulation/writeups" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm font-medium rounded-lg border border-gray-700">
                Writeups
              </Link>
              <button type="button" onClick={openCreate} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg">
                + New Challenge
              </button>
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden shadow-sm">
            {loading ? (
              <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-400">
                  <thead className="bg-gray-800/50 text-xs uppercase text-gray-500 border-b border-gray-800">
                    <tr>
                      <th className="px-6 py-4 font-medium">Name</th>
                      <th className="px-6 py-4 font-medium">Category</th>
                      <th className="px-6 py-4 font-medium">Tier</th>
                      <th className="px-6 py-4 font-medium">XP</th>
                      <th className="px-6 py-4 font-medium">Published</th>
                      <th className="px-6 py-4 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {challenges.map((c) => (
                      <tr key={c.id} className="hover:bg-gray-800/30">
                        <td className="px-6 py-4 text-gray-200 font-medium">{c.name}</td>
                        <td className="px-6 py-4 uppercase text-xs">{c.category}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] border font-medium ${getDifficultyColor(c.difficulty_level)}`}>{c.difficulty_level}</span>
                        </td>
                        <td className="px-6 py-4 text-emerald-400">+{c.points}</td>
                        <td className="px-6 py-4">
                          {c.is_published ? (
                            <span className="text-emerald-400 text-xs">Live</span>
                          ) : (
                            <span className="text-gray-500 text-xs">Draft</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right space-x-3">
                          <button type="button" onClick={() => openEdit(c)} className="text-primary-400 hover:text-primary-300 text-xs font-medium">Edit</button>
                          <button type="button" onClick={() => togglePublish(c)} className="text-gray-400 hover:text-white text-xs font-medium">
                            {c.is_published ? 'Unpublish' : 'Publish'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {modalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-gray-800 flex justify-between">
                  <h2 className="text-xl font-bold text-white">{editingId ? 'Edit Challenge' : 'New Challenge'}</h2>
                  <button type="button" onClick={() => setModalOpen(false)} className="text-gray-400">✕</button>
                </div>
                <form onSubmit={saveChallenge} className="p-6 space-y-4">
                  <input required placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
                  <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
                  <div className="grid grid-cols-2 gap-3">
                    <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
                      <option value="web">web</option>
                      <option value="api">api</option>
                      <option value="auth">auth</option>
                    </select>
                    <select value={form.difficulty_level} onChange={(e) => setForm({ ...form, difficulty_level: e.target.value })} className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
                      <option value="beginner">beginner</option>
                      <option value="intermediate">intermediate</option>
                      <option value="advanced">advanced</option>
                    </select>
                  </div>
                  <input placeholder="Docker image (findbug/academy-lab)" required value={form.docker_image} onChange={(e) => setForm({ ...form, docker_image: e.target.value })} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm font-mono" />
                  <div className="grid grid-cols-3 gap-3">
                    <input type="number" placeholder="Port" value={form.exposed_port} onChange={(e) => setForm({ ...form, exposed_port: Number(e.target.value) })} className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm" />
                    <input type="number" placeholder="XP" value={form.points} onChange={(e) => setForm({ ...form, points: Number(e.target.value) })} className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm" />
                    <input type="number" placeholder="Minutes" value={form.estimated_time_minutes} onChange={(e) => setForm({ ...form, estimated_time_minutes: Number(e.target.value) })} className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm" />
                  </div>
                  <input placeholder="YouTube embed URL" value={form.tutorial_video_url} onChange={(e) => setForm({ ...form, tutorial_video_url: e.target.value })} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
                  <input placeholder="Expected vuln type (sql_injection)" value={form.expected_vulnerability_type} onChange={(e) => setForm({ ...form, expected_vulnerability_type: e.target.value })} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
                  <input placeholder="Validation keywords (comma-separated)" value={form.validation_keywords} onChange={(e) => setForm({ ...form, validation_keywords: e.target.value })} className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
                  <label className="flex items-center gap-2 text-sm text-gray-300">
                    <input type="checkbox" checked={form.is_published} onChange={(e) => setForm({ ...form, is_published: e.target.checked })} />
                    Publish to academy catalog
                  </label>
                  <div className="flex justify-end gap-3 pt-2">
                    <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 bg-gray-800 text-white rounded-lg text-sm">Cancel</button>
                    <button type="submit" disabled={saving} className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm disabled:opacity-50">{saving ? 'Saving...' : 'Save'}</button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </PortalShell>
    </ProtectedRoute>
  );
}
