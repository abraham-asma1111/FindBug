export interface EngagementProgram {
  id: string;
  name: string;
  description?: string | null;
  type: string;
  status: string;
  visibility: string;
  budget: number;
  organizationName?: string | null;
  matchScore?: number | null;
  reason?: string | null;
  source: 'catalog' | 'recommendation' | 'matching';
}

export interface ProgramInvitation {
  id: string;
  programId: string;
  researcherId?: string | null;
  status: string;
  message?: string | null;
  invitedAt?: string | null;
  respondedAt?: string | null;
  expiresAt?: string | null;
}

export interface ParticipationProgram {
  id: string;
  name: string;
  description?: string | null;
  type?: string | null;
  status?: string | null;
  visibility?: string | null;
  budget?: number | null;
}

export interface ProgramParticipation {
  id: string;
  joinedAt?: string | null;
  program: ParticipationProgram;
}

export interface MatchingInvitation {
  id: string;
  requestId?: string | null;
  engagementId?: string | null;
  matchScore?: number | null;
  status: string;
  message?: string | null;
  sentAt?: string | null;
  expiresAt?: string | null;
  respondedAt?: string | null;
}

export interface LiveEventAssignment {
  id: string;
  name: string;
  description?: string | null;
  status: string;
  startTime?: string | null;
  endTime?: string | null;
  prizePool?: number | null;
  myRank?: number | null;
  myScore?: number | null;
  timeRemaining?: number | null;
  participationStatus?: string | null;
  submissionsCount?: number | null;
  validSubmissionsCount?: number | null;
}

export interface CodeReviewAssignment {
  id: string;
  title: string;
  repositoryUrl?: string | null;
  reviewType?: string | null;
  status: string;
  findingsCount?: number | null;
  reportSubmittedAt?: string | null;
  createdAt?: string | null;
}

export interface PTaaSOpportunity {
  id: string;
  name: string;
  status?: string | null;
  methodology?: string | null;
  description?: string | null;
  matchScore?: number | null;
  compensation?: number | null;
  reason?: string | null;
  source: 'matching' | 'researcher-recommendation';
}

export interface ResearcherEngagementsState {
  recommendedPrograms: EngagementProgram[];
  publicPrograms: EngagementProgram[];
  matchedPrograms: EngagementProgram[];
  programInvitations: ProgramInvitation[];
  participations: ProgramParticipation[];
  matchingInvitations: MatchingInvitation[];
  liveEvents: LiveEventAssignment[];
  codeReviewAssignments: CodeReviewAssignment[];
  ptaasOpportunities: PTaaSOpportunity[];
  warnings: string[];
}

export type LoaderKey =
  | 'recommendedPrograms'
  | 'publicPrograms'
  | 'matchedPrograms'
  | 'programInvitations'
  | 'participations'
  | 'matchingInvitations'
  | 'ptaasMatching'
  | 'ptaasResearcher'
  | 'liveEvents'
  | 'codeReview';
