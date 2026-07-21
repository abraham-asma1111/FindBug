'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

function formatLabel(value?: string | null): string {
  if (!value) {
    return 'Not specified';
  }

  return value
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getStatusTone(value?: string | null): string {
  switch (value?.toLowerCase()) {
    case 'public':
    case 'active':
      return 'bg-[#eef7ef] text-[#24613a]';
    case 'private':
    case 'draft':
    case 'pending':
      return 'bg-[#faf1e1] text-[#9a6412]';
    default:
      return 'bg-[#edf5fb] text-[#2d78a8]';
  }
}

export default function ResearcherProgramDetailPage() {
  const user = useAuthStore((state) => state.user);
  const params = useParams<{ programId: string }>();
  const programId = typeof params?.programId === 'string' ? params.programId : '';
  const [joiningProgramId, setJoiningProgramId] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');
  const [optimisticJoined, setOptimisticJoined] = useState(false);

  const {
    data: program,
    isLoading: isLoadingProgram,
    error: programError,
    refetch: refetchProgram,
  } = useApiQuery<any>(programId ? `/programs/${programId}` : '', {
    enabled: !!user && !!programId,
  });

  const {
    data: participations,
    isLoading: isLoadingParticipations,
    refetch: refetchParticipations,
  } = useApiQuery<any[]>(`/programs/my-participations`, {
    enabled: !!user,
  });

  const joinedFromServer = Boolean(
    participations?.some((entry) => {
      const entryProgramId = entry?.program?.id ?? entry?.program_id;
      return entryProgramId === programId;
    })
  );
  const isJoined = optimisticJoined || joinedFromServer;
  const scopes = Array.isArray(program?.scopes) ? program.scopes : [];
  const inScopeAssets = scopes.filter((scope: any) => scope?.is_in_scope);
  const outOfScopeAssets = scopes.filter((scope: any) => !scope?.is_in_scope);
  const rewardTiers = Array.isArray(program?.reward_tiers) ? program.reward_tiers : [];

  async function handleJoinProgram() {
    if (!programId || isJoined) {
      return;
    }

    try {
      setJoiningProgramId(programId);
      setActionError('');
      setActionSuccess('');

      await api.post(`/programs/${programId}/join`, {});
      setOptimisticJoined(true);
      setActionSuccess('You joined this program.');
      await Promise.all([refetchProgram(), refetchParticipations()]);
    } catch (err: any) {
      if (err.response?.status === 409) {
        setOptimisticJoined(true);
        setActionError('');
        setActionSuccess('You already joined this program.');
        await Promise.all([refetchProgram(), refetchParticipations()]);
        return;
      }

      setActionError(err.response?.data?.detail || 'Failed to join this program.');
    } finally {
      setJoiningProgramId(null);
    }
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Program Detail"
          subtitle="Review scope, rewards, and policy before testing or submitting a report."
          navItems={getPortalNavItems(user.role)}
        >
          <div className="space-y-6">
            {actionError ? (
              <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
                <p className="text-sm text-[#b42318]">{actionError}</p>
              </div>
            ) : null}

            {actionSuccess ? (
              <div className="rounded-2xl border border-[#b8dbbf] bg-[#eef7ef] p-4">
                <p className="text-sm text-[#24613a]">{actionSuccess}</p>
              </div>
            ) : null}

            {programError ? (
              <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4">
                <p className="text-sm text-[#b42318]">{programError.message}</p>
              </div>
            ) : null}

            {isLoadingProgram ? (
              <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6">
                <div className="flex items-center justify-center py-16">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                </div>
              </div>
            ) : !program ? (
              <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 text-center">
                <p className="text-sm text-[#8b8177]">Program not found</p>
              </div>
            ) : (
              <>
                <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 space-y-6">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <div className="flex flex-wrap gap-2">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusTone(program.status)}`}>
                          {formatLabel(program.status)}
                        </span>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusTone(program.visibility)}`}>
                          {formatLabel(program.visibility)}
                        </span>
                        <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                          {formatLabel(program.type)}
                        </span>
                      </div>

                      <div>
                        <h1 className="text-2xl font-bold text-[#2d2a26]">{program.name}</h1>
                        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6d6760]">
                          {program.description || 'No program description has been provided yet.'}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Link
                        href="/researcher/engagements"
                        className="inline-flex items-center rounded-full border border-[#d8d0c8] px-4 py-2 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#faf6f1]"
                      >
                        Back
                      </Link>
                      {isJoined ? (
                        <>
                          <button
                            type="button"
                            disabled
                            className="inline-flex cursor-default items-center rounded-full border border-[#b8dbbf] bg-[#eef7ef] px-4 py-2 text-sm font-semibold text-[#24613a]"
                          >
                            Joined
                          </button>
                          <Link
                            href={`/researcher/reports?programId=${encodeURIComponent(programId)}&contextLabel=${encodeURIComponent(program.name)}`}
                            className="inline-flex items-center rounded-full bg-[#ef2330] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
                          >
                            Report vulnerability
                          </Link>
                        </>
                      ) : (
                        <Button onClick={handleJoinProgram} disabled={joiningProgramId === programId || isLoadingParticipations}>
                          {joiningProgramId === programId ? 'Joining...' : 'Join program'}
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="grid gap-4 md:grid-cols-4 pt-6 border-t border-[#e6ddd4]">
                    <div>
                      <p className="text-xs text-[#8b8177] mb-1">Type</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">{formatLabel(program.type)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177] mb-1">Visibility</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">{formatLabel(program.visibility)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177] mb-1">Budget</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {program.budget ? formatCurrency(program.budget) : 'Not disclosed'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177] mb-1">Status</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {isJoined ? 'Joined' : 'Not joined'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid gap-6 xl:grid-cols-2">
                  <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h2 className="text-lg font-semibold text-[#2d2a26]">In-Scope Assets</h2>
                        <p className="mt-1 text-sm text-[#6d6760]">Assets you are allowed to test</p>
                      </div>
                      <span className="rounded-full bg-[#eef7ef] px-3 py-1 text-xs font-semibold text-[#24613a]">
                        {inScopeAssets.length}
                      </span>
                    </div>

                    {inScopeAssets.length ? (
                      <div className="space-y-3">
                        {inScopeAssets.map((scope: any) => (
                          <div key={scope.id} className="rounded-xl border border-[#e6ddd4] bg-[#fafafa] p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                              <p className="text-sm font-semibold text-[#2d2a26]">{scope.asset_identifier}</p>
                              <span className="rounded-full bg-[#eef7ef] px-2.5 py-0.5 text-xs font-semibold text-[#24613a]">
                                {formatLabel(scope.asset_type)}
                              </span>
                            </div>
                            {scope.description ? (
                              <p className="text-sm text-[#6d6760]">{scope.description}</p>
                            ) : null}
                            {scope.max_severity ? (
                              <p className="mt-2 text-xs text-[#8b8177]">
                                Max severity: {formatLabel(scope.max_severity)}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-sm text-[#8b8177]">No in-scope assets defined</p>
                      </div>
                    )}
                  </div>

                  <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h2 className="text-lg font-semibold text-[#2d2a26]">Out-of-Scope Assets</h2>
                        <p className="mt-1 text-sm text-[#6d6760]">Assets that should not be tested</p>
                      </div>
                      <span className="rounded-full bg-[#fff2f1] px-3 py-1 text-xs font-semibold text-[#b42318]">
                        {outOfScopeAssets.length}
                      </span>
                    </div>

                    {outOfScopeAssets.length ? (
                      <div className="space-y-3">
                        {outOfScopeAssets.map((scope: any) => (
                          <div key={scope.id} className="rounded-xl border border-[#e6ddd4] bg-[#fafafa] p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                              <p className="text-sm font-semibold text-[#2d2a26]">{scope.asset_identifier}</p>
                              <span className="rounded-full bg-[#fff2f1] px-2.5 py-0.5 text-xs font-semibold text-[#b42318]">
                                {formatLabel(scope.asset_type)}
                              </span>
                            </div>
                            {scope.description ? (
                              <p className="text-sm text-[#6d6760]">{scope.description}</p>
                            ) : null}
                            {scope.max_severity ? (
                              <p className="mt-2 text-xs text-[#8b8177]">
                                Max severity: {formatLabel(scope.max_severity)}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-sm text-[#8b8177]">No out-of-scope assets defined</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
                  <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 space-y-5">
                    <h2 className="text-lg font-semibold text-[#2d2a26]">Program Policy</h2>
                    <div className="space-y-5">
                      <div>
                        <h3 className="text-sm font-semibold text-[#2d2a26] mb-2">Rules of Engagement</h3>
                        <p className="text-sm text-[#6d6760] leading-relaxed whitespace-pre-wrap">
                          {program.rules_of_engagement || 'No rules of engagement have been published.'}
                        </p>
                      </div>
                      <div className="border-t border-[#e6ddd4] pt-5">
                        <h3 className="text-sm font-semibold text-[#2d2a26] mb-2">Safe Harbor</h3>
                        <p className="text-sm text-[#6d6760] leading-relaxed whitespace-pre-wrap">
                          {program.safe_harbor || 'No safe harbor statement has been published.'}
                        </p>
                      </div>
                      <div className="border-t border-[#e6ddd4] pt-5">
                        <h3 className="text-sm font-semibold text-[#2d2a26] mb-2">Security Policy</h3>
                        <p className="text-sm text-[#6d6760] leading-relaxed whitespace-pre-wrap">
                          {program.policy || 'No program policy has been published.'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] p-6 space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="text-lg font-semibold text-[#2d2a26]">Reward Tiers</h2>
                      <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                        {rewardTiers.length}
                      </span>
                    </div>

                    {rewardTiers.length ? (
                      <div className="space-y-2">
                        {rewardTiers.map((tier: any) => (
                          <div key={tier.id} className="rounded-xl border border-[#e6ddd4] bg-[#fafafa] p-4">
                            <div className="flex items-center justify-between gap-3">
                              <p className="text-sm font-semibold text-[#2d2a26]">{formatLabel(tier.severity)}</p>
                              <p className="text-sm font-semibold text-[#2d2a26]">
                                {formatCurrency(tier.min_amount)} - {formatCurrency(tier.max_amount)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-sm text-[#8b8177]">No reward tiers defined</p>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
