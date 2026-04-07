'use client';

import Link from 'next/link';
import SectionCard from '@/components/dashboard/SectionCard';
import { formatDateTime } from '@/lib/portal';
import { type ActiveTrackRow, formatStatusLabel, getPillTone } from './shared';

interface ActiveParticipationBoardProps {
  isLoading: boolean;
  tracks: ActiveTrackRow[];
  getTrackStep: (track: { type: string; status?: string | null }) => string;
  onInspect: (trackId: string, trackType: string) => void;
}

export default function ActiveParticipationBoard({
  isLoading,
  tracks,
  getTrackStep,
  onInspect,
}: ActiveParticipationBoardProps) {
  return (
    <SectionCard
      title="Active Participation Board"
      headerAlign="center"
    >
      {tracks.length ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-sm">
            <thead>
              <tr className="border-b border-[#e6ddd4]">
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">TRACK</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">TYPE</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">LAST MILE</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">UPDATED</th>
                <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {tracks.map((track) => (
                <tr key={`${track.type}-${track.id}`} className="border-b border-[#e6ddd4] last:border-0">
                  <td className="py-4 pr-4 font-semibold text-[#2d2a26]">{track.name}</td>
                  <td className="py-4 pr-4 text-[#6d6760]">{formatStatusLabel(track.type)}</td>
                  <td className="py-4 pr-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(track.status)}`}>
                      {formatStatusLabel(track.status)}
                    </span>
                  </td>
                  <td className="py-4 pr-4 text-[#6d6760]">{getTrackStep({ type: track.type, status: track.status })}</td>
                  <td className="py-4 pr-4 text-[#6d6760]">{formatDateTime(track.updatedAt)}</td>
                  <td className="py-4">
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => onInspect(track.id, track.type)}
                        className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                      >
                        Workflow
                      </button>
                      <Link
                        href={track.actionHref}
                        className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                      >
                        {track.actionLabel}
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-6 text-sm leading-6 text-[#6d6760]">
          {isLoading
            ? 'Loading active participation board...'
            : 'You have no active engagement tracks yet. Join a program or accept an invitation first.'}
        </div>
      )}
    </SectionCard>
  );
}
