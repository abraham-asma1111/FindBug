'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface RecommendedProgram {
  program_id: string;
  program_name: string;
  program_type: string;
  budget?: number | null;
  organization_name?: string | null;
  match_score: number;
  reason: string;
}

interface ProgramListItem {
  id: string;
  name: string;
  description?: string | null;
  type: string;
  status: string;
  visibility: string;
  budget?: number | string | null;
}

export default function ResearcherEngagementsPage() {
  const user = useAuthStore((state) => state.user);
  const [recommended, setRecommended] = useState<RecommendedProgram[]>([]);
  const [programs, setPrograms] = useState<ProgramListItem[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadPrograms = async () => {
      try {
        setIsLoading(true);
        const [recommendedResponse, programsResponse] = await Promise.all([
          api.get('/recommendations/programs', { params: { limit: 6 } }),
          api.get('/programs', { params: { limit: 12 } }),
        ]);

        if (!cancelled) {
          setRecommended(recommendedResponse.data?.recommendations || []);
          setPrograms(programsResponse.data || []);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load researcher engagements.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadPrograms();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Engagements"
          subtitle="Discover active opportunities, track matching signals, and move from eligibility into real researcher participation."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <SectionCard
            title="Recommended Engagements"
            description="Opportunity matching signals from the backend recommendation service."
          >
            <div className="grid gap-4">
              {recommended.length ? (
                recommended.map((program) => (
                  <article key={program.program_id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                        {program.program_type}
                      </span>
                      <span className="rounded-full bg-[#fde9e7] px-3 py-1 text-xs font-semibold text-[#9d1f1f]">
                        {Math.round(program.match_score * 100)}% match
                      </span>
                    </div>
                    <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">{program.program_name}</h3>
                    <p className="mt-1 text-sm text-[#6d6760]">{program.organization_name || 'Organization pending'}</p>
                    <p className="mt-4 text-sm leading-6 text-[#6d6760]">{program.reason}</p>
                    <div className="mt-4 flex items-center justify-between gap-4">
                      <p className="text-sm text-[#6d6760]">Budget</p>
                      <p className="font-semibold text-[#2d2a26]">{formatCurrency(program.budget)}</p>
                    </div>
                  </article>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading recommended engagements...' : 'No recommended engagements available yet.'}
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard
            title="Open Engagements"
            description="Current program inventory surfaced through the researcher portal."
          >
            <div className="space-y-4">
              {programs.length ? (
                programs.map((program) => (
                  <article key={program.id} className="rounded-3xl border border-[#e6ddd4] bg-white p-5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                        {program.type}
                      </span>
                      <span className="rounded-full bg-[#faf1e1] px-3 py-1 text-xs font-semibold text-[#9a6412]">
                        {program.status}
                      </span>
                      <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                        {program.visibility}
                      </span>
                    </div>
                    <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">{program.name}</h3>
                    <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                      {program.description || 'Engagement detail content will expand as the new workflow tabs are added.'}
                    </p>
                    <div className="mt-4 flex items-center justify-between gap-4 border-t border-[#eee6de] pt-4 text-sm">
                      <span className="text-[#6d6760]">Maximum reward</span>
                      <span className="font-semibold text-[#2d2a26]">{formatCurrency(Number(program.budget || 0))}</span>
                    </div>
                  </article>
                ))
              ) : (
                <p className="text-sm text-[#6d6760]">
                  {isLoading ? 'Loading open engagements...' : 'No open engagements are available yet.'}
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
