'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import PortalShell from '@/components/portal/PortalShell';
import api from '@/lib/api';
import { formatCurrency, formatDateTime, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface OrganizationProgram {
  id: string;
  name: string;
  description?: string | null;
  type: string;
  status: string;
  visibility: string;
  budget?: number | string | null;
  created_at?: string | null;
}

export default function OrganizationProgramsPage() {
  const user = useAuthStore((state) => state.user);
  const [programs, setPrograms] = useState<OrganizationProgram[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadPrograms = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/programs/my-programs');
        if (!cancelled) {
          setPrograms(response.data || []);
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load organization programs.');
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
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Program Portfolio"
          subtitle="Current organization-owned programs from `/programs/my-programs`, with creation and editing UI as the next vertical slice."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

        <SectionCard
          title="Owned Programs"
          description="The backend already exposes portfolio data; the next frontend slice is the program creation and edit workflow."
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
                    {program.description || 'Program description will surface in the next create/edit flow.'}
                  </p>
                  <div className="mt-4 grid gap-3 border-t border-[#eee6de] pt-4 text-sm md:grid-cols-2">
                    <div>
                      <p className="text-[#8b8177]">Budget</p>
                      <p className="mt-1 font-semibold text-[#2d2a26]">{formatCurrency(Number(program.budget || 0))}</p>
                    </div>
                    <div>
                      <p className="text-[#8b8177]">Created</p>
                      <p className="mt-1 font-semibold text-[#2d2a26]">{formatDateTime(program.created_at)}</p>
                    </div>
                  </div>
                </article>
              ))
            ) : (
              <p className="text-sm text-[#6d6760]">
                {isLoading ? 'Loading programs...' : 'No organization programs available yet.'}
              </p>
            )}
          </div>
        </SectionCard>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
