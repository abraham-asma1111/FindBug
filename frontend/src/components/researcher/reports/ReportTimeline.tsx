'use client';

import { useApiQuery } from '@/hooks/useApiQuery';
import Spinner from '@/components/ui/Spinner';

interface TimelineEvent {
  id: string;
  event_type: string;
  description: string;
  created_at: string;
  user?: {
    username: string;
    role: string;
  };
  metadata?: Record<string, any>;
}

interface ReportTimelineProps {
  reportId: string;
}

export default function ReportTimeline({ reportId }: ReportTimelineProps) {
  const { data: activityData, isLoading } = useApiQuery<{ activities: TimelineEvent[]; total: number }>(
    `/reports/${reportId}/activity`,
    { enabled: !!reportId }
  );

  const activities = activityData?.activities || [];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType?.toLowerCase()) {
      case 'submitted':
      case 'created':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        );
      case 'acknowledged':
      case 'triaged':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'accepted':
      case 'approved':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'rejected':
      case 'closed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'comment':
      case 'commented':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case 'updated':
      case 'modified':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        );
      case 'resolved':
      case 'fixed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType?.toLowerCase()) {
      case 'submitted':
      case 'created':
        return 'bg-[#3b82f6] text-white';
      case 'acknowledged':
      case 'triaged':
        return 'bg-[#8b5cf6] text-white';
      case 'accepted':
      case 'approved':
        return 'bg-[#10b981] text-white';
      case 'rejected':
      case 'closed':
        return 'bg-[#ef4444] text-white';
      case 'resolved':
      case 'fixed':
        return 'bg-[#059669] text-white';
      case 'comment':
      case 'commented':
        return 'bg-[#f59e0b] text-white';
      case 'updated':
      case 'modified':
        return 'bg-[#6366f1] text-white';
      default:
        return 'bg-[#6b7280] text-white';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner size="md" />
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="rounded-2xl bg-[#faf6f1] p-8 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
          No activity yet
        </p>
        <p className="mt-2 text-sm text-[#6d6760]">
          Activity history will appear here as the report progresses.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div key={activity.id} className="flex gap-4">
          {/* Timeline Line */}
          <div className="flex flex-col items-center">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-full ${getEventColor(
                activity.event_type
              )}`}
            >
              {getEventIcon(activity.event_type)}
            </div>
            {index < activities.length - 1 && (
              <div className="w-0.5 flex-1 bg-[#e6ddd4] min-h-[40px]" />
            )}
          </div>

          {/* Event Content */}
          <div className="flex-1 pb-8">
            <div className="rounded-2xl bg-[#faf6f1] p-5">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="text-sm font-semibold text-[#2d2a26] capitalize">
                    {activity.event_type.replace('_', ' ')}
                  </p>
                  {activity.user && (
                    <p className="text-xs text-[#6d6760] mt-1">
                      by {activity.user.username} ({activity.user.role.replace('_', ' ')})
                    </p>
                  )}
                </div>
                <span className="text-xs text-[#8b8177] whitespace-nowrap">
                  {formatDate(activity.created_at)}
                </span>
              </div>
              <p className="text-sm text-[#2d2a26] leading-relaxed">
                {activity.description}
              </p>
              {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#e6ddd4]">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Details
                  </p>
                  <div className="space-y-1">
                    {Object.entries(activity.metadata).map(([key, value]) => (
                      <p key={key} className="text-xs text-[#6d6760]">
                        <span className="font-medium">{key.replace('_', ' ')}:</span>{' '}
                        {String(value)}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
