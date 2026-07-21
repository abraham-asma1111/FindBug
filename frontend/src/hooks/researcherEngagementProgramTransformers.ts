'use client';

import type { EngagementProgram } from './researcherEngagementTypes';
import { normalizeNumber, normalizeString } from './researcherEngagementNormalize';

export function normalizeCatalogProgram(raw: any): EngagementProgram | null {
  const id = normalizeString(raw?.id);

  if (!id) {
    return null;
  }

  return {
    id,
    name: normalizeString(raw?.name, 'Untitled program'),
    description: typeof raw?.description === 'string' ? raw.description : null,
    type: normalizeString(raw?.type, 'bounty').toLowerCase(),
    status: normalizeString(raw?.status, 'public').toLowerCase(),
    visibility: normalizeString(raw?.visibility, 'public').toLowerCase(),
    budget: normalizeNumber(raw?.budget),
    organizationName:
      typeof (raw?.organization_name ?? raw?.organization?.name) === 'string'
        ? raw.organization_name ?? raw.organization?.name
        : null,
    matchScore: null,
    reason: null,
    source: 'catalog',
  };
}

export function normalizeRecommendedProgram(raw: any): EngagementProgram | null {
  const id = normalizeString(raw?.program_id);

  if (!id) {
    return null;
  }

  return {
    id,
    name: normalizeString(raw?.program_name, 'Untitled program'),
    description:
      typeof (raw?.program_description ?? raw?.description) === 'string'
        ? raw.program_description ?? raw.description
        : null,
    type: normalizeString(raw?.program_type, 'bounty').toLowerCase(),
    status: normalizeString(raw?.status, 'public').toLowerCase(),
    visibility: normalizeString(raw?.visibility, 'public').toLowerCase(),
    budget: normalizeNumber(raw?.budget),
    organizationName: typeof raw?.organization_name === 'string' ? raw.organization_name : null,
    matchScore: raw?.match_score !== undefined ? normalizeNumber(raw?.match_score) : null,
    reason: typeof raw?.reason === 'string' ? raw.reason : null,
    source: 'recommendation',
  };
}

export function normalizeMatchedProgram(raw: any): EngagementProgram | null {
  const id = normalizeString(raw?.id);

  if (!id) {
    return null;
  }

  return {
    id,
    name: normalizeString(raw?.name, 'Untitled program'),
    description: typeof raw?.description === 'string' ? raw.description : null,
    type: normalizeString(raw?.type, 'bounty').toLowerCase(),
    status: normalizeString(raw?.status, 'public').toLowerCase(),
    visibility: normalizeString(raw?.visibility, 'public').toLowerCase(),
    budget: normalizeNumber(raw?.budget),
    organizationName:
      typeof (raw?.organization_name ?? raw?.organization?.name) === 'string'
        ? raw.organization_name ?? raw.organization?.name
        : null,
    matchScore: raw?.match_score !== undefined ? normalizeNumber(raw?.match_score) : null,
    reason: typeof (raw?.match_reason ?? raw?.reason) === 'string' ? raw.match_reason ?? raw.reason : null,
    source: 'matching',
  };
}

export function mergePrograms(programs: EngagementProgram[]): EngagementProgram[] {
  const byId = new Map<string, EngagementProgram>();

  programs.forEach((program) => {
    const existing = byId.get(program.id);

    if (!existing) {
      byId.set(program.id, program);
      return;
    }

    byId.set(program.id, {
      ...existing,
      ...program,
      status: program.status || existing.status,
      visibility: program.visibility || existing.visibility,
      reason: existing.reason || program.reason,
      organizationName: existing.organizationName || program.organizationName,
      matchScore: existing.matchScore ?? program.matchScore ?? null,
    });
  });

  return Array.from(byId.values());
}
