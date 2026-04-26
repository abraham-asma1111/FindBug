'use client';

interface TimelineEvent {
  id: string;
  title: string;
  description?: string;
  timestamp: string;
  user?: string;
  type?: 'created' | 'updated' | 'approved' | 'rejected' | 'completed' | 'failed';
  metadata?: Record<string, any>;
}

interface TimelineProps {
  events: TimelineEvent[];
}

export default function Timeline({ events }: TimelineProps) {
  const getEventIcon = (type?: string) => {
    switch (type) {
      case 'created':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        );
      case 'approved':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'rejected':
      case 'failed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'completed':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'updated':
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getEventColor = (type?: string) => {
    switch (type) {
      case 'created':
        return 'bg-[#3B82F6] border-[#3B82F6]';
      case 'approved':
      case 'completed':
        return 'bg-[#10B981] border-[#10B981]';
      case 'rejected':
      case 'failed':
        return 'bg-[#EF4444] border-[#EF4444]';
      case 'updated':
      default:
        return 'bg-[#F59E0B] border-[#F59E0B]';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  if (events.length === 0) {
    return (
      <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
        <p className="text-[#94A3B8]">No activity yet</p>
      </div>
    );
  }

  return (
    <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
      <h3 className="text-base font-semibold text-[#F8FAFC] mb-4">Activity Timeline</h3>
      <div className="space-y-4">
        {events.map((event, index) => (
          <div key={event.id} className="flex gap-4">
            {/* Timeline Line */}
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full border-2 flex items-center justify-center text-white ${getEventColor(
                  event.type
                )}`}
              >
                {getEventIcon(event.type)}
              </div>
              {index < events.length - 1 && (
                <div className="w-0.5 h-full bg-[#334155] mt-2"></div>
              )}
            </div>

            {/* Event Content */}
            <div className="flex-1 pb-6">
              <div className="flex items-start justify-between mb-1">
                <h4 className="text-sm font-semibold text-[#F8FAFC]">{event.title}</h4>
                <span className="text-xs text-[#94A3B8]">
                  {formatTimestamp(event.timestamp)}
                </span>
              </div>
              {event.description && (
                <p className="text-sm text-[#94A3B8] mb-2">{event.description}</p>
              )}
              {event.user && (
                <p className="text-xs text-[#64748B]">
                  by <span className="text-[#94A3B8]">{event.user}</span>
                </p>
              )}
              {event.metadata && Object.keys(event.metadata).length > 0 && (
                <div className="mt-2 p-3 bg-[#0F172A] rounded border border-[#334155]">
                  {Object.entries(event.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                      <span className="text-[#64748B]">{key}:</span>
                      <span className="text-[#94A3B8]">{String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
