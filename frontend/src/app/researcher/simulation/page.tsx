'use client';

import React, { Suspense, useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import api from '@/lib/api';

type Challenge = {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty_level: string;
  points: number;
  estimated_time_minutes: number;
  user_status: string;
};

function SimulationCatalogContent() {
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [dockerAvailable, setDockerAvailable] = useState(false);

  const tierFromUrl = searchParams.get('difficulty') || 'all';
  const categoryFromUrl = searchParams.get('category');
  const [activeTier, setActiveTier] = useState(tierFromUrl);

  useEffect(() => {
    setActiveTier(tierFromUrl);
  }, [tierFromUrl]);

  useEffect(() => {
    fetchChallenges();
  }, [activeTier, categoryFromUrl]);

  const fetchChallenges = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (activeTier !== 'all') params.set('difficulty', activeTier);
      if (categoryFromUrl) params.set('category', categoryFromUrl);
      const qs = params.toString();
      const { data } = await api.get(`/simulation/challenges${qs ? `?${qs}` : ''}`);
      setChallenges(data.challenges);
      setDockerAvailable(!!data.docker_available);
    } catch (err) {
      console.error('Failed to fetch challenges', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'beginner': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'intermediate': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'advanced': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getStatusBadge = (status: string) => {
    if (status === 'completed') {
      return <span className="px-2 py-1 text-xs rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">SOLVED</span>;
    }
    if (status === 'in_progress') {
      return <span className="px-2 py-1 text-xs rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">IN PROGRESS</span>;
    }
    return null;
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight mb-2">Challenge Catalog</h1>
        <p className="text-gray-500 text-sm">
          Select a vulnerable environment below to begin. Each lab is isolated and contains a real vulnerability to exploit.
        </p>
        {!dockerAvailable && (
          <p className="text-amber-500/90 text-xs mt-2">
            Docker is offline — labs use sandbox URLs until Docker is running on the server.
          </p>
        )}
        {categoryFromUrl && (
          <p className="text-emerald-400/80 text-xs mt-2">
            Filtered by category: <span className="font-mono">{categoryFromUrl}</span>
            {' '}
            <Link href="/researcher/simulation" className="underline hover:text-emerald-300">Clear</Link>
          </p>
        )}
      </div>

      <div className="flex space-x-1 bg-gray-900/50 rounded-lg p-1 border border-gray-800">
        {['all', 'beginner', 'intermediate', 'advanced'].map((tier) => (
          <Link
            key={tier}
            href={tier === 'all' && !categoryFromUrl ? '/researcher/simulation' : `/researcher/simulation?difficulty=${tier}${categoryFromUrl ? `&category=${categoryFromUrl}` : ''}`}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all text-center ${
              activeTier === tier
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
          >
            {tier === 'all' ? 'All Tiers' : tier.charAt(0).toUpperCase() + tier.slice(1)}
          </Link>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      ) : challenges.length === 0 ? (
        <div className="text-center py-20 bg-gray-900/30 rounded-xl border border-gray-800 border-dashed">
          <p className="text-gray-500">No challenges found. Run the simulation seed script if the catalog is empty.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {challenges.map((c) => (
            <Link key={c.id} href={`/researcher/simulation/${c.id}`}>
              <div className="group bg-[#161616] border border-gray-800/60 rounded-xl p-5 hover:border-emerald-500/40 transition-all duration-300 h-full flex flex-col cursor-pointer hover:shadow-lg hover:shadow-emerald-900/10">
                <div className="flex justify-between items-start mb-3">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border uppercase tracking-widest ${getDifficultyColor(c.difficulty_level)}`}>
                    {c.difficulty_level}
                  </span>
                  {getStatusBadge(c.user_status)}
                </div>
                <h3 className="text-lg font-semibold text-gray-100 mb-1.5 group-hover:text-emerald-400 transition-colors">{c.name}</h3>
                <p className="text-sm text-gray-500 mb-5 flex-grow line-clamp-2">{c.description}</p>
                <div className="flex items-center justify-between pt-3 border-t border-gray-800/60 text-xs">
                  <div className="flex items-center gap-3">
                    <span className="text-emerald-400 font-bold">+{c.points} XP</span>
                    <span className="text-gray-600">|</span>
                    <span className="text-gray-500 uppercase tracking-wide">{c.category}</span>
                  </div>
                  <span className="text-gray-600">{c.estimated_time_minutes} min</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function SimulationCatalogPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500" /></div>}>
      <SimulationCatalogContent />
    </Suspense>
  );
}
