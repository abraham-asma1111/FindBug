'use client';

import React, { Suspense, useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import { labsHubUrl } from '@/lib/simulation-lab';

type LabItem = {
  id: string;
  name: string;
  category: string;
  difficulty_level: string;
  points: number;
  user_status: string;
  lab_sandbox_path: string;
};

function LabsHubContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const focusFromUrl = searchParams.get('focus');

  const [labs, setLabs] = useState<LabItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [labReady, setLabReady] = useState(false);
  const [ensuring, setEnsuring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hubUrl, setHubUrl] = useState('');

  const loadMenu = useCallback(async () => {
    setError(null);
    try {
      const res = await api.get('/simulation/labs');
      const raw: LabItem[] = res.data.labs || [];
      const list = raw.filter(
        (lab, idx, arr) =>
          arr.findIndex((x) => x.lab_sandbox_path === lab.lab_sandbox_path) === idx
      );
      setLabs(list);
      setLabReady(!!res.data.lab_ready);
      setHubUrl(res.data.labs_hub_url || labsHubUrl());

      const defaultId =
        focusFromUrl ||
        res.data.default_focus_id ||
        list.find((l) => l.user_status === 'in_progress')?.id ||
        list[0]?.id ||
        null;
      setSelectedId(defaultId);
    } catch {
      router.push('/researcher/simulation');
    } finally {
      setLoading(false);
    }
  }, [focusFromUrl, router]);

  useEffect(() => {
    loadMenu();
  }, [loadMenu]);

  useEffect(() => {
    if (focusFromUrl && labs.some((l) => l.id === focusFromUrl)) {
      setSelectedId(focusFromUrl);
    }
  }, [focusFromUrl, labs]);

  const ensureLab = async () => {
    setEnsuring(true);
    setError(null);
    try {
      await api.post('/simulation/labs/ensure');
      setLabReady(true);
    } catch (e: any) {
      const d = e.response?.data?.detail;
      setError(
        typeof d === 'object' && d?.error
          ? d.error
          : 'Lab engine is not running. Run: docker compose -f simulation/docker-compose.yml up -d'
      );
    } finally {
      setEnsuring(false);
    }
  };

  const selectLab = async (lab: LabItem) => {
    setSelectedId(lab.id);
    if (lab.user_status === 'not_started') {
      try {
        await api.post(`/simulation/challenges/${lab.id}/start`);
        setLabs((prev) =>
          prev.map((l) =>
            l.id === lab.id ? { ...l, user_status: 'in_progress' } : l
          )
        );
      } catch {
        /* hub still works if engine already up */
      }
    }
  };

  const selected = labs.find((l) => l.id === selectedId);
  const accessLink = labsHubUrl(selectedId || focusFromUrl || undefined);

  if (loading) {
    return (
      <div className="flex justify-center py-32">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500" />
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 min-h-0 min-w-0 w-full overflow-hidden">
      <div className="shrink-0 px-4 sm:px-6 py-4 bg-[#111] border-b border-gray-800">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <Link href="/researcher/simulation" className="text-emerald-500 text-sm hover:text-emerald-400">
              ← Challenge catalog
            </Link>
            <h1 className="text-xl font-bold text-white mt-2">Academy Lab Environment</h1>
            <p className="text-gray-500 text-sm mt-1 max-w-xl">
              You can access your lab at this link. Pick any module from the menu — your{' '}
              <span className="text-blue-400">in progress</span> lab is selected by default.
            </p>
          </div>
          <div className="text-left sm:text-right min-w-[200px]">
            <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Your lab link</p>
            <p className="text-emerald-400 font-mono text-xs break-all">{accessLink}</p>
          </div>
        </div>

        {!labReady && (
          <div className="mt-4 p-3 rounded-lg bg-amber-950/30 border border-amber-700/40 flex flex-wrap items-center justify-between gap-3">
            <p className="text-amber-200 text-sm">Lab engine offline — start Docker compose first.</p>
            <button
              type="button"
              onClick={ensureLab}
              disabled={ensuring}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg disabled:opacity-50"
            >
              {ensuring ? 'Checking...' : 'Start lab engine'}
            </button>
          </div>
        )}
        {error && <p className="mt-3 text-red-400 text-xs">{error}</p>}
      </div>

      <div className="flex flex-1 min-h-0 min-w-0 overflow-hidden grid grid-cols-1 lg:grid-cols-[minmax(12rem,16rem)_minmax(0,1fr)]">
        <aside className="min-w-0 shrink-0 border-b lg:border-b-0 lg:border-r border-gray-800 bg-[#0d0d0d] overflow-y-auto max-h-48 lg:max-h-none">
          <p className="px-4 py-3 text-[10px] font-semibold text-gray-600 uppercase tracking-widest">
            All labs ({labs.length})
          </p>
          <ul className="pb-4">
            {labs.map((lab) => {
              const active = lab.id === selectedId;
              return (
                <li key={lab.id}>
                  <button
                    type="button"
                    onClick={() => selectLab(lab)}
                    className={`w-full text-left px-4 py-3 border-l-2 transition-colors ${
                      active
                        ? 'border-emerald-500 bg-emerald-500/10 text-white'
                        : 'border-transparent text-gray-400 hover:bg-gray-900 hover:text-gray-200'
                    }`}
                  >
                    <p className="text-sm font-medium truncate">{lab.name}</p>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-[10px] uppercase text-gray-600">{lab.difficulty_level}</span>
                      <span className="text-[10px] text-emerald-600">+{lab.points} XP</span>
                      {lab.user_status === 'in_progress' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                          In progress
                        </span>
                      )}
                      {lab.user_status === 'completed' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                          Solved
                        </span>
                      )}
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        <div className="flex flex-col min-h-0 min-w-0 overflow-hidden bg-[#0a0a0a]">
          {selected ? (
            <>
              <div className="shrink-0 px-4 py-2 border-b border-gray-800 flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm text-white font-medium truncate min-w-0">{selected.name}</p>
                <Link
                  href={`/researcher/simulation/${selected.id}`}
                  className="text-xs text-emerald-500 hover:text-emerald-400 shrink-0"
                >
                  Challenge details & report →
                </Link>
              </div>
              {labReady ? (
                <iframe
                  key={selected.lab_sandbox_path}
                  title={selected.name}
                  src={selected.lab_sandbox_path}
                  className="flex-1 w-full min-h-0 min-w-0 border-0"
                />
              ) : (
                <div className="flex-1 flex items-center justify-center p-8 text-center text-gray-500 text-sm">
                  Start the lab engine, then select a module again.
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
              Select a lab from the menu.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LabsHubPage() {
  return (
    <Suspense
      fallback={
        <div className="flex justify-center py-32">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500" />
        </div>
      }
    >
      <LabsHubContent />
    </Suspense>
  );
}
