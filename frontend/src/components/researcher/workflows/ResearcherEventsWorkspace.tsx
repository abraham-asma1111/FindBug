"use client";

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import { Badge } from "@/components/ui/Badge";
import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";

interface LiveEvent {
  id: string;
  name: string;
  description: string;
  status: "draft" | "scheduled" | "active" | "closed" | "archived";
  start_time: string;
  end_time: string;
  prize_pool: number | null;
}

interface Participation {
  id: string;
  status: "invited" | "accepted" | "declined" | "active" | "completed";
  score: number;
  rank: number | null;
  submissions_count: number;
  valid_submissions_count: number;
  prize_amount: number | null;
}

interface ResearcherEvent {
  event: LiveEvent;
  participation: Participation;
  my_rank: number | null;
  my_score: number;
  time_remaining: number | null;
}

const statusColors = {
  invited: "bg-blue-500",
  accepted: "bg-green-500",
  declined: "bg-gray-500",
  active: "bg-green-600",
  completed: "bg-gray-600",
};

const eventStatusColors = {
  draft: "bg-gray-500",
  scheduled: "bg-blue-500",
  active: "bg-green-500",
  closed: "bg-yellow-500",
  archived: "bg-gray-400",
};

export default function ResearcherEventsWorkspace() {
  const router = useRouter();
  const [filter, setFilter] = useState<string>("all");

  const { data: events, isLoading } = useApiQuery<ResearcherEvent[]>(
    "/live-events/researcher/my-events",
    ["researcher-events"]
  );

  const handleEventClick = (eventId: string) => {
    router.push(`/researcher/events/${eventId}`);
  };

  const filteredEvents = events?.filter((re) => {
    if (filter === "all") return true;
    if (filter === "invited") return re.participation.status === "invited";
    if (filter === "active") return re.participation.status === "active";
    if (filter === "completed") return re.participation.status === "completed";
    return true;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Live Hacking Events
        </h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Participate in time-boxed competitive hacking events and win prizes
        </p>
      </div>

      <div className="flex gap-2">
        <Button
          variant={filter === "all" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setFilter("all")}
        >
          All Events
        </Button>
        <Button
          variant={filter === "invited" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setFilter("invited")}
        >
          Invitations
        </Button>
        <Button
          variant={filter === "active" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setFilter("active")}
        >
          Active
        </Button>
        <Button
          variant={filter === "completed" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setFilter("completed")}
        >
          Completed
        </Button>
      </div>

      {!filteredEvents || filteredEvents.length === 0 ? (
        <EmptyState
          title="No events available"
          description="You haven't been invited to any live hacking events yet. Check back later for opportunities to participate in competitive challenges."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((re) => {
            const { event, participation, my_rank, my_score, time_remaining } = re;

            return (
              <Card
                key={event.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => handleEventClick(event.id)}
              >
                <div className="p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      <Badge className={eventStatusColors[event.status]}>
                        {event.status.toUpperCase()}
                      </Badge>
                      <Badge className={statusColors[participation.status]}>
                        {participation.status.toUpperCase()}
                      </Badge>
                    </div>
                    {event.prize_pool && (
                      <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                        {event.prize_pool.toLocaleString()} ETB
                      </span>
                    )}
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {event.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {event.description}
                    </p>
                  </div>

                  {participation.status !== "invited" && participation.status !== "declined" && (
                    <div className="grid grid-cols-2 gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Score</div>
                        <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                          {my_score}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Rank</div>
                        <div className="text-lg font-bold text-gray-900 dark:text-white">
                          {my_rank ? `#${my_rank}` : "-"}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Submissions</div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {participation.submissions_count}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Valid</div>
                        <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                          {participation.valid_submissions_count}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-1">
                    {time_remaining !== null && time_remaining > 0 && (
                      <div className="text-sm text-orange-600 dark:text-orange-400 font-medium">
                        ⏱️ {Math.floor(time_remaining / 60)}h {time_remaining % 60}m remaining
                      </div>
                    )}
                    {participation.prize_amount && (
                      <div className="text-sm text-green-600 dark:text-green-400 font-semibold">
                        🏆 Prize: {participation.prize_amount.toLocaleString()} ETB
                      </div>
                    )}
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {event.status === "scheduled" && `Starts ${formatDistanceToNow(new Date(event.start_time), { addSuffix: true })}`}
                      {event.status === "active" && `Ends ${formatDistanceToNow(new Date(event.end_time), { addSuffix: true })}`}
                      {event.status === "closed" && `Ended ${formatDistanceToNow(new Date(event.end_time), { addSuffix: true })}`}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
