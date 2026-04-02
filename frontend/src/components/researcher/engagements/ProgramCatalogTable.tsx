'use client';

import { type ReactNode } from 'react';
import SectionCard from '@/components/dashboard/SectionCard';
import { type EngagementProgram } from '@/hooks/useResearcherEngagementsData';
import { formatCurrency } from '@/lib/portal';
import { formatStatusLabel, getPillTone } from './shared';

interface ProgramCatalogTableProps {
  isLoading: boolean;
  programs: EngagementProgram[];
  joinedProgramIds: Set<string>;
  renderAction: (program: EngagementProgram) => ReactNode;
  onInspect: (programId: string) => void;
}

export default function ProgramCatalogTable({
  isLoading,
  programs,
  joinedProgramIds,
  renderAction,
  onInspect,
}: ProgramCatalogTableProps) {
  return (
    <SectionCard
      title="Program Catalog"
      description="Public programs and VDP opportunities that can turn directly into researcher report workflow."
    >
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead>
            <tr className="border-b border-[#e6ddd4]">
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PROGRAM</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">TYPE</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">VISIBILITY</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">BUDGET</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">WORKFLOW</th>
              <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {programs.length ? (
              programs.map((program) => (
                <tr key={program.id} className="border-b border-[#e6ddd4] last:border-0">
                  <td className="py-4 pr-4">
                    <p className="font-semibold text-[#2d2a26]">{program.name}</p>
                    <p className="mt-1 text-[#6d6760]">
                      {program.description || 'Open the engagement and review scope before joining.'}
                    </p>
                  </td>
                  <td className="py-4 pr-4 text-[#6d6760]">{formatStatusLabel(program.type)}</td>
                  <td className="py-4 pr-4 text-[#6d6760]">{formatStatusLabel(program.visibility)}</td>
                  <td className="py-4 pr-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(program.status)}`}>
                      {formatStatusLabel(program.status)}
                    </span>
                  </td>
                  <td className="py-4 pr-4 font-semibold text-[#2d2a26]">
                    {program.budget ? formatCurrency(program.budget) : 'Not disclosed'}
                  </td>
                  <td className="py-4 pr-4 text-[#6d6760]">
                    {joinedProgramIds.has(program.id)
                      ? 'You can report vulnerabilities from this joined program immediately.'
                      : 'Join first, then move into the reports workflow with the program preselected.'}
                  </td>
                  <td className="py-4">
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => onInspect(program.id)}
                        className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                      >
                        Workflow
                      </button>
                      {renderAction(program)}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="py-10 text-center text-sm text-[#6d6760]">
                  {isLoading ? 'Loading public program catalog...' : 'No public programs are available right now.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
