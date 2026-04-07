'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems, formatCurrency, formatDateTime } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import RewardEditModal from '@/components/organization/programs/RewardEditModal';
import ScopeAddModal from '@/components/organization/programs/ScopeAddModal';

export default function ProgramDetailPage() {
  const params = useParams();
  const user = useAuthStore((state) => state.user);
  const programId = params.id as string;
  const [activeTab, setActiveTab] = useState('overview');
  const [showRewardEditModal, setShowRewardEditModal] = useState(false);
  const [showScopeAddModal, setShowScopeAddModal] = useState(false);

  // Fetch program details
  const { data: program, isLoading, error, refetch } = useApiQuery(`/programs/${programId}`, {
    enabled: !!user && !!programId,
  });

  // Fetch scopes
  const { data: scopes, refetch: refetchScopes } = useApiQuery(`/programs/${programId}/scopes`, {
    enabled: activeTab === 'scope',
  });

  // Fetch rewards
  const { data: rewards, refetch: refetchRewards } = useApiQuery(`/programs/${programId}/rewards`, {
    enabled: activeTab === 'rewards',
  });

  // Mutations
  const { mutate: publishProgram, isLoading: isPublishing } = useApiMutation(
    `/programs/${programId}/publish`,
    'POST',
    { 
      onSuccess: () => {
        alert('Program published successfully!');
        refetch();
      },
    }
  );

  const { mutate: pauseProgram, isLoading: isPausing } = useApiMutation(
    `/programs/${programId}/pause`,
    'POST',
    { 
      onSuccess: () => {
        alert('Program paused successfully!');
        refetch();
      },
    }
  );

  const { mutate: resumeProgram, isLoading: isResuming } = useApiMutation(
    `/programs/${programId}/resume`,
    'POST',
    { 
      onSuccess: () => {
        alert('Program resumed successfully!');
        refetch();
      },
    }
  );

  const { mutate: closeProgram, isLoading: isClosing } = useApiMutation(
    `/programs/${programId}/close`,
    'POST',
    { 
      onSuccess: () => {
        alert('Program closed successfully!');
        refetch();
      },
    }
  );

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="Loading..."
            subtitle="Please wait"
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-gray-900 dark:border-slate-700 dark:border-t-slate-100"></div>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (error || !program) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="Program Not Found"
            subtitle="The program you're looking for doesn't exist"
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
              <p className="text-sm text-red-800 dark:text-red-200">
                {error?.message || 'Program not found'}
              </p>
            </div>
            <div className="mt-6">
              <Link href="/organization/programs">
                <Button>Back to Programs</Button>
              </Link>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Program description' },
    { id: 'scope', label: 'Scope' },
    { id: 'rewards', label: 'Rewards' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title={program.name}
          subtitle={program.type?.toUpperCase() || 'PROGRAM'}
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {/* Back Button */}
          <div className="mb-6">
            <Link
              href="/organization/programs"
              className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Programs
            </Link>
          </div>

          {/* Professional Tab Navigation */}
          <div className="mb-8 border-b border-gray-200 dark:border-slate-700">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'border-red-600 text-red-600 dark:border-red-500 dark:text-red-400'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-slate-400 dark:hover:border-slate-600 dark:hover:text-slate-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="space-y-12">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <>
                {/* Status Badges */}
                <section>
                  <div className="flex flex-wrap items-center gap-3">
                    <span className={`inline-flex items-center rounded-md px-3 py-1 text-xs font-bold uppercase ${
                      program.type === 'bounty' 
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' 
                        : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                    }`}>
                      {program.type}
                    </span>
                    <span className={`inline-flex items-center rounded-md px-3 py-1 text-xs font-bold uppercase ${
                      program.status === 'public' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : program.status === 'draft'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : program.status === 'paused'
                        ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                      {program.status}
                    </span>
                    <span className="inline-flex items-center rounded-md bg-gray-100 px-3 py-1 text-xs font-bold uppercase text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                      {program.visibility}
                    </span>
                  </div>
                </section>

                {/* Program Info Grid */}
                <section className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Budget</p>
                    <p className="mt-2 text-lg font-semibold text-gray-900 dark:text-slate-100">
                      {program.budget ? formatCurrency(program.budget) : 'Not set'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Created</p>
                    <p className="mt-2 text-sm text-gray-900 dark:text-slate-100">
                      {formatDateTime(program.created_at)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Status</p>
                    <p className="mt-2 text-sm capitalize text-gray-900 dark:text-slate-100">
                      {program.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Visibility</p>
                    <p className="mt-2 text-sm capitalize text-gray-900 dark:text-slate-100">
                      {program.visibility}
                    </p>
                  </div>
                </section>

                {/* Description */}
                <section className="border-t border-gray-200 pt-8 dark:border-slate-700">
                  <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                    Description
                  </h2>
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <p className="whitespace-pre-wrap text-gray-700 dark:text-slate-300">
                      {program.description || 'No description provided'}
                    </p>
                  </div>
                </section>

                {/* Program Rules */}
                {program.rules && (
                  <section className="border-t border-gray-200 pt-8 dark:border-slate-700">
                    <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                      Program Rules
                    </h2>
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      <p className="whitespace-pre-wrap text-gray-700 dark:text-slate-300">
                        {program.rules}
                      </p>
                    </div>
                  </section>
                )}
              </>
            )}

            {/* Scope Tab */}
            {activeTab === 'scope' && (
              <section>
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                    In-Scope Assets
                  </h2>
                  <Button 
                    variant="secondary" 
                    size="sm"
                    onClick={() => setShowScopeAddModal(true)}
                  >
                    + Add Scope
                  </Button>
                </div>

                {scopes && scopes.length > 0 ? (
                  <div className="space-y-4">
                    {scopes.map((scope: any) => (
                      <div
                        key={scope.id}
                        className="flex items-start justify-between gap-4 rounded-lg border border-gray-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800"
                      >
                        <div className="flex-1">
                          <p className="text-sm font-bold uppercase text-gray-900 dark:text-slate-100">{scope.asset_type}</p>
                          <p className="mt-2 text-sm text-gray-700 dark:text-slate-300">{scope.asset_identifier}</p>
                          {scope.description && (
                            <p className="mt-2 text-xs text-gray-500 dark:text-slate-400">{scope.description}</p>
                          )}
                        </div>
                        <span className={`inline-flex items-center rounded-md px-3 py-1 text-xs font-bold uppercase ${
                          scope.is_in_scope 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {scope.is_in_scope ? 'In Scope' : 'Out of Scope'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-lg border border-gray-200 bg-gray-50 p-12 text-center dark:border-slate-700 dark:bg-slate-800">
                    <p className="text-sm text-gray-500 dark:text-slate-400">
                      {program.scope || 'No scope defined yet. Click "+ Add Scope" to add assets.'}
                    </p>
                  </div>
                )}
              </section>
            )}

            {/* Rewards Tab */}
            {activeTab === 'rewards' && (
              <section>
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                    Reward Tiers
                  </h2>
                  <Button 
                    variant="secondary" 
                    size="sm"
                    onClick={() => setShowRewardEditModal(true)}
                  >
                    Edit Rewards
                  </Button>
                </div>

                {rewards && rewards.length > 0 ? (
                  <div className="space-y-4">
                    {rewards.map((reward: any) => (
                      <div
                        key={reward.id}
                        className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800"
                      >
                        <div>
                          <p className="text-sm font-bold uppercase text-gray-900 dark:text-slate-100">
                            {reward.severity}
                          </p>
                          <p className="mt-1 text-xs text-gray-500 dark:text-slate-400">
                            {reward.description || 'Standard bounty'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-900 dark:text-slate-100">
                            {formatCurrency(reward.min_amount)} - {formatCurrency(reward.max_amount)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-lg border border-gray-200 bg-gray-50 p-12 text-center dark:border-slate-700 dark:bg-slate-800">
                    <p className="text-sm text-gray-500 dark:text-slate-400">
                      No reward tiers configured yet
                    </p>
                  </div>
                )}
              </section>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <section>
                <h2 className="mb-6 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Program Actions
                </h2>
                <div className="max-w-md space-y-4">
                  {program.status === 'draft' && (
                    <Button
                      onClick={() => publishProgram({})}
                      disabled={isPublishing}
                      className="w-full"
                    >
                      {isPublishing ? 'Publishing...' : 'Publish Program'}
                    </Button>
                  )}

                  {program.status === 'public' && (
                    <Button
                      onClick={() => pauseProgram({})}
                      disabled={isPausing}
                      variant="secondary"
                      className="w-full"
                    >
                      {isPausing ? 'Pausing...' : 'Pause Program'}
                    </Button>
                  )}

                  {program.status === 'paused' && (
                    <Button
                      onClick={() => resumeProgram({})}
                      disabled={isResuming}
                      className="w-full"
                    >
                      {isResuming ? 'Resuming...' : 'Resume Program'}
                    </Button>
                  )}

                  {(program.status === 'public' || program.status === 'paused') && (
                    <Button
                      onClick={() => {
                        if (confirm('Are you sure you want to close this program? This action cannot be undone.')) {
                          closeProgram({});
                        }
                      }}
                      disabled={isClosing}
                      variant="secondary"
                      className="w-full"
                    >
                      {isClosing ? 'Closing...' : 'Close Program'}
                    </Button>
                  )}
                </div>

                <div className="mt-8 rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-900">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    <strong>Note:</strong> Closing a program will prevent new submissions but existing reports will remain accessible.
                  </p>
                </div>
              </section>
            )}
          </div>
        </PortalShell>
      )}

      {/* Modals */}
      {showRewardEditModal && (
        <RewardEditModal
          programId={programId}
          existingRewards={rewards || []}
          onClose={() => setShowRewardEditModal(false)}
          onSuccess={() => {
            setShowRewardEditModal(false);
            refetchRewards();
          }}
        />
      )}

      {showScopeAddModal && (
        <ScopeAddModal
          programId={programId}
          onClose={() => setShowScopeAddModal(false)}
          onSuccess={() => {
            setShowScopeAddModal(false);
            refetchScopes();
          }}
        />
      )}
    </ProtectedRoute>
  );
}
