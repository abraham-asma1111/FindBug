import type {
  CodeReviewAssignment,
  EngagementProgram,
  LiveEventAssignment,
  MatchingInvitation,
  ProgramInvitation,
  ProgramParticipation,
  PTaaSOpportunity,
} from '@/hooks/useResearcherEngagementsData';
import { formatCurrency, formatDateTime } from '@/lib/portal';
import type { ActiveTrackRow, EngagementInvitationRow, EngagementWorkflowItem } from './shared';
import {
  getCodeReviewNextStep,
  getCodeReviewSummary,
  getJoinedProgramNextStep,
  getJoinedProgramSummary,
  getLiveEventNextStep,
  getLiveEventSummary,
  getMatchingInvitationNextStep,
  getMatchingInvitationSummary,
  getOpenProgramNextStep,
  getOpenProgramSummary,
  getPTaaSNextStep,
  getPTaaSSummary,
  getProgramInvitationNextStep,
  getProgramInvitationSummary,
} from './workflowCopy';

export interface EngagementWorkflowAdapter {
  id: string;
  buildItems: () => EngagementWorkflowItem[];
}

export function getProgramReportHref(programId: string, programName: string): string {
  return `/researcher/reports?programId=${encodeURIComponent(programId)}&contextLabel=${encodeURIComponent(programName)}`;
}

export function getGenericReportsHref(contextLabel: string): string {
  return `/researcher/reports?contextLabel=${encodeURIComponent(contextLabel)}`;
}

export function getActiveTrackStep(track: { type: string; status?: string | null }): string {
  if (track.type === 'program') {
    return 'Submit a vulnerability report directly from this engagement and keep evidence attached to the program scope.';
  }

  if (track.type === 'live-event') {
    return 'Open the event workflow, submit or link an eligible finding, and watch leaderboard impact.';
  }

  if (track.type === 'code-review') {
    return 'Start the review, capture findings, then submit the final code review report from the same engagement.';
  }

  return 'Open the selected engagement and continue the next assigned handoff.';
}

export function buildJoinedProgramIds(participations: ProgramParticipation[]): Set<string> {
  return new Set(participations.map((entry) => entry.program.id));
}

export function buildProgramDirectory(
  recommendedPrograms: EngagementProgram[],
  publicPrograms: EngagementProgram[],
  matchedPrograms: EngagementProgram[],
  participations: ProgramParticipation[]
): Map<string, string> {
  const directory = new Map<string, string>();

  [...recommendedPrograms, ...publicPrograms, ...matchedPrograms].forEach((program) => {
    directory.set(program.id, program.name);
  });

  participations.forEach((entry) => {
    directory.set(entry.program.id, entry.program.name);
  });

  return directory;
}

export function buildOpportunityRadar(
  recommendedPrograms: EngagementProgram[],
  matchedPrograms: EngagementProgram[]
): EngagementProgram[] {
  return [...recommendedPrograms, ...matchedPrograms]
    .filter((program, index, list) => list.findIndex((entry) => entry.id === program.id) === index)
    .slice(0, 6);
}

export function buildInvitationRows(
  programInvitations: ProgramInvitation[],
  matchingInvitations: MatchingInvitation[],
  programDirectory: Map<string, string>
): EngagementInvitationRow[] {
  return [
    ...programInvitations.map((invitation) => ({
      id: invitation.id,
      kind: 'Program invitation',
      actionKind: 'program-invitation' as const,
      label: programDirectory.get(invitation.programId) || `Program ${invitation.programId.slice(0, 8)}`,
      status: invitation.status,
      message: invitation.message,
      expiresAt: invitation.expiresAt,
    })),
    ...matchingInvitations.map((invitation) => ({
      id: invitation.id,
      kind: 'Matching invitation',
      actionKind: 'matching-invitation' as const,
      label: invitation.engagementId ? `Engagement ${invitation.engagementId.slice(0, 8)}` : 'Matched service request',
      status: invitation.status,
      message: invitation.message,
      expiresAt: invitation.expiresAt,
    })),
  ];
}

export function buildActiveTracks(
  participations: ProgramParticipation[],
  liveEvents: LiveEventAssignment[],
  codeReviewAssignments: CodeReviewAssignment[]
): ActiveTrackRow[] {
  return [
    ...participations.map((entry) => ({
      id: entry.id,
      name: entry.program.name,
      type: 'program',
      status: entry.program.status || 'active',
      updatedAt: entry.joinedAt,
      actionHref: getProgramReportHref(entry.program.id, entry.program.name),
      actionLabel: 'Report vulnerability',
    })),
    ...liveEvents.map((event) => ({
      id: event.id,
      name: event.name,
      type: 'live-event',
      status: event.participationStatus || event.status,
      updatedAt: event.endTime || event.startTime,
      actionHref: getGenericReportsHref(`Live Event: ${event.name}`),
      actionLabel: 'Open finding flow',
    })),
    ...codeReviewAssignments.map((assignment) => ({
      id: assignment.id,
      name: assignment.title,
      type: 'code-review',
      status: assignment.status,
      updatedAt: assignment.reportSubmittedAt || assignment.createdAt,
      actionHref: '/researcher/engagements',
      actionLabel: assignment.status === 'in_progress' ? 'Continue review' : 'Start review',
    })),
  ];
}

function buildParticipationWorkflowItems(participations: ProgramParticipation[]): EngagementWorkflowItem[] {
  return participations.map((entry) => ({
    key: `participation-${entry.id}`,
    entityId: entry.program.id,
    kind: 'program-joined',
    title: entry.program.name,
    status: entry.program.status || 'active',
    summary: getJoinedProgramSummary(entry.program.description),
    nextStep: getJoinedProgramNextStep(),
    contextLabel: entry.program.name,
    primaryActionLabel: 'Submit vulnerability now',
    reportHref: getProgramReportHref(entry.program.id, entry.program.name),
    reportProgramId: entry.program.id,
    metrics: [
      { label: 'Joined', value: formatDateTime(entry.joinedAt) },
      { label: 'Type', value: entry.program.type || 'bounty' },
      { label: 'Visibility', value: entry.program.visibility || 'private' },
      { label: 'Budget', value: entry.program.budget ? formatCurrency(entry.program.budget) : 'Not disclosed' },
    ],
  }));
}

export function buildPublicProgramWorkflowItems(
  publicPrograms: EngagementProgram[],
  participations: ProgramParticipation[],
  joinedProgramIds: Set<string>
): EngagementWorkflowItem[] {
  const participationByProgramId = new Map(participations.map((entry) => [entry.program.id, entry]));

  return publicPrograms.map((program) => {
      const participation = participationByProgramId.get(program.id);
      const isJoined = joinedProgramIds.has(program.id);

      return {
        key: `program-${program.id}`,
        entityId: program.id,
        kind: isJoined ? 'program-joined' : 'program-open',
        title: program.name,
        status: program.status,
        summary: getOpenProgramSummary(program.description),
        nextStep: getOpenProgramNextStep(isJoined),
        contextLabel: program.name,
        primaryActionLabel: isJoined ? 'Submit vulnerability now' : 'Join program',
        reportHref: getProgramReportHref(program.id, program.name),
        reportProgramId: program.id,
        metrics: [
          { label: 'Type', value: program.type || 'bounty' },
          { label: 'Visibility', value: program.visibility || 'public' },
          { label: 'Budget', value: program.budget ? formatCurrency(program.budget) : 'Not disclosed' },
          { label: 'Joined', value: participation ? formatDateTime(participation.joinedAt) : 'Not yet joined' },
        ],
      } satisfies EngagementWorkflowItem;
    });
}

function buildInvitationWorkflowItems(
  programInvitations: ProgramInvitation[],
  matchingInvitations: MatchingInvitation[],
  programDirectory: Map<string, string>
): EngagementWorkflowItem[] {
  const programItems = programInvitations.map<EngagementWorkflowItem>((invitation) => ({
    key: `program-invitation-${invitation.id}`,
    entityId: invitation.id,
    kind: 'program-invitation',
    title: programDirectory.get(invitation.programId) || `Program ${invitation.programId.slice(0, 8)}`,
    status: invitation.status,
    summary: getProgramInvitationSummary(invitation.message),
    nextStep: getProgramInvitationNextStep(),
    contextLabel: programDirectory.get(invitation.programId) || 'Program invitation',
    primaryActionLabel: 'Respond to invitation',
    reportProgramId: invitation.programId,
    metrics: [
      { label: 'Invitation', value: 'Program' },
      { label: 'Expires', value: formatDateTime(invitation.expiresAt) },
    ],
  }));

  const matchingItems = matchingInvitations.map<EngagementWorkflowItem>((invitation) => ({
    key: `matching-invitation-${invitation.id}`,
    entityId: invitation.id,
    kind: 'matching-invitation',
    title: invitation.engagementId ? `Engagement ${invitation.engagementId.slice(0, 8)}` : 'Matched service request',
    status: invitation.status,
    summary: getMatchingInvitationSummary(invitation.message),
    nextStep: getMatchingInvitationNextStep(),
    contextLabel: invitation.engagementId ? `Matched ${invitation.engagementId.slice(0, 8)}` : 'Matched service request',
    primaryActionLabel: 'Respond to match',
    metrics: [
      { label: 'Invitation', value: 'Matching' },
      {
        label: 'Match score',
        value:
          invitation.matchScore !== null && invitation.matchScore !== undefined
            ? `${Math.round(invitation.matchScore * 100)}%`
            : 'Not disclosed',
      },
      { label: 'Expires', value: formatDateTime(invitation.expiresAt) },
    ],
  }));

  return [...programItems, ...matchingItems];
}

function buildLiveEventWorkflowItems(liveEvents: LiveEventAssignment[]): EngagementWorkflowItem[] {
  return liveEvents.map((event) => ({
    key: `live-event-${event.id}`,
    entityId: event.id,
    kind: 'live-event',
    title: event.name,
    status: event.participationStatus || event.status,
    summary: getLiveEventSummary(event.description),
    nextStep: getLiveEventNextStep(),
    contextLabel: `Live Event: ${event.name}`,
    primaryActionLabel: 'Open finding flow',
    reportHref: getGenericReportsHref(`Live Event: ${event.name}`),
    metrics: [
      { label: 'Rank', value: event.myRank ? `#${event.myRank}` : 'Unranked' },
      { label: 'Score', value: String(event.myScore || 0) },
      { label: 'Valid findings', value: String(event.validSubmissionsCount || 0) },
      { label: 'Ends', value: formatDateTime(event.endTime) },
    ],
  }));
}

function buildCodeReviewWorkflowItems(codeReviewAssignments: CodeReviewAssignment[]): EngagementWorkflowItem[] {
  return codeReviewAssignments.map((assignment) => ({
    key: `code-review-${assignment.id}`,
    entityId: assignment.id,
    kind: 'code-review',
    title: assignment.title,
    status: assignment.status,
    summary: getCodeReviewSummary(assignment.repositoryUrl),
    nextStep: getCodeReviewNextStep(assignment.status),
    contextLabel: `Code Review: ${assignment.title}`,
    primaryActionLabel: assignment.status === 'in_progress' ? 'Continue review' : 'Start review',
    metrics: [
      { label: 'Type', value: assignment.reviewType || 'Security review' },
      { label: 'Findings', value: String(assignment.findingsCount || 0) },
      { label: 'Created', value: formatDateTime(assignment.createdAt) },
    ],
  }));
}

function buildPTaaSWorkflowItems(ptaasOpportunities: PTaaSOpportunity[]): EngagementWorkflowItem[] {
  return ptaasOpportunities.map((opportunity) => ({
    key: `ptaas-${opportunity.id}`,
    entityId: opportunity.id,
    kind: 'ptaas',
    title: opportunity.name,
    status: opportunity.status || 'recommended',
    summary: getPTaaSSummary(opportunity.description, opportunity.reason),
    nextStep: getPTaaSNextStep(),
    contextLabel: `PTaaS: ${opportunity.name}`,
    primaryActionLabel: 'Review assignment',
    metrics: [
      { label: 'Method', value: opportunity.methodology || 'Not disclosed' },
      {
        label: 'Compensation',
        value: opportunity.compensation ? formatCurrency(opportunity.compensation) : 'Not disclosed',
      },
      {
        label: 'Match score',
        value:
          opportunity.matchScore !== null && opportunity.matchScore !== undefined
            ? `${Math.round(opportunity.matchScore * 100)}%`
            : 'Not disclosed',
      },
    ],
  }));
}

export function createParticipationWorkflowAdapter(
  participations: ProgramParticipation[]
): EngagementWorkflowAdapter {
  return {
    id: 'participations',
    buildItems: () => buildParticipationWorkflowItems(participations),
  };
}

export function createInvitationWorkflowAdapter(
  programInvitations: ProgramInvitation[],
  matchingInvitations: MatchingInvitation[],
  programDirectory: Map<string, string>
): EngagementWorkflowAdapter {
  return {
    id: 'invitations',
    buildItems: () => buildInvitationWorkflowItems(programInvitations, matchingInvitations, programDirectory),
  };
}

export function createLiveEventWorkflowAdapter(liveEvents: LiveEventAssignment[]): EngagementWorkflowAdapter {
  return {
    id: 'live-events',
    buildItems: () => buildLiveEventWorkflowItems(liveEvents),
  };
}

export function createCodeReviewWorkflowAdapter(
  codeReviewAssignments: CodeReviewAssignment[]
): EngagementWorkflowAdapter {
  return {
    id: 'code-review',
    buildItems: () => buildCodeReviewWorkflowItems(codeReviewAssignments),
  };
}

export function createPTaaSWorkflowAdapter(ptaasOpportunities: PTaaSOpportunity[]): EngagementWorkflowAdapter {
  return {
    id: 'ptaas',
    buildItems: () => buildPTaaSWorkflowItems(ptaasOpportunities),
  };
}

export function createPublicProgramWorkflowAdapter(
  publicProgramWorkflowItems: EngagementWorkflowItem[]
): EngagementWorkflowAdapter {
  return {
    id: 'public-programs',
    buildItems: () => publicProgramWorkflowItems,
  };
}

export function composeWorkflowItems(adapters: ReadonlyArray<EngagementWorkflowAdapter>): EngagementWorkflowItem[] {
  return adapters.flatMap((adapter) => adapter.buildItems());
}

export function pickDefaultWorkflowItem(items: EngagementWorkflowItem[]): EngagementWorkflowItem | null {
  return (
    items.find((item) => item.kind === 'program-joined') ||
    items.find((item) => item.kind === 'program-invitation') ||
    items[0] ||
    null
  );
}
