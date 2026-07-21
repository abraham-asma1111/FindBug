'use client';

import React from 'react';
import { CheckCircle, Clock, AlertCircle, XCircle, UserPlus, RefreshCw } from 'lucide-react';

interface TimelineEvent {
  id: string;
  status: string;
  timestamp: string;
  user: {
    name: string;
    role: string;
  };
  notes?: string;
}

interface PTaaSFindingTimelineProps {
  findingId: string;
  events: TimelineEvent[];
}

const statusConfig = {
  SUBMITTED: { icon: Clock, color: 'text-blue-500', bg: 'bg-blue-50', label: 'Submitted' },
  TRIAGED: { icon: CheckCircle, color: 'text-purple-500', bg: 'bg-purple-50', label: 'Triaged' },
  ACCEPTED: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50', label: 'Accepted' },
  IN_PROGRESS: { icon: RefreshCw, color: 'text-yellow-500', bg: 'bg-yellow-50', label: 'In Progress' },
  FIXED: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: 'Fixed' },
  RETEST: { icon: RefreshCw, color: 'text-blue-600', bg: 'bg-blue-100', label: 'Retest' },
  CLOSED: { icon: CheckCircle, color: 'text-gray-600', bg: 'bg-gray-100', label: 'Closed' },
  REJECTED: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-50', label: 'Rejected' },
  ASSIGNED: { icon: UserPlus, color: 'text-indigo-500', bg: 'bg-indigo-50', label: 'Assigned' },
};

export default function PTaaSFindingTimeline({ findingId, events }: PTaaSFindingTimelineProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
        Status History
      </h3>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-[#e6ddd4] dark:bg-[#3d3a36]" />

        {/* Timeline events */}
        <div className="space-y-6">
          {events.map((event, index) => {
            const config = statusConfig[event.status as keyof typeof statusConfig] || statusConfig.SUBMITTED;
            const Icon = config.icon;

            return (
              <div key={event.id} className="relative flex gap-4">
                {/* Icon */}
                <div className={`relative z-10 flex h-12 w-12 items-center justify-center rounded-full ${config.bg}`}>
                  <Icon className={`h-5 w-5 ${config.color}`} />
                </div>

                {/* Content */}
                <div className="flex-1 pt-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">
                        {config.label}
                      </p>
                      <p className="text-sm text-[#6b6662] dark:text-[#a39e9a]">
                        by {event.user.name} ({event.user.role})
                      </p>
                    </div>
                    <span className="text-sm text-[#6b6662] dark:text-[#a39e9a]">
                      {formatDate(event.timestamp)}
                    </span>
                  </div>

                  {event.notes && (
                    <div className="mt-2 rounded-lg bg-[#faf6f1] dark:bg-[#3d3a36] p-3">
                      <p className="text-sm text-[#2d2a26] dark:text-[#e6ddd4]">
                        {event.notes}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {events.length === 0 && (
        <div className="text-center py-8 text-[#6b6662] dark:text-[#a39e9a]">
          No status history available
        </div>
      )}
    </div>
  );
}
