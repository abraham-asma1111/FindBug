'use client';

import SectionCard from '@/components/dashboard/SectionCard';
import { formatDateTime } from '@/lib/portal';
import { type EngagementInvitationRow, formatStatusLabel, getPillTone } from './shared';

interface InvitationQueueProps {
  isLoading: boolean;
  invitations: EngagementInvitationRow[];
  pendingAction: string;
  onInspect: (invitationId: string, kind: 'program-invitation' | 'matching-invitation') => void;
  onAccept: (invitationId: string, kind: 'program-invitation' | 'matching-invitation') => void;
  onDecline: (invitationId: string, kind: 'program-invitation' | 'matching-invitation') => void;
}

export default function InvitationQueue({
  isLoading,
  invitations,
  pendingAction,
  onInspect,
  onAccept,
  onDecline,
}: InvitationQueueProps) {
  return (
    <SectionCard
      title="Invitation Queue"
      description="Accept or decline invitations before they expire, then move accepted work into the active board."
    >
      {invitations.length ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-[#e6ddd4]">
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">TYPE</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">OPPORTUNITY</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">MESSAGE</th>
                <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">EXPIRES</th>
                <th className="pb-3 font-semibold text-[#2d2a26]">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {invitations.map((invitation) => {
                const isPending = pendingAction === `${invitation.actionKind}-${invitation.id}`;

                return (
                  <tr key={invitation.id} className="border-b border-[#e6ddd4] last:border-0">
                    <td className="py-4 pr-4 text-[#6d6760]">{invitation.kind}</td>
                    <td className="py-4 pr-4 font-semibold text-[#2d2a26]">{invitation.label}</td>
                    <td className="py-4 pr-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getPillTone(invitation.status)}`}>
                        {formatStatusLabel(invitation.status)}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-[#6d6760]">{invitation.message || 'No message attached.'}</td>
                    <td className="py-4 pr-4 text-[#6d6760]">{formatDateTime(invitation.expiresAt)}</td>
                    <td className="py-4">
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => onInspect(invitation.id, invitation.actionKind)}
                          className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                        >
                          Review
                        </button>
                        <button
                          type="button"
                          onClick={() => onAccept(invitation.id, invitation.actionKind)}
                          disabled={isPending}
                          className="rounded-full bg-[#2d2a26] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#1f1c19] disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Accept
                        </button>
                        <button
                          type="button"
                          onClick={() => onDecline(invitation.id, invitation.actionKind)}
                          disabled={isPending}
                          className="rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7] disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Decline
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-3xl border border-dashed border-[#d8d0c8] bg-[#fcfaf7] p-6 text-sm leading-6 text-[#6d6760]">
          {isLoading ? 'Loading invitation queue...' : 'No pending invitations are waiting for you right now.'}
        </div>
      )}
    </SectionCard>
  );
}
