'use client';

import { useEffect, useMemo, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import Alert from '@/components/ui/Alert';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import { useApiQuery } from '@/hooks/useApiQuery';
import api from '@/lib/api';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import {
  Banner,
  EmptyCollection,
  MetricGrid,
  SectionCard,
  StatusBadge,
  WorkflowTimeline,
  formatStatusLabel,
  formatWorkflowDate,
  formatWorkflowMoney,
} from './shared';

interface EventRecord {
  event: {
    id: string;
    name: string;
    description?: string | null;
    status: string;
    start_time?: string | null;
    end_time?: string | null;
    prize_pool?: number | string | null;
    scope_description?: string | null;
    target_assets?: string | null;
    reward_policy?: string | null;
  };
  participation: {
    status: string;
    submissions_count: number;
    valid_submissions_count: number;
    prize_amount?: number | string | null;
  };
  my_rank?: number | null;
  my_score: number;
  time_remaining?: number | null;
  invitation_id?: string | null;
  invitation_status?: string | null;
  invitation_expires_at?: string | null;
}

interface LeaderboardEntry {
  rank: number;
  researcher_id: string;
  researcher_name: string;
  score: number;
  submissions_count: number;
  valid_submissions_count: number;
  prize_amount?: number | string | null;
}

interface LeaderboardResponse {
  event_id: string;
  event_name: string;
  entries: LeaderboardEntry[];
}

interface ResearcherReport {
  id: string;
  title: string;
  severity: string;
  status: string;
  report_number: string;
  program_name: string;
}

const eventWorkflow = [
  {
    label: 'Invitation and event acceptance',
    detail: 'Live events typically start with an explicit invitation and fast pre-event confirmation.',
    state: 'complete' as const,
  },
  {
    label: 'Real-time hunting window',
    detail: 'Once the event is active, researchers move quickly while triage and the leaderboard update in near real time.',
    state: 'active' as const,
  },
  {
    label: 'Finding linkage and leaderboard impact',
    detail: 'Attach eligible reports to the event so the platform can score valid submissions and compute ranking.',
    state: 'active' as const,
  },
  {
    label: 'Closure and payout',
    detail: 'When the event closes, ranking, reward allocation, and post-event learnings become the handoff package.',
    state: 'upcoming' as const,
  },
];

function formatTimeRemaining(minutes?: number | null): string {
  if (!minutes && minutes !== 0) {
    return 'Timer unavailable';
  }

  if (minutes < 60) {
    return `${minutes} minutes left`;
  }

  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  return remainder ? `${hours}h ${remainder}m left` : `${hours}h left`;
}

export default function ResearcherEventsWorkspace() {
  const user = useAuthStore((state) => state.user);
  const [selectedEventId, setSelectedEventId] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'leaderboard' | 'submissions'>('overview');
  const [selectedReportId, setSelectedReportId] = useState('');
  const [pageError, setPageError] = useState('');
  const [pageSuccess, setPageSuccess] = useState('');
  const [pendingAction, setPendingAction] = useState('');

  const {
    data: events,
    isLoading: isLoadingEvents,
    error: eventsError,
    refetch: refetchEvents,
  } = useApiQuery<EventRecord[]>('/live-events/researcher/my-events', {
    enabled: !!user,
  });

  useEffect(() => {
    if (!events?.length) {
      setSelectedEventId('');
      return;
    }

    if (!selectedEventId || !events.some((entry) => entry.event.id === selectedEventId)) {
      setSelectedEventId(events[0].event.id);
    }
  }, [events, selectedEventId]);

  const selectedEvent = useMemo(
    () => events?.find((entry) => entry.event.id === selectedEventId) ?? null,
    [events, selectedEventId]
  );

  const {
    data: leaderboard,
    isLoading: isLoadingLeaderboard,
    refetch: refetchLeaderboard,
  } = useApiQuery<LeaderboardResponse>(
    selectedEventId ? `/live-events/${selectedEventId}/leaderboard` : '',
    { enabled: !!user && !!selectedEventId }
  );

  const { data: reports } = useApiQuery<ResearcherReport[]>('/reports/my-reports?limit=100&offset=0', {
    enabled: !!user,
  });

  const metrics = selectedEvent
    ? [
        {
          label: 'Event status',
          value: formatStatusLabel(selectedEvent.event.status),
          helper: selectedEvent.participation.status ? `Participation ${formatStatusLabel(selectedEvent.participation.status)}` : 'Participation state pending',
        },
        {
          label: 'My score',
          value: String(selectedEvent.my_score || 0),
          helper: selectedEvent.my_rank ? `Current rank #${selectedEvent.my_rank}` : 'Rank not assigned yet',
        },
        {
          label: 'Valid submissions',
          value: String(selectedEvent.participation.valid_submissions_count || 0),
          helper: `${selectedEvent.participation.submissions_count || 0} submissions linked`,
        },
        {
          label: 'Prize track',
          value: formatWorkflowMoney(selectedEvent.participation.prize_amount ?? selectedEvent.event.prize_pool),
          helper: formatTimeRemaining(selectedEvent.time_remaining),
        },
      ]
    : [];

  async function handleInvitationResponse(accept: boolean) {
    if (!selectedEvent?.invitation_id) {
      return;
    }

    try {
      setPendingAction(accept ? 'accept' : 'decline');
      setPageError('');
      setPageSuccess('');
      await api.post(`/live-events/invitations/${selectedEvent.invitation_id}/respond`, { accept });
      setPageSuccess(`Event invitation ${accept ? 'accepted' : 'declined'} successfully.`);
      await Promise.all([refetchEvents(), refetchLeaderboard()]);
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to update the event invitation.');
    } finally {
      setPendingAction('');
    }
  }

  async function handleLinkReport() {
    if (!selectedEventId || !selectedReportId) {
      setPageError('Choose a report before linking it to the event.');
      return;
    }

    try {
      setPendingAction('link-report');
      setPageError('');
      setPageSuccess('');
      await api.post(`/live-events/${selectedEventId}/submit`, { report_id: selectedReportId });
      setPageSuccess('Report linked to the live event. Refreshing leaderboard context now.');
      await Promise.all([refetchEvents(), refetchLeaderboard()]);
      setSelectedReportId('');
    } catch (error: any) {
      setPageError(error.response?.data?.detail || 'Failed to link the report to the event.');
    } finally {
      setPendingAction('');
    }
  }

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Live Events Command Desk"
          subtitle="Track invitations, event timing, leaderboard position, and report linkage from a single live-event workflow page."
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-sm tracking-[0.25em]"
        >
          <div className="space-y-6">
            <Banner
              title="Live Hacking Events"
              subtitle="This page is now event-driven instead of static. Invitations, live participation, leaderboard pressure, and report linkage all come from the real event APIs."
              accentClassName="bg-[linear-gradient(135deg,#8b1d26_0%,#d72c3e_45%,#ff7b65_100%)]"
              badge="Real-Time Competition Workflow"
              icon="🎯"
            />

            {pageError ? (
              <Alert variant="error" title="Workflow issue">
                {pageError}
              </Alert>
            ) : null}

            {pageSuccess ? (
              <Alert variant="success" title="Workflow updated">
                {pageSuccess}
              </Alert>
            ) : null}

            {eventsError ? (
              <Alert variant="warning" title="Event data is unavailable">
                {eventsError.message}
              </Alert>
            ) : null}

            <SectionCard title="My live events" description="Choose an invited or active event to open its event-day command surface.">
              {isLoadingEvents ? (
                <p className="text-sm text-[#6d6760]">Loading event assignments...</p>
              ) : events?.length ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  {events.map((entry) => (
                    <button
                      key={entry.event.id}
                      type="button"
                      onClick={() => setSelectedEventId(entry.event.id)}
                      className={`rounded-[20px] border p-5 text-left transition ${
                        entry.event.id === selectedEventId
                          ? 'border-[#d72c3e] bg-[#fff0ee]'
                          : 'border-[#e6ddd4] bg-[#fcfaf7] hover:border-[#efb1aa]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-lg font-semibold text-[#2d2a26]">{entry.event.name}</p>
                          <p className="mt-2 text-sm text-[#6d6760]">{entry.event.description || 'No event description provided.'}</p>
                        </div>
                        <StatusBadge status={entry.event.status} />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <EmptyCollection
                  title="No live hacking events yet"
                  description="Invited and active events will appear here once an organization adds you to the participant list."
                />
              )}
            </SectionCard>

            {selectedEvent ? (
              <>
                <MetricGrid items={metrics} />

                <div className="flex flex-wrap gap-2 rounded-[22px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-2">
                  {(['overview', 'leaderboard', 'submissions'] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                        activeTab === tab
                          ? 'bg-[#d72c3e] text-white'
                          : 'text-[#6d6760] hover:bg-[#f5efe8] hover:text-[#2d2a26]'
                      }`}
                    >
                      {formatStatusLabel(tab)}
                    </button>
                  ))}
                </div>

                {activeTab === 'overview' ? (
                  <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
                    <SectionCard
                      title="Event brief"
                      description="Scope, target assets, rewards, and invitation state for the selected live event."
                      action={
                        selectedEvent.invitation_status === 'pending' ? (
                          <div className="flex gap-2">
                            <Button variant="outline" isLoading={pendingAction === 'decline'} onClick={() => handleInvitationResponse(false)}>
                              Decline
                            </Button>
                            <Button variant="danger" isLoading={pendingAction === 'accept'} onClick={() => handleInvitationResponse(true)}>
                              Accept
                            </Button>
                          </div>
                        ) : undefined
                      }
                    >
                      <div className="space-y-5">
                        <div className="flex flex-wrap gap-2">
                          <StatusBadge status={selectedEvent.event.status} />
                          <StatusBadge status={selectedEvent.participation.status} />
                          {selectedEvent.invitation_status ? <StatusBadge status={selectedEvent.invitation_status} /> : null}
                        </div>
                        <p className="text-sm leading-6 text-[#6d6760]">
                          {selectedEvent.event.description || 'No event summary has been published yet.'}
                        </p>
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Starts</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">{formatWorkflowDate(selectedEvent.event.start_time)}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-[#8b8177]">Ends</p>
                            <p className="mt-2 text-sm font-semibold text-[#2d2a26]">{formatWorkflowDate(selectedEvent.event.end_time)}</p>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Scope description</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                            {selectedEvent.event.scope_description || 'No additional scope notes were attached.'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Target assets</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                            {selectedEvent.event.target_assets || 'Target assets will be shared in the event briefing.'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#2d2a26]">Reward policy</p>
                          <p className="mt-2 text-sm leading-6 text-[#6d6760]">
                            {selectedEvent.event.reward_policy || 'Reward rules were not published in this payload.'}
                          </p>
                        </div>
                      </div>
                    </SectionCard>

                    <div className="space-y-6">
                      <SectionCard title="Event-day workflow" description="This tracks the live-competition pattern used by larger event-driven platforms.">
                        <WorkflowTimeline steps={eventWorkflow} />
                      </SectionCard>

                      <SectionCard title="Invitation timing" description="Useful when the event is still in pre-start confirmation.">
                        <div className="space-y-3 text-sm text-[#6d6760]">
                          <div className="flex items-center justify-between gap-3">
                            <span>Invitation status</span>
                            <span className="font-semibold text-[#2d2a26]">
                              {formatStatusLabel(selectedEvent.invitation_status || 'not_available')}
                            </span>
                          </div>
                          <div className="flex items-center justify-between gap-3">
                            <span>Invitation expires</span>
                            <span className="font-semibold text-[#2d2a26]">
                              {formatWorkflowDate(selectedEvent.invitation_expires_at, 'No expiry')}
                            </span>
                          </div>
                        </div>
                      </SectionCard>
                    </div>
                  </div>
                ) : null}

                {activeTab === 'leaderboard' ? (
                  <SectionCard title="Leaderboard" description="Real-time ranking context for the selected live event.">
                    {isLoadingLeaderboard ? (
                      <p className="text-sm text-[#6d6760]">Loading leaderboard...</p>
                    ) : leaderboard?.entries?.length ? (
                      <div className="space-y-3">
                        {leaderboard.entries.map((entry) => (
                          <div key={`${entry.researcher_id}-${entry.rank}`} className="grid gap-3 rounded-[20px] border border-[#e6ddd4] bg-[#fcfaf7] p-4 md:grid-cols-[90px_minmax(0,1fr)_120px_120px] md:items-center">
                            <div className="text-sm font-semibold text-[#2d2a26]">#{entry.rank}</div>
                            <div>
                              <p className="text-sm font-semibold text-[#2d2a26]">{entry.researcher_name}</p>
                              <p className="text-xs text-[#8b8177]">{entry.valid_submissions_count} valid / {entry.submissions_count} linked</p>
                            </div>
                            <div className="text-sm font-semibold text-[#2d2a26]">{entry.score} pts</div>
                            <div className="text-sm font-semibold text-[#2d2a26]">
                              {formatWorkflowMoney(entry.prize_amount, 'TBD')}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <EmptyCollection
                        title="Leaderboard is empty"
                        description="The event has not accumulated ranked submissions yet."
                      />
                    )}
                  </SectionCard>
                ) : null}

                {activeTab === 'submissions' ? (
                  <div className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
                    <SectionCard title="Link an existing report" description="Attach a submitted vulnerability report to this live event so scoring can update.">
                      <div className="space-y-4">
                        <Select label="Eligible report" value={selectedReportId} onChange={(event) => setSelectedReportId(event.target.value)}>
                          <option value="">Select a report</option>
                          {(reports || []).map((report) => (
                            <option key={report.id} value={report.id}>
                              {report.report_number} - {report.title}
                            </option>
                          ))}
                        </Select>
                        <Button variant="danger" isLoading={pendingAction === 'link-report'} onClick={handleLinkReport}>
                          Link report to event
                        </Button>
                      </div>
                    </SectionCard>

                    <SectionCard title="Current submission position" description="Use this to understand event scoring pressure before linking another report.">
                      <div className="space-y-3 text-sm text-[#6d6760]">
                        <div className="flex items-center justify-between gap-3">
                          <span>Linked submissions</span>
                          <span className="font-semibold text-[#2d2a26]">{selectedEvent.participation.submissions_count}</span>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                          <span>Valid submissions</span>
                          <span className="font-semibold text-[#2d2a26]">{selectedEvent.participation.valid_submissions_count}</span>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                          <span>Current score</span>
                          <span className="font-semibold text-[#2d2a26]">{selectedEvent.my_score}</span>
                        </div>
                      </div>
                    </SectionCard>
                  </div>
                ) : null}
              </>
            ) : null}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
