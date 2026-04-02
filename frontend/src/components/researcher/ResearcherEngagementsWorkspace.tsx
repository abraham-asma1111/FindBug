'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import EngagementWorkflowDesk from '@/components/researcher/engagements/EngagementWorkflowDesk';
import ActiveParticipationBoard from '@/components/researcher/engagements/ActiveParticipationBoard';
import InvitationQueue from '@/components/researcher/engagements/InvitationQueue';
import OpportunityRadar from '@/components/researcher/engagements/OpportunityRadar';
import ProgramCatalogTable from '@/components/researcher/engagements/ProgramCatalogTable';
import SpecializedTracks from '@/components/researcher/engagements/SpecializedTracks';
import {
  buildActiveTracks,
  buildInvitationRows,
  buildJoinedProgramIds,
  buildOpportunityRadar,
  buildPublicProgramWorkflowItems,
  buildProgramDirectory,
  composeWorkflowItems,
  createCodeReviewWorkflowAdapter,
  createInvitationWorkflowAdapter,
  createLiveEventWorkflowAdapter,
  createPTaaSWorkflowAdapter,
  createParticipationWorkflowAdapter,
  createPublicProgramWorkflowAdapter,
  getActiveTrackStep,
  getProgramReportHref,
  pickDefaultWorkflowItem,
} from '@/components/researcher/engagements/selectors';
import type { EngagementProgram } from '@/hooks/useResearcherEngagementsData';
import { useResearcherEngagementsData } from '@/hooks/useResearcherEngagementsData';
import api from '@/lib/api';
import { formatCompactNumber, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function ResearcherEngagementsWorkspace() {
  const user = useAuthStore((state) => state.user);
  const {
    recommendedPrograms,
    publicPrograms,
    matchedPrograms,
    programInvitations,
    participations,
    matchingInvitations,
    liveEvents,
    codeReviewAssignments,
    ptaasOpportunities,
    warnings,
    error,
    isLoading,
    refreshData,
  } = useResearcherEngagementsData();
  const [actionError, setActionError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');
  const [pendingAction, setPendingAction] = useState('');
  const [selectedWorkflowKey, setSelectedWorkflowKey] = useState('');

  const serviceWarnings = new Set(warnings);
  const joinedProgramIds = buildJoinedProgramIds(participations);
  const programDirectory = buildProgramDirectory(recommendedPrograms, publicPrograms, matchedPrograms, participations);
  const opportunityRadar = buildOpportunityRadar(recommendedPrograms, matchedPrograms);
  const invitationRows = buildInvitationRows(programInvitations, matchingInvitations, programDirectory);
  const activeTracks = buildActiveTracks(participations, liveEvents, codeReviewAssignments);
  const publicProgramWorkflowItems = buildPublicProgramWorkflowItems(publicPrograms, participations, joinedProgramIds).filter(
    (item) => item.kind === 'program-open'
  );
  const workflowItems = composeWorkflowItems([
    createParticipationWorkflowAdapter(participations),
    createInvitationWorkflowAdapter(programInvitations, matchingInvitations, programDirectory),
    createLiveEventWorkflowAdapter(liveEvents),
    createCodeReviewWorkflowAdapter(codeReviewAssignments),
    createPTaaSWorkflowAdapter(ptaasOpportunities),
    createPublicProgramWorkflowAdapter(publicProgramWorkflowItems),
  ]);

  const resolvedWorkflowKey = selectedWorkflowKey || pickDefaultWorkflowItem(workflowItems)?.key || '';
  const selectedWorkflowItem = workflowItems.find((item) => item.key === resolvedWorkflowKey) || null;

  useEffect(() => {
    if (!workflowItems.length) {
      setSelectedWorkflowKey('');
      return;
    }

    if (selectedWorkflowKey && workflowItems.some((item) => item.key === selectedWorkflowKey)) {
      return;
    }

    const defaultItem = pickDefaultWorkflowItem(workflowItems);
    setSelectedWorkflowKey(defaultItem?.key || '');
  }, [selectedWorkflowKey, workflowItems]);

  const allPrograms = new Map<string, EngagementProgram>();
  [...recommendedPrograms, ...publicPrograms, ...matchedPrograms].forEach((program) => {
    allPrograms.set(program.id, program);
  });

  const programInvitationById = new Map(programInvitations.map((invitation) => [invitation.id, invitation]));
  const matchingInvitationById = new Map(matchingInvitations.map((invitation) => [invitation.id, invitation]));

  function selectWorkflowByProgram(programId: string) {
    const nextItem = workflowItems.find(
      (item) => item.reportProgramId === programId || (item.kind === 'program-open' && item.entityId === programId)
    );

    if (nextItem) {
      setSelectedWorkflowKey(nextItem.key);
    }
  }

  function selectWorkflowByTrack(trackId: string, trackType: string) {
    const nextKey =
      trackType === 'program'
        ? `participation-${trackId}`
        : trackType === 'live-event'
          ? `live-event-${trackId}`
          : `code-review-${trackId}`;

    setSelectedWorkflowKey(nextKey);
  }

  function selectWorkflowByInvitation(
    invitationId: string,
    kind: 'program-invitation' | 'matching-invitation'
  ) {
    setSelectedWorkflowKey(`${kind}-${invitationId}`);
  }

  async function handleJoinProgram(programId: string) {
    const program = allPrograms.get(programId);

    if (!program) {
      setActionError('Program details are unavailable right now.');
      return;
    }

    try {
      setPendingAction(`join-${program.id}`);
      setActionError('');
      setActionSuccess('');

      await api.post(`/programs/programs/${program.id}/join`);
      setActionSuccess(
        `You joined ${program.name}. The engagement now unlocks direct vulnerability submission from the action desk.`
      );
      refreshData();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || `Failed to join ${program.name}.`);
    } finally {
      setPendingAction('');
    }
  }

  async function handleProgramInvitation(invitationId: string, accept: boolean) {
    const invitation = programInvitationById.get(invitationId);

    if (!invitation) {
      setActionError('Program invitation details are unavailable right now.');
      return;
    }

    try {
      setPendingAction(`program-invitation-${invitation.id}`);
      setActionError('');
      setActionSuccess('');

      await api.post(`/programs/invitations/${invitation.id}/respond`, { accept });
      setActionSuccess(`Program invitation ${accept ? 'accepted' : 'declined'} successfully.`);
      refreshData();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Failed to update the program invitation.');
    } finally {
      setPendingAction('');
    }
  }

  async function handleMatchingInvitation(invitationId: string, accept: boolean) {
    const invitation = matchingInvitationById.get(invitationId);

    if (!invitation) {
      setActionError('Matching invitation details are unavailable right now.');
      return;
    }

    try {
      setPendingAction(`matching-invitation-${invitation.id}`);
      setActionError('');
      setActionSuccess('');

      await api.post(`/matching/invitations/${invitation.id}/respond`, null, {
        params: { accept },
      });
      setActionSuccess(`Matching invitation ${accept ? 'accepted' : 'declined'} successfully.`);
      refreshData();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Failed to update the matching invitation.');
    } finally {
      setPendingAction('');
    }
  }

  async function handleStartCodeReview(engagementId: string) {
    try {
      setPendingAction(`code-review-${engagementId}`);
      setActionError('');
      setActionSuccess('');

      await api.post(`/code-review/engagements/${engagementId}/start`);
      setActionSuccess('Code review started successfully. Continue the engagement workflow to capture findings.');
      refreshData();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Failed to start the code review.');
    } finally {
      setPendingAction('');
    }
  }

  function renderProgramAction(program: EngagementProgram) {
    if (joinedProgramIds.has(program.id)) {
      return (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => selectWorkflowByProgram(program.id)}
            className="inline-flex rounded-full bg-[#2d2a26] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#1f1c19]"
          >
            Report vulnerability
          </button>
          <Link
            href={getProgramReportHref(program.id, program.name)}
            className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
          >
            Open queue
          </Link>
        </div>
      );
    }

    return (
      <button
        type="button"
        onClick={() => handleJoinProgram(program.id)}
        disabled={pendingAction === `join-${program.id}`}
        className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7] disabled:cursor-not-allowed disabled:opacity-60"
      >
        {pendingAction === `join-${program.id}` ? 'Joining...' : 'Join program'}
      </button>
    );
  }

  const pendingInvitationCount = invitationRows.filter((entry) => entry.status === 'pending').length;
  const activeTrackCount = activeTracks.length;

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Engagements"
          subtitle="Discover programs and service tracks, respond to invitations, and execute the next action from the engagement itself."
          navItems={getPortalNavItems(user.role)}
        >
          {error ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {error}
            </div>
          ) : null}

          {actionError ? (
            <div className="mb-6 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              {actionError}
            </div>
          ) : null}

          {actionSuccess ? (
            <div className="mb-6 rounded-2xl border border-[#b8dbbf] bg-[#eef7ef] p-4 text-sm text-[#24613a]">
              {actionSuccess}
            </div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Public Programs"
              value={isLoading ? '...' : formatCompactNumber(publicPrograms.length)}
              helper="Public VDP and bounty programs open to researchers"
            />
            <StatCard
              label="Pending Invitations"
              value={isLoading ? '...' : formatCompactNumber(pendingInvitationCount)}
              helper="Program and matching invitations awaiting your decision"
            />
            <StatCard
              label="Active Tracks"
              value={isLoading ? '...' : formatCompactNumber(activeTrackCount)}
              helper="Joined programs, live events, and assigned service work"
            />
            <StatCard
              label="PTaaS Opportunities"
              value={isLoading ? '...' : formatCompactNumber(ptaasOpportunities.length)}
              helper="Researcher-side PTaaS matches and recommendations"
            />
          </div>

          <div className="mt-6">
            <EngagementWorkflowDesk
              item={selectedWorkflowItem}
              isLoading={isLoading}
              pendingAction={pendingAction}
              onJoinProgram={handleJoinProgram}
              onRespondProgramInvitation={handleProgramInvitation}
              onRespondMatchingInvitation={handleMatchingInvitation}
              onStartCodeReview={handleStartCodeReview}
            />
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
            <OpportunityRadar
              isLoading={isLoading}
              programs={opportunityRadar}
              renderAction={renderProgramAction}
              onInspect={selectWorkflowByProgram}
            />
            <InvitationQueue
              isLoading={isLoading}
              invitations={invitationRows}
              pendingAction={pendingAction}
              onInspect={selectWorkflowByInvitation}
              onAccept={(invitationId, kind) =>
                kind === 'program-invitation'
                  ? handleProgramInvitation(invitationId, true)
                  : handleMatchingInvitation(invitationId, true)
              }
              onDecline={(invitationId, kind) =>
                kind === 'program-invitation'
                  ? handleProgramInvitation(invitationId, false)
                  : handleMatchingInvitation(invitationId, false)
              }
            />
          </div>

          <div className="mt-6">
            <ActiveParticipationBoard
              isLoading={isLoading}
              tracks={activeTracks}
              getTrackStep={getActiveTrackStep}
              onInspect={selectWorkflowByTrack}
            />
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
            <ProgramCatalogTable
              isLoading={isLoading}
              programs={publicPrograms}
              joinedProgramIds={joinedProgramIds}
              renderAction={renderProgramAction}
              onInspect={selectWorkflowByProgram}
            />
            <SpecializedTracks
              liveEvents={liveEvents}
              codeReviewAssignments={codeReviewAssignments}
              ptaasOpportunities={ptaasOpportunities}
              warnings={serviceWarnings}
              onInspectLiveEvent={(eventId) => setSelectedWorkflowKey(`live-event-${eventId}`)}
              onInspectCodeReview={(engagementId) => setSelectedWorkflowKey(`code-review-${engagementId}`)}
              onInspectPTaaS={(engagementId) => setSelectedWorkflowKey(`ptaas-${engagementId}`)}
            />
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
