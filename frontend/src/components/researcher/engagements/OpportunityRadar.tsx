'use client';

import { type ReactNode } from 'react';
import SectionCard from '@/components/dashboard/SectionCard';
import { type EngagementProgram } from '@/hooks/useResearcherEngagementsData';
import { formatCurrency } from '@/lib/portal';
import { formatStatusLabel, getPillTone, getProgramTone } from './shared';

interface OpportunityRadarProps {
  isLoading: boolean;
  programs: EngagementProgram[];
  renderAction: (program: EngagementProgram) => ReactNode;
  onInspect: (programId: string) => void;
}

export default function OpportunityRadar({ isLoading, programs, renderAction, onInspect }: OpportunityRadarProps) {
  return (
    <SectionCard
      title="Opportunity Radar"
      description="Bug bounty and VDP opportunities most aligned with your profile. Open the detail page to inspect scope before joining."
    >
      <div className="grid gap-4 md:grid-cols-2">
        {programs.length ? (
          programs.map((program) => (
            <article
              key={program.id}
              className={`rounded-[28px] border border-[#e6ddd4] bg-gradient-to-br ${getProgramTone(program.type)} p-5`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(program.type)}`}>
                  {formatStatusLabel(program.type)}
                </span>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(program.source)}`}>
                  {formatStatusLabel(program.source)}
                </span>
                {program.matchScore !== null && program.matchScore !== undefined ? (
                  <span className="rounded-full bg-white/80 px-3 py-1 text-xs font-semibold text-[#2d2a26]">
                    {Math.round(program.matchScore * 100)}% fit
                  </span>
                ) : null}
              </div>
              <h3 className="mt-4 text-lg font-semibold tracking-tight text-[#2d2a26]">{program.name}</h3>
              <p className="mt-2 text-sm text-[#6d6760]">
                {program.organizationName || 'Organization disclosure unavailable'}
              </p>
              <p className="mt-4 min-h-[72px] text-sm leading-6 text-[#5b534c]">
                {program.reason || program.description || 'Open the engagement and inspect the scope before joining.'}
              </p>
              <div className="mt-5 flex items-center justify-between gap-3 border-t border-white/60 pt-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Budget</p>
                  <p className="mt-2 text-base font-semibold text-[#2d2a26]">
                    {program.budget ? formatCurrency(program.budget) : 'Not disclosed'}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => onInspect(program.id)}
                    className="rounded-full border border-[#d8d0c8] bg-white/70 px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-white"
                  >
                    View details
                  </button>
                  {renderAction(program)}
                </div>
              </div>
            </article>
          ))
        ) : (
          <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-6 text-sm leading-6 text-[#6d6760] md:col-span-2">
            {isLoading ? 'Loading opportunity radar...' : 'No recommended or matched programs are available right now.'}
          </div>
        )}
      </div>
    </SectionCard>
  );
}
