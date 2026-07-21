export function getJoinedProgramSummary(description?: string | null): string {
  return (
    description || 'This active program is ready for vulnerability submission, evidence updates, and triage replies.'
  );
}

export function getJoinedProgramNextStep(): string {
  return 'Use the inline report composer below to file a vulnerability without leaving the engagement workflow.';
}

export function getOpenProgramSummary(description?: string | null): string {
  return (
    description || 'Review the target scope, confirm the exposure, then use the engagement to create a report.'
  );
}

export function getOpenProgramNextStep(isJoined: boolean): string {
  return isJoined
    ? 'Use the inline report composer below to submit the vulnerability against this joined program.'
    : 'Join this program first. Once joined, the engagement unlocks direct vulnerability submission.';
}

export function getProgramInvitationSummary(message?: string | null): string {
  return message || 'This invitation grants direct access to a scoped program workflow.';
}

export function getProgramInvitationNextStep(): string {
  return 'Accept to move the program into your active participation board, or decline if the scope does not fit.';
}

export function getMatchingInvitationSummary(message?: string | null): string {
  return message || 'This request matched your researcher profile to a specialized delivery workflow.';
}

export function getMatchingInvitationNextStep(): string {
  return 'Accept the invitation to move it into an active operational track, or decline to keep your queue clean.';
}

export function getLiveEventSummary(description?: string | null): string {
  return description || 'Work from the event scope, then link accepted findings back into the live competition.';
}

export function getLiveEventNextStep(): string {
  return 'Use the event engagement to continue the finding flow and keep the leaderboard submission path visible.';
}

export function getCodeReviewSummary(repositoryUrl?: string | null): string {
  return repositoryUrl || 'Assigned repository context is available from this engagement once the review starts.';
}

export function getCodeReviewNextStep(status?: string | null): string {
  return status === 'in_progress'
    ? 'Continue adding findings and submit the final review from this engagement.'
    : 'Start the review here, then move into finding capture and final report submission.';
}

export function getPTaaSSummary(description?: string | null, reason?: string | null): string {
  return description || reason || 'This PTaaS opportunity is driven by assignment and service delivery.';
}

export function getPTaaSNextStep(): string {
  return 'Review the service fit, wait for assignment confirmation, then continue the coordination handoff.';
}
