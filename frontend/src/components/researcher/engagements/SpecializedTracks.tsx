'use client';

import SectionCard from '@/components/dashboard/SectionCard';
import {
  type CodeReviewAssignment,
  type LiveEventAssignment,
  type PTaaSOpportunity,
} from '@/hooks/useResearcherEngagementsData';
import { formatCompactNumber, formatCurrency } from '@/lib/portal';
import { formatStatusLabel, getPillTone, normalizeMinutes } from './shared';

interface SpecializedTracksProps {
  liveEvents: LiveEventAssignment[];
  codeReviewAssignments: CodeReviewAssignment[];
  ptaasOpportunities: PTaaSOpportunity[];
  warnings: Set<string>;
  onInspectLiveEvent: (eventId: string) => void;
  onInspectCodeReview: (engagementId: string) => void;
  onInspectPTaaS: (engagementId: string) => void;
}

export default function SpecializedTracks({
  liveEvents,
  codeReviewAssignments,
  ptaasOpportunities,
  warnings,
  onInspectLiveEvent,
  onInspectCodeReview,
  onInspectPTaaS,
}: SpecializedTracksProps) {
  return (
    <SectionCard
      title="Specialized Tracks"
      description="Service-led opportunities that live beside classic program participation in the researcher portal."
    >
      <div className="space-y-5">
        <div>
          <div className="mb-3 flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Live Events</h3>
            <span className="text-xs font-semibold text-[#8b8177]">{liveEvents.length} tracks</span>
          </div>
          {warnings.has('liveEvents') ? (
            <p className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
              Live event data is unavailable right now.
            </p>
          ) : liveEvents.length ? (
            <div className="space-y-3">
              {liveEvents.slice(0, 3).map((event) => (
                <article key={event.id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(event.status)}`}>
                      {formatStatusLabel(event.status)}
                    </span>
                    <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                      {normalizeMinutes(event.timeRemaining)}
                    </span>
                  </div>
                  <h4 className="mt-3 font-semibold text-[#2d2a26]">{event.name}</h4>
                  <p className="mt-2 text-sm text-[#6d6760]">
                    Rank {event.myRank || '-'} · Score {formatCompactNumber(event.myScore)}
                  </p>
                  <button
                    type="button"
                    onClick={() => onInspectLiveEvent(event.id)}
                    className="mt-4 rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white"
                  >
                    Open workflow
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
              No live event assignments are active right now.
            </p>
          )}
        </div>

        <div>
          <div className="mb-3 flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Code Review</h3>
            <span className="text-xs font-semibold text-[#8b8177]">{codeReviewAssignments.length} assignments</span>
          </div>
          {warnings.has('codeReview') ? (
            <p className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
              Code review assignments are unavailable right now.
            </p>
          ) : codeReviewAssignments.length ? (
            <div className="space-y-3">
              {codeReviewAssignments.slice(0, 3).map((assignment) => (
                <article key={assignment.id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(assignment.status)}`}>
                      {formatStatusLabel(assignment.status)}
                    </span>
                    <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                      {formatStatusLabel(assignment.reviewType)}
                    </span>
                  </div>
                  <h4 className="mt-3 font-semibold text-[#2d2a26]">{assignment.title}</h4>
                  <p className="mt-2 text-sm text-[#6d6760]">{assignment.findingsCount || 0} findings recorded</p>
                  <button
                    type="button"
                    onClick={() => onInspectCodeReview(assignment.id)}
                    className="mt-4 rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white"
                  >
                    Open workflow
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
              No assigned code review engagements are visible yet.
            </p>
          )}
        </div>

        <div>
          <div className="mb-3 flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">PTaaS</h3>
            <span className="text-xs font-semibold text-[#8b8177]">{ptaasOpportunities.length} opportunities</span>
          </div>
          {ptaasOpportunities.length ? (
            <div className="space-y-3">
              {ptaasOpportunities.slice(0, 3).map((opportunity) => (
                <article key={opportunity.id} className="rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        opportunity.status ? getPillTone(opportunity.status) : 'bg-[#f3ede6] text-[#5f5851]'
                      }`}
                    >
                      {formatStatusLabel(opportunity.status || 'Recommended')}
                    </span>
                    <span className="rounded-full bg-[#edf5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                      {formatStatusLabel(opportunity.source)}
                    </span>
                    {opportunity.matchScore !== null && opportunity.matchScore !== undefined ? (
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#2d2a26]">
                        {Math.round(opportunity.matchScore * 100)}% fit
                      </span>
                    ) : null}
                  </div>
                  <h4 className="mt-3 font-semibold text-[#2d2a26]">{opportunity.name}</h4>
                  <p className="mt-2 text-sm text-[#6d6760]">
                    {opportunity.methodology || 'Methodology not disclosed'}
                  </p>
                  <p className="mt-2 text-sm text-[#6d6760]">
                    {opportunity.compensation ? formatCurrency(opportunity.compensation) : 'Compensation not disclosed'}
                  </p>
                  <button
                    type="button"
                    onClick={() => onInspectPTaaS(opportunity.id)}
                    className="mt-4 rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white"
                  >
                    Open workflow
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="rounded-2xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-4 text-sm text-[#6d6760]">
              No PTaaS opportunities are available right now.
            </p>
          )}
        </div>
      </div>
    </SectionCard>
  );
}
