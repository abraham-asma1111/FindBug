'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { formatCurrency, formatDateTime } from '@/lib/portal';
import ProgramDetailModal from './ProgramDetailModal';

interface Program {
  id: string;
  name: string;
  description?: string;
  program_type: string;
  status: string;
  visibility: string;
  budget?: number;
  created_at: string;
  updated_at?: string;
}

interface ProgramListProps {
  programs: Program[];
  onUpdate: () => void;
  isArchived?: boolean;
}

export default function ProgramList({ programs, onUpdate, isArchived = false }: ProgramListProps) {
  const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'public':
        return 'bg-[#e6f7ed] text-[#0d7a3d]';
      case 'draft':
        return 'bg-[#faf1e1] text-[#9a6412]';
      case 'paused':
        return 'bg-[#fff4e6] text-[#b54708]';
      case 'closed':
        return 'bg-[#f3ede6] text-[#5f5851]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'bounty':
        return 'bg-[#edf5fb] text-[#2d78a8]';
      case 'vdp':
        return 'bg-[#f3e8ff] text-[#6b21a8]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  return (
    <>
      <div className="space-y-4">
        {programs.map((program) => (
          <Card key={program.id} className="hover:border-[#d4c5b3] transition-colors">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                {/* Badges */}
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getTypeColor(program.program_type)}`}>
                    {program.program_type.toUpperCase()}
                  </span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(program.status)}`}>
                    {program.status.charAt(0).toUpperCase() + program.status.slice(1)}
                  </span>
                  {program.visibility && (
                    <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                      {program.visibility}
                    </span>
                  )}
                </div>

                {/* Program Name */}
                <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">
                  {program.name}
                </h3>

                {/* Description */}
                {program.description && (
                  <p className="text-sm text-[#6d6760] leading-relaxed mb-4 line-clamp-2">
                    {program.description}
                  </p>
                )}

                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-6 text-sm">
                  {program.budget !== undefined && program.budget !== null && (
                    <div>
                      <span className="text-[#8b8177]">Budget: </span>
                      <span className="font-semibold text-[#2d2a26]">
                        {formatCurrency(program.budget)}
                      </span>
                    </div>
                  )}
                  <div>
                    <span className="text-[#8b8177]">Created: </span>
                    <span className="font-semibold text-[#2d2a26]">
                      {formatDateTime(program.created_at)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex-shrink-0">
                <Button
                  variant="secondary"
                  onClick={() => setSelectedProgram(program)}
                >
                  View Details
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Program Detail Modal */}
      {selectedProgram && (
        <ProgramDetailModal
          program={selectedProgram}
          onClose={() => setSelectedProgram(null)}
          onUpdate={() => {
            setSelectedProgram(null);
            onUpdate();
          }}
          isArchived={isArchived}
        />
      )}
    </>
  );
}
