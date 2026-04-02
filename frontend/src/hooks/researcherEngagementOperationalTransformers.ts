'use client';

import type {
  CodeReviewAssignment,
  LiveEventAssignment,
  MatchingInvitation,
  ProgramInvitation,
  ProgramParticipation,
  PTaaSOpportunity,
} from './researcherEngagementTypes';
import { normalizeNumber, normalizeString } from './researcherEngagementNormalize';

export function normalizeParticipation(raw: any): ProgramParticipation | null {
  const programId = normalizeString(raw?.program?.id ?? raw?.program_id);

  if (!programId) {
    return null;
  }

  return {
    id: normalizeString(raw?.id ?? raw?.participation_id ?? programId, programId),
    joinedAt: raw?.joined_at ?? null,
    program: {
      id: programId,
      name: normalizeString(raw?.program?.name, 'Untitled program'),
      description: raw?.program?.description ?? null,
      type: raw?.program?.type ?? null,
      status: raw?.program?.status ?? null,
      visibility: raw?.program?.visibility ?? null,
      budget: raw?.program?.budget !== undefined ? normalizeNumber(raw?.program?.budget) : null,
    },
  };
}

export function normalizeProgramInvitation(raw: any): ProgramInvitation | null {
  const id = normalizeString(raw?.id);
  const programId = normalizeString(raw?.program_id);

  if (!id || !programId) {
    return null;
  }

  return {
    id,
    programId,
    researcherId: raw?.researcher_id ? String(raw.researcher_id) : null,
    status: normalizeString(raw?.status, 'pending').toLowerCase(),
    message: raw?.message ?? null,
    invitedAt: raw?.invited_at ?? null,
    respondedAt: raw?.responded_at ?? null,
    expiresAt: raw?.expires_at ?? null,
  };
}

export function normalizeMatchingInvitation(raw: any): MatchingInvitation | null {
  const id = normalizeString(raw?.id);

  if (!id) {
    return null;
  }

  return {
    id,
    requestId: raw?.request_id ? String(raw.request_id) : null,
    engagementId: raw?.engagement_id ? String(raw.engagement_id) : null,
    matchScore: raw?.match_score !== undefined ? normalizeNumber(raw?.match_score) : null,
    status: normalizeString(raw?.status, 'pending').toLowerCase(),
    message: raw?.message ?? null,
    sentAt: raw?.sent_at ?? null,
    expiresAt: raw?.expires_at ?? null,
    respondedAt: raw?.responded_at ?? null,
  };
}

export function normalizeLiveEvent(raw: any): LiveEventAssignment | null {
  const event = raw?.event ?? raw;
  const id = normalizeString(event?.id);

  if (!id) {
    return null;
  }

  return {
    id,
    name: normalizeString(event?.name, 'Untitled event'),
    description: event?.description ?? null,
    status: normalizeString(event?.status, 'draft').toLowerCase(),
    startTime: event?.start_time ?? null,
    endTime: event?.end_time ?? null,
    prizePool: event?.prize_pool !== undefined ? normalizeNumber(event?.prize_pool) : null,
    myRank: raw?.my_rank !== undefined && raw?.my_rank !== null ? normalizeNumber(raw?.my_rank) : null,
    myScore: raw?.my_score !== undefined && raw?.my_score !== null ? normalizeNumber(raw?.my_score) : null,
    timeRemaining:
      raw?.time_remaining !== undefined && raw?.time_remaining !== null ? normalizeNumber(raw?.time_remaining) : null,
    participationStatus: raw?.participation?.status ?? null,
    submissionsCount:
      raw?.participation?.submissions_count !== undefined
        ? normalizeNumber(raw?.participation?.submissions_count)
        : null,
    validSubmissionsCount:
      raw?.participation?.valid_submissions_count !== undefined
        ? normalizeNumber(raw?.participation?.valid_submissions_count)
        : null,
  };
}

export function normalizeCodeReviewAssignment(raw: any): CodeReviewAssignment | null {
  const id = normalizeString(raw?.id);

  if (!id) {
    return null;
  }

  return {
    id,
    title: normalizeString(raw?.title, 'Untitled code review'),
    repositoryUrl: raw?.repository_url ?? null,
    reviewType: raw?.review_type ?? null,
    status: normalizeString(raw?.status, 'pending').toLowerCase(),
    findingsCount: raw?.findings_count !== undefined ? normalizeNumber(raw?.findings_count) : null,
    reportSubmittedAt: raw?.report_submitted_at ?? null,
    createdAt: raw?.created_at ?? null,
  };
}

export function normalizePTaaSOpportunity(raw: any, source: PTaaSOpportunity['source']): PTaaSOpportunity | null {
  const id = normalizeString(raw?.id ?? raw?.engagement_id);

  if (!id) {
    return null;
  }

  return {
    id,
    name: normalizeString(raw?.name ?? raw?.engagement_name ?? raw?.title, 'Untitled PTaaS engagement'),
    status: raw?.status ?? null,
    methodology: raw?.testing_methodology ?? raw?.methodology ?? null,
    description: raw?.description ?? raw?.summary ?? null,
    matchScore: raw?.match_score !== undefined ? normalizeNumber(raw?.match_score) : null,
    compensation:
      raw?.estimated_compensation !== undefined
        ? normalizeNumber(raw?.estimated_compensation)
        : raw?.base_price !== undefined
          ? normalizeNumber(raw?.base_price)
          : null,
    reason: raw?.reason ?? raw?.match_reason ?? null,
    source,
  };
}

export function mergePTaaSOpportunities(opportunities: PTaaSOpportunity[]): PTaaSOpportunity[] {
  const byId = new Map<string, PTaaSOpportunity>();

  opportunities.forEach((opportunity) => {
    const existing = byId.get(opportunity.id);

    if (!existing) {
      byId.set(opportunity.id, opportunity);
      return;
    }

    byId.set(opportunity.id, {
      ...existing,
      ...opportunity,
      reason: existing.reason || opportunity.reason,
      compensation: existing.compensation ?? opportunity.compensation ?? null,
      matchScore: existing.matchScore ?? opportunity.matchScore ?? null,
    });
  });

  return Array.from(byId.values());
}
