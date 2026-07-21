"use client";

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import { Badge } from "@/components/ui/Badge";
import { LiveEventCreateModal } from "@/components/organization/live-events/LiveEventCreateModal";
import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";

interface LiveEvent {
  id: string;
  name: string;
  description: string;
  status: "draft" | "scheduled" | "active" | "closed" | "archived";
  start_time: string;
  end_time: string;
  max_participants: number | null;
  prize_pool: number | null;
  created_at: string;
}

const statusColors = {
  draft: "bg-gray-500",
  scheduled: "bg-blue-500",
  active: "bg-green-500",
  closed: "bg-yellow-500",
  archived: "bg-gray-400",
};

const statusLabels = {
  draft: "Draft",
  scheduled: "Scheduled",
  active: "Active",
  closed: "Closed",
  archived: "Archived",
};

export default function LiveEventsPage() {
  const router = useRouter();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const { data: events, isLoading, refetch } = useApiQuery<LiveEvent[]>(
    `/live-events${statusFilter ? `?status_filter=${statusFilter}` : ""}`,
    ["live-events", statusFilter]
  );

  const handleEventClick = (eventId: string) => {
    router.push(`/organization/services/live-events/${eventId}`);
  };

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Live Hacking Events
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Organize time-boxed competitive hacking events with real-time leaderboards
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          Create Event
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={statusFilter === null ? "primary" : "secondary"}
          size="sm"
          onClick={() => setStatusFilter(null)}
        >
          All
        </Button>
        <Button
          variant={statusFilter === "scheduled" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setStatusFilter("scheduled")}
        >
          Scheduled
        </Button>
        <Button
          variant={statusFilter === "active" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setStatusFilter("active")}
        >
          Active
        </Button>
        <Button
          variant={statusFilter === "closed" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setStatusFilter("closed")}
        >
          Closed
        </Button>
      </div>

      {/* Events List */}
      {!events || events.length === 0 ? (
        <EmptyState
          title="No live events yet"
          description="Create your first live hacking event to engage researchers in competitive time-boxed challenges"
          action={{
            label: "Create Event",
            onClick: () => setShowCreateModal(true),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => (
            <Card
              key={event.id}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => handleEventClick(event.id)}
            >
              <div className="p-6 space-y-4">
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <Badge className={statusColors[event.status]}>
                    {statusLabels[event.status]}
                  </Badge>
                  {event.prize_pool && (
                    <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                      {event.prize_pool.toLocaleString()} ETB
                    </span>
                  )}
                </div>

                {/* Event Name */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {event.name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                    {event.description}
                  </p>
                </div>

                {/* Event Details */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Start:</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(event.start_time).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">End:</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(event.end_time).toLocaleDateString()}
                    </span>
                  </div>
                  {event.max_participants && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Max Participants:</span>
                      <span className="text-gray-900 dark:text-white">
                        {event.max_participants}
                      </span>
                    </div>
                  )}
                </div>

                {/* Created Time */}
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Created {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <LiveEventCreateModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
}
