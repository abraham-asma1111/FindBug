'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import { Plus, Calendar, Users, Trophy, Clock, Play, CheckCircle, XCircle } from 'lucide-react';
import LiveEventCreateModal from './LiveEventCreateModal';

interface LiveEvent {
  id: number;
  name: string;
  description: string;
  start_time: string;
  end_time: string;
  status: string;
  max_participants: number;
  current_participants: number;
  prize_pool: number;
  scope_description: string;
  created_at: string;
}

const statusConfig = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  scheduled: { label: 'Scheduled', color: 'bg-blue-100 text-blue-700', icon: Calendar },
  active: { label: 'Live', color: 'bg-orange-100 text-orange-700', icon: Play },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: XCircle },
};

export default function LiveEventsList() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: events, isLoading, error, refetch } = useApiQuery<LiveEvent[]>({
    endpoint: '/live-events',
    queryKey: ['live-events'],
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#f59e0b] border-r-transparent"></div>
          <p className="mt-4 text-sm text-[#6d6760]">Loading events...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900">Error loading events</h3>
            <p className="mt-1 text-sm text-red-700">{error.message}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="mt-3"
            >
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <>
        <EmptyState
          title="No Live Events"
          description="Create your first live hacking event to engage researchers in real-time competitive security testing with instant validation and rewards."
          action={{
            label: 'Create Event',
            onClick: () => setIsCreateModalOpen(true),
            icon: Plus,
          }}
        />
        <LiveEventCreateModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSuccess={() => {
            setIsCreateModalOpen(false);
            refetch();
          }}
        />
      </>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-[#2d2a26]">Live Hacking Events</h2>
            <p className="mt-1 text-sm text-[#6d6760]">
              Manage live events and track real-time participation
            </p>
          </div>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            icon={Plus}
          >
            Create Event
          </Button>
        </div>

        {/* Event Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {events.map((event) => {
            const statusInfo = statusConfig[event.status as keyof typeof statusConfig] || statusConfig.draft;
            const StatusIcon = statusInfo.icon;
            const isLive = event.status === 'active';

            return (
              <div
                key={event.id}
                className={`group cursor-pointer rounded-2xl border bg-white p-6 transition-all hover:shadow-md ${
                  isLive 
                    ? 'border-[#f59e0b] ring-2 ring-[#f59e0b]/20' 
                    : 'border-[#e6ddd4] hover:border-[#f59e0b]'
                }`}
              >
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
                    <StatusIcon className="h-3.5 w-3.5" />
                    {statusInfo.label}
                  </span>
                  <span className="text-xs text-[#8b8177]">#{event.id}</span>
                </div>

                {/* Event Info */}
                <div className="mt-4">
                  <h3 className="font-semibold text-[#2d2a26] group-hover:text-[#f59e0b]">
                    {event.name}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm text-[#6d6760]">
                    {event.description}
                  </p>
                </div>

                {/* Prize Pool */}
                {event.prize_pool > 0 && (
                  <div className="mt-3 flex items-center gap-2 rounded-lg bg-orange-50 px-3 py-2">
                    <Trophy className="h-4 w-4 text-orange-700" />
                    <div>
                      <p className="text-xs text-orange-600">Prize Pool</p>
                      <p className="text-sm font-semibold text-orange-700">
                        {event.prize_pool.toLocaleString()} ETB
                      </p>
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[#e6ddd4] pt-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Participants</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {event.current_participants || 0}/{event.max_participants}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Duration</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {Math.ceil((new Date(event.end_time).getTime() - new Date(event.start_time).getTime()) / (1000 * 60 * 60))}h
                      </p>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div className="mt-4 flex items-center gap-2 text-xs text-[#8b8177]">
                  <Clock className="h-3.5 w-3.5" />
                  <span>
                    {new Date(event.start_time).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>

                {/* Live Indicator */}
                {isLive && (
                  <div className="mt-3 flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-orange-400 opacity-75"></span>
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-orange-500"></span>
                    </span>
                    <span className="text-xs font-medium text-orange-700">Event is live now!</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <LiveEventCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          setIsCreateModalOpen(false);
          refetch();
        }}
      />
    </>
  );
}
