export interface EngagementInvitationRow {
  id: string;
  kind: string;
  actionKind: 'program-invitation' | 'matching-invitation';
  label: string;
  status: string;
  message?: string | null;
  expiresAt?: string | null;
}

export interface ActiveTrackRow {
  id: string;
  name: string;
  type: string;
  status?: string | null;
  updatedAt?: string | null;
  actionHref: string;
  actionLabel: string;
}

export type EngagementWorkflowKind =
  | 'program-open'
  | 'program-joined'
  | 'program-invitation'
  | 'matching-invitation'
  | 'live-event'
  | 'code-review'
  | 'ptaas';

export interface EngagementWorkflowMetric {
  label: string;
  value: string;
}

export interface EngagementWorkflowItem {
  key: string;
  entityId: string;
  kind: EngagementWorkflowKind;
  title: string;
  status?: string | null;
  summary: string;
  nextStep: string;
  contextLabel: string;
  primaryActionLabel: string;
  reportHref?: string;
  reportProgramId?: string;
  metrics: EngagementWorkflowMetric[];
}

export function formatStatusLabel(value?: string | null): string {
  if (!value) {
    return 'Unknown';
  }

  return value
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function normalizeMinutes(minutes?: number | null): string {
  if (minutes === null || minutes === undefined || Number.isNaN(minutes)) {
    return 'No timer';
  }

  if (minutes < 60) {
    return `${minutes} min left`;
  }

  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  return remainder ? `${hours}h ${remainder}m left` : `${hours}h left`;
}

export function getProgramTone(programType?: string | null): string {
  switch (programType?.toLowerCase()) {
    case 'vdp':
      return 'from-[#d9edf7] via-[#edf6fb] to-[#fcf8f2]';
    default:
      return 'from-[#f8e3d6] via-[#fcf4ea] to-[#fffaf5]';
  }
}

export function getPillTone(value?: string | null): string {
  switch (value?.toLowerCase()) {
    case 'active':
    case 'valid':
    case 'accepted':
    case 'assigned':
    case 'in_progress':
    case 'in progress':
      return 'bg-[#eef7ef] text-[#24613a]';
    case 'pending':
    case 'triaged':
    case 'matching':
    case 'scheduled':
      return 'bg-[#faf1e1] text-[#9a6412]';
    case 'declined':
    case 'invalid':
    case 'cancelled':
    case 'closed':
      return 'bg-[#fff2f1] text-[#b42318]';
    default:
      return 'bg-[#edf5fb] text-[#2d78a8]';
  }
}
