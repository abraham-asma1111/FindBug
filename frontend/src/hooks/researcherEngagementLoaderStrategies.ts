'use client';

import type { LoaderKey, PTaaSOpportunity, ResearcherEngagementsState } from './researcherEngagementTypes';
import {
  mergePrograms,
  normalizeCatalogProgram,
  normalizeMatchedProgram,
  normalizeRecommendedProgram,
} from './researcherEngagementProgramTransformers';
import {
  normalizeCodeReviewAssignment,
  normalizeLiveEvent,
  normalizeMatchingInvitation,
  normalizeParticipation,
  normalizeProgramInvitation,
  normalizePTaaSOpportunity,
} from './researcherEngagementOperationalTransformers';

export type PTaaSAccumulator = {
  matching: PTaaSOpportunity[];
  researcher: PTaaSOpportunity[];
};

function applyRecommendedPrograms(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.recommendedPrograms = mergePrograms(
    (responseData?.recommendations || []).map((entry: any) => normalizeRecommendedProgram(entry)).filter(Boolean)
  ) as typeof nextState.recommendedPrograms;
}

function applyPublicPrograms(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.publicPrograms = mergePrograms(
    (responseData || []).map((entry: any) => normalizeCatalogProgram(entry)).filter(Boolean)
  ) as typeof nextState.publicPrograms;
}

function applyMatchedPrograms(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.matchedPrograms = mergePrograms(
    (responseData?.programs || []).map((entry: any) => normalizeMatchedProgram(entry)).filter(Boolean)
  ) as typeof nextState.matchedPrograms;
}

function applyProgramInvitations(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.programInvitations = (responseData || [])
    .map((entry: any) => normalizeProgramInvitation(entry))
    .filter(Boolean) as typeof nextState.programInvitations;
}

function applyParticipations(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.participations = (responseData || [])
    .map((entry: any) => normalizeParticipation(entry))
    .filter(Boolean) as typeof nextState.participations;
}

function applyMatchingInvitations(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.matchingInvitations = (responseData?.invitations || [])
    .map((entry: any) => normalizeMatchingInvitation(entry))
    .filter(Boolean) as typeof nextState.matchingInvitations;
}

function applyPTaaSMatching(responseData: any, _: ResearcherEngagementsState, ptaasAccumulator: PTaaSAccumulator) {
  ptaasAccumulator.matching = (responseData?.opportunities || [])
    .map((entry: any) => normalizePTaaSOpportunity(entry, 'matching'))
    .filter(Boolean) as PTaaSOpportunity[];
}

function applyPTaaSResearcher(responseData: any, _: ResearcherEngagementsState, ptaasAccumulator: PTaaSAccumulator) {
  ptaasAccumulator.researcher = (responseData?.recommendations || [])
    .map((entry: any) => normalizePTaaSOpportunity(entry, 'researcher-recommendation'))
    .filter(Boolean) as PTaaSOpportunity[];
}

function applyLiveEvents(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.liveEvents = (responseData || [])
    .map((entry: any) => normalizeLiveEvent(entry))
    .filter(Boolean) as typeof nextState.liveEvents;
}

function applyCodeReview(responseData: any, nextState: ResearcherEngagementsState) {
  nextState.codeReviewAssignments = (responseData?.engagements || [])
    .map((entry: any) => normalizeCodeReviewAssignment(entry))
    .filter(Boolean) as typeof nextState.codeReviewAssignments;
}

export function createLoaderResponseStrategies(
  nextState: ResearcherEngagementsState,
  ptaasAccumulator: PTaaSAccumulator
) {
  return {
    recommendedPrograms: (responseData: any) => applyRecommendedPrograms(responseData, nextState),
    publicPrograms: (responseData: any) => applyPublicPrograms(responseData, nextState),
    matchedPrograms: (responseData: any) => applyMatchedPrograms(responseData, nextState),
    programInvitations: (responseData: any) => applyProgramInvitations(responseData, nextState),
    participations: (responseData: any) => applyParticipations(responseData, nextState),
    matchingInvitations: (responseData: any) => applyMatchingInvitations(responseData, nextState),
    ptaasMatching: (responseData: any) => applyPTaaSMatching(responseData, nextState, ptaasAccumulator),
    ptaasResearcher: (responseData: any) => applyPTaaSResearcher(responseData, nextState, ptaasAccumulator),
    liveEvents: (responseData: any) => applyLiveEvents(responseData, nextState),
    codeReview: (responseData: any) => applyCodeReview(responseData, nextState),
  } satisfies Record<LoaderKey, (responseData: any) => void>;
}
