'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import SectionCard from '@/components/dashboard/SectionCard';
import type { ProgramScope } from '@/hooks/useResearcherEngagementsData';
import api from '@/lib/api';
import EngagementReportComposer from './EngagementReportComposer';
import { formatStatusLabel } from './shared';
import type { EngagementWorkflowItem } from './shared';

interface EngagementWorkflowDeskProps {
  item: EngagementWorkflowItem | null;
  isLoading: boolean;
  pendingAction: string;
  onJoinProgram: (programId: string) => Promise<void>;
  onRespondProgramInvitation: (invitationId: string, accept: boolean) => Promise<void>;
  onRespondMatchingInvitation: (invitationId: string, accept: boolean) => Promise<void>;
  onStartCodeReview: (engagementId: string) => Promise<void>;
}

function getWorkflowStages(item: EngagementWorkflowItem): Array<{ label: string; state: 'done' | 'current' | 'upcoming' }> {
  switch (item.kind) {
    case 'program-joined':
      return [
        { label: 'Joined', state: 'done' },
        { label: 'Scope confirmed', state: 'done' },
        { label: 'Submit vulnerability', state: 'current' },
        { label: 'Track triage', state: 'upcoming' },
      ];
    case 'program-open':
      return [
        { label: 'Inspect program', state: 'done' },
        { label: 'Join program', state: 'current' },
        { label: 'Submit vulnerability', state: 'upcoming' },
        { label: 'Track triage', state: 'upcoming' },
      ];
    case 'program-invitation':
    case 'matching-invitation':
      return [
        { label: 'Review invitation', state: 'done' },
        { label: 'Accept or decline', state: 'current' },
        { label: 'Activate engagement', state: 'upcoming' },
        { label: 'Execute workflow', state: 'upcoming' },
      ];
    case 'live-event':
      return [
        { label: 'Event active', state: 'done' },
        { label: 'Prepare evidence', state: 'current' },
        { label: 'Link eligible finding', state: 'upcoming' },
        { label: 'Watch leaderboard', state: 'upcoming' },
      ];
    case 'code-review':
      return [
        { label: 'Assignment received', state: 'done' },
        { label: item.status === 'in_progress' ? 'Continue review' : 'Start review', state: 'current' },
        { label: 'Capture findings', state: 'upcoming' },
        { label: 'Submit final review', state: 'upcoming' },
      ];
    default:
      return [
        { label: 'Review fit', state: 'done' },
        { label: 'Await assignment', state: 'current' },
        { label: 'Coordinate delivery', state: 'upcoming' },
        { label: 'Complete handoff', state: 'upcoming' },
      ];
  }
}

function getStageTone(state: 'done' | 'current' | 'upcoming'): string {
  switch (state) {
    case 'done':
      return 'border-[#bfd5c5] bg-[#eef7ef] text-[#24613a]';
    case 'current':
      return 'border-[#d7c8b7] bg-[#fbf2e6] text-[#9a6412]';
    default:
      return 'border-[#e6ddd4] bg-[#fcfaf7] text-[#6d6760]';
  }
}

function getSelectedProgramId(item: EngagementWorkflowItem | null): string {
  if (!item) {
    return '';
  }

  if (item.kind === 'program-open' || item.kind === 'program-joined') {
    return item.entityId;
  }

  if (item.kind === 'program-invitation') {
    return item.reportProgramId || '';
  }

  return '';
}

function normalizeScope(raw: any): ProgramScope | null {
  const id = typeof raw?.id === 'string' ? raw.id : '';

  if (!id) {
    return null;
  }

  return {
    id,
    programId: typeof (raw?.program_id ?? raw?.programId) === 'string' ? raw.program_id ?? raw.programId : '',
    assetType: typeof (raw?.asset_type ?? raw?.assetType) === 'string' ? raw.asset_type ?? raw.assetType : 'asset',
    assetIdentifier:
      typeof (raw?.asset_identifier ?? raw?.assetIdentifier) === 'string'
        ? raw.asset_identifier ?? raw.assetIdentifier
        : 'Unknown asset',
    isInScope: Boolean(raw?.is_in_scope ?? raw?.isInScope),
    description: typeof raw?.description === 'string' ? raw.description : null,
    maxSeverity:
      typeof (raw?.max_severity ?? raw?.maxSeverity) === 'string' ? raw.max_severity ?? raw.maxSeverity : null,
  };
}

export default function EngagementWorkflowDesk({
  item,
  isLoading,
  pendingAction,
  onJoinProgram,
  onRespondProgramInvitation,
  onRespondMatchingInvitation,
  onStartCodeReview,
}: EngagementWorkflowDeskProps) {
  const [programScopes, setProgramScopes] = useState<ProgramScope[]>([]);
  const [isLoadingProgramScopes, setIsLoadingProgramScopes] = useState(false);
  const [programScopeError, setProgramScopeError] = useState('');

  const selectedProgramId = getSelectedProgramId(item);

  useEffect(() => {
    let cancelled = false;

    if (!selectedProgramId) {
      setProgramScopes([]);
      setProgramScopeError('');
      setIsLoadingProgramScopes(false);
      return;
    }

    const loadProgramScopes = async () => {
      try {
        setIsLoadingProgramScopes(true);
        setProgramScopeError('');

        const response = await api.get(`/programs/${selectedProgramId}/scopes`);

        if (cancelled) {
          return;
        }

        const nextScopes = Array.isArray(response.data)
          ? response.data.map(normalizeScope).filter((scope): scope is ProgramScope => Boolean(scope))
          : [];

        setProgramScopes(nextScopes);
      } catch (err: any) {
        if (!cancelled) {
          setProgramScopes([]);
          setProgramScopeError(err.response?.data?.detail || 'Failed to load program scope.');
        }
      } finally {
        if (!cancelled) {
          setIsLoadingProgramScopes(false);
        }
      }
    };

    loadProgramScopes();

    return () => {
      cancelled = true;
    };
  }, [selectedProgramId]);

  async function handlePrimaryAction() {
    if (!item) {
      return;
    }

    switch (item.kind) {
      case 'program-open':
        await onJoinProgram(item.entityId);
        return;
      case 'program-invitation':
        await onRespondProgramInvitation(item.entityId, true);
        return;
      case 'matching-invitation':
        await onRespondMatchingInvitation(item.entityId, true);
        return;
      case 'code-review':
        if (item.status !== 'in_progress') {
          await onStartCodeReview(item.entityId);
        }
        return;
      default:
        return;
    }
  }

  const isProgramInvitation = item?.kind === 'program-invitation';
  const isMatchingInvitation = item?.kind === 'matching-invitation';
  const inScopeAssets = programScopes.filter((scope) => scope.isInScope);
  const outOfScopeAssets = programScopes.filter((scope) => !scope.isInScope);
  const primaryActionPending =
    item &&
    ((item.kind === 'program-open' && pendingAction === `join-${item.entityId}`) ||
      (item.kind === 'program-invitation' && pendingAction === `program-invitation-${item.entityId}`) ||
      (item.kind === 'matching-invitation' && pendingAction === `matching-invitation-${item.entityId}`) ||
      (item.kind === 'code-review' && pendingAction === `code-review-${item.entityId}`));

  return (
    <SectionCard
      title="Engagement Action Desk"
      description="This is the operational handoff for the selected engagement. Join, respond, start the service workflow, or submit a vulnerability from here."
    >
      {!item ? (
        <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-6 text-sm leading-6 text-[#6d6760]">
          {isLoading
            ? 'Loading engagement actions...'
            : 'Select an engagement from the radar, invitation queue, active board, or specialized tracks to open its workflow.'}
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <div className="space-y-5 rounded-[28px] border border-[#e6ddd4] bg-[#fcfaf7] p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Selected Engagement</p>
                <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#2d2a26]">{item.title}</h3>
              </div>
              <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                {formatStatusLabel(item.status)}
              </span>
            </div>

            <p className="text-sm leading-7 text-[#5b534c]">{item.summary}</p>

            <div className="grid gap-3 sm:grid-cols-2">
              {item.metrics.map((metric) => (
                <div key={`${item.key}-${metric.label}`} className="rounded-2xl border border-[#e6ddd4] bg-white dark:bg-[#111111] px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">{metric.label}</p>
                  <p className="mt-2 text-sm font-semibold text-[#2d2a26]">{metric.value}</p>
                </div>
              ))}
            </div>

            <div className="rounded-2xl border border-[#eadfce] bg-[#fff7ef] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Next Step</p>
              <p className="mt-2 text-sm leading-6 text-[#5b534c]">{item.nextStep}</p>
            </div>

              <div className="flex flex-wrap gap-2">
              {item.kind === 'program-joined' ? (
                <span className="rounded-full border border-[#bfd5c5] bg-[#eef7ef] px-4 py-2 text-xs font-semibold text-[#24613a]">
                  Joined
                </span>
              ) : null}

              {item.kind !== 'program-joined' && item.kind !== 'live-event' && item.kind !== 'ptaas' ? (
                <button
                  type="button"
                  onClick={handlePrimaryAction}
                  disabled={Boolean(primaryActionPending)}
                  className="rounded-full bg-[#2d2a26] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#1f1c19] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {primaryActionPending ? 'Processing...' : item.primaryActionLabel}
                </button>
              ) : null}

              {isProgramInvitation ? (
                <button
                  type="button"
                  onClick={() => onRespondProgramInvitation(item.entityId, false)}
                  disabled={pendingAction === `program-invitation-${item.entityId}`}
                  className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white dark:bg-[#111111] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Decline
                </button>
              ) : null}

              {isMatchingInvitation ? (
                <button
                  type="button"
                  onClick={() => onRespondMatchingInvitation(item.entityId, false)}
                  disabled={pendingAction === `matching-invitation-${item.entityId}`}
                  className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white dark:bg-[#111111] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Decline
                </button>
              ) : null}

              {item.reportHref ? (
                <Link
                  href={item.reportHref}
                  className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white"
                >
                  {item.kind === 'program-joined' ? 'Report vulnerability' : 'Open full queue'}
                </Link>
              ) : null}
            </div>
          </div>

          <div className="space-y-5">
            {selectedProgramId ? (
              <div className="rounded-[28px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Scope Coverage</p>
                    <p className="mt-2 text-sm leading-6 text-[#5b534c]">
                      Review the allowed assets before you test or submit a finding.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs font-semibold">
                    <span className="rounded-full bg-[#eef7ef] px-3 py-1 text-[#24613a]">
                      {inScopeAssets.length} in scope
                    </span>
                    <span className="rounded-full bg-[#fff2f1] px-3 py-1 text-[#b42318]">
                      {outOfScopeAssets.length} out of scope
                    </span>
                  </div>
                </div>

                {isLoadingProgramScopes ? (
                  <div className="mt-4 rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
                    Loading scope assets...
                  </div>
                ) : programScopeError ? (
                  <div className="mt-4 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                    {programScopeError}
                  </div>
                ) : programScopes.length ? (
                  <div className="mt-4 grid gap-4 lg:grid-cols-2">
                    <div className="space-y-3">
                      <h4 className="text-sm font-semibold text-[#24613a]">In-Scope Assets</h4>
                      {inScopeAssets.length ? (
                        inScopeAssets.map((scope) => (
                          <div key={scope.id} className="rounded-2xl border border-[#d9eadc] bg-[#f7fbf8] p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <p className="text-sm font-semibold text-[#2d2a26]">{scope.assetIdentifier}</p>
                              <span className="rounded-full bg-[#eef7ef] px-3 py-1 text-xs font-semibold text-[#24613a]">
                                {formatStatusLabel(scope.assetType)}
                              </span>
                            </div>
                            {scope.description ? (
                              <p className="mt-2 text-sm leading-6 text-[#5b534c]">{scope.description}</p>
                            ) : null}
                            {scope.maxSeverity ? (
                              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-[#6d6760]">
                                Max severity: {formatStatusLabel(scope.maxSeverity)}
                              </p>
                            ) : null}
                          </div>
                        ))
                      ) : (
                        <div className="rounded-2xl border border-dashed border-[#d9eadc] bg-[#f7fbf8] p-4 text-sm text-[#5b534c]">
                          No in-scope assets are listed for this program yet.
                        </div>
                      )}
                    </div>

                    <div className="space-y-3">
                      <h4 className="text-sm font-semibold text-[#b42318]">Out-of-Scope Assets</h4>
                      {outOfScopeAssets.length ? (
                        outOfScopeAssets.map((scope) => (
                          <div key={scope.id} className="rounded-2xl border border-[#f2d0cd] bg-[#fff7f6] p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <p className="text-sm font-semibold text-[#2d2a26]">{scope.assetIdentifier}</p>
                              <span className="rounded-full bg-[#fff2f1] px-3 py-1 text-xs font-semibold text-[#b42318]">
                                {formatStatusLabel(scope.assetType)}
                              </span>
                            </div>
                            {scope.description ? (
                              <p className="mt-2 text-sm leading-6 text-[#5b534c]">{scope.description}</p>
                            ) : null}
                            {scope.maxSeverity ? (
                              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-[#6d6760]">
                                Max severity: {formatStatusLabel(scope.maxSeverity)}
                              </p>
                            ) : null}
                          </div>
                        ))
                      ) : (
                        <div className="rounded-2xl border border-dashed border-[#f2d0cd] bg-[#fff7f6] p-4 text-sm text-[#5b534c]">
                          No out-of-scope assets are listed for this program.
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="mt-4 rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
                    No scope assets are defined for this program yet.
                  </div>
                )}
              </div>
            ) : null}

            <div className="rounded-[28px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Workflow Path</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {getWorkflowStages(item).map((stage) => (
                  <div key={`${item.key}-${stage.label}`} className={`rounded-2xl border px-4 py-4 ${getStageTone(stage.state)}`}>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em]">{stage.state}</p>
                    <p className="mt-2 text-sm font-semibold">{stage.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {item.kind === 'program-joined' ? (
              <EngagementReportComposer
                resetKey={item.key}
                reportProgramId={item.reportProgramId}
                reportHref={item.reportHref}
              />
            ) : (
              <div className="rounded-[28px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Operational Note</p>
                <p className="mt-3 text-sm leading-7 text-[#5b534c]">
                  {item.kind === 'live-event'
                    ? 'Live event submission depends on linking an eligible report into the event record. The engagement keeps that handoff visible before you move into the full queue.'
                    : item.kind === 'code-review'
                      ? 'Code review work stays anchored to this engagement. Start the review here, then continue into finding capture and final submission.'
                      : item.kind === 'ptaas'
                        ? 'PTaaS opportunities are assignment-driven. This desk is the review and coordination entry point until the service workflow opens.'
                        : 'Respond from this desk, then the engagement will move into the active board and unlock the next operational stage.'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </SectionCard>
  );
}
