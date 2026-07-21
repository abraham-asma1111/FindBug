"use client";

import { useState, useEffect } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/components/ui/Toast";
import { EventFindingSubmissionModal } from "@/components/researcher/events/EventFindingSubmissionModal";
import { LiveLeaderboard } from "@/components/researcher/events/LiveLeaderboard";
import { useRouter } from "next/navigation";

interface LiveEvent {
  id: string;
  name: string;
  description: string;
  status: "draft" | "scheduled" | "active" | "closed" | "archived";
  start_time: string;
  end_time: string;
  prize_pool: number | null;
  scope_description: string | null;
  target_assets: string | null;
  reward_policy: string | null;
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

interface ResearcherEventData {
  event: LiveEvent;
  participation: Participation;
  my_rank: number | null;
  my_score: number;
  time_remaining: number | null;
}

export default function ResearcherEventDetailPage({ params }: { params: { id: string } }) {
  const { showToast } = useToast();
  const { id } = params;
  const router = useRouter();
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  const { data, isLoading, refetch } = useApiQuery<ResearcherEventData>(
    `/live-events/researcher/my-events`,
    ["researcher-event", id]
  );

  const eventData = data?.find((e: any) => e.event.id === id);

  const respondMutation = useApiMutation(`/live-events/invitations/${eventData?.participation.id}/respond`, "POST", {
    onSuccess: () => {
      showToast("Response recorded successfully", "success");
      refetch();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to respond", "error");
    },
  });

  const handleAccept = () => {
    if (!eventData) return;
    respondMutation.mutate({ accept: true });
  };

  const handleDecline = () => {
    if (!eventData) return;
    if (confirm("Are you sure you want to decline this invitation?")) {
      respondMutation.mutate({ accept: false });
    }
  };

  // Update time remaining every minute
  useEffect(() => {
    if (!eventData?.event || eventData.event.status !== "active") return;

    const updateTime = () => {
      const now = new Date().getTime();
      const end = new Date(eventData.event.end_time).getTime();
      const diff = Math.floor((end - now) / 1000 / 60); // Minutes
      setTimeRemaining(diff > 0 ? diff : 0);
    };

    updateTime();
    const interval = setInterval(updateTime, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [eventData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!eventData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Event not found</p>
        <Button onClick={() => router.back()} className="mt-4">
          Go Back
        </Button>
      </div>
    );
  }

  const { event, participation, my_rank, my_score } = eventData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {event.name}
            </h1>
            <Badge className={event.status === "active" ? "bg-green-500" : "bg-gray-500"}>
              {event.status.toUpperCase()}
            </Badge>
          </div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {event.description}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {participation.status === "invited" && (
            <>
              <Button variant="secondary" onClick={handleDecline}>
                Decline
              </Button>
              <Button onClick={handleAccept}>
                Accept Invitation
              </Button>
            </>
          )}
          {participation.status === "active" && event.status === "active" && (
            <Button onClick={() => setShowSubmitModal(true)}>
              Submit Finding
            </Button>
          )}
        </div>
      </div>

      {/* Event Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Your Score</div>
          <div className="mt-1 text-2xl font-bold text-blue-600 dark:text-blue-400">
            {my_score}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Your Rank</div>
          <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {my_rank ? `#${my_rank}` : "-"}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Submissions</div>
          <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {participation.submissions_count}
            <span className="text-sm text-green-600 dark:text-green-400 ml-2">
              ({participation.valid_submissions_count} valid)
            </span>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {event.status === "active" ? "Time Remaining" : "Prize Pool"}
          </div>
          <div className="mt-1 text-2xl font-bold text-orange-600 dark:text-orange-400">
            {event.status === "active" && timeRemaining !== null
              ? `${Math.floor(timeRemaining / 60)}h ${timeRemaining % 60}m`
              : event.prize_pool
              ? `${event.prize_pool.toLocaleString()} ETB`
              : "N/A"}
          </div>
        </Card>
      </div>

      {/* Leaderboard */}
      {(participation.status === "active" || participation.status === "completed") && (
        <LiveLeaderboard eventId={id} />
      )}

      {/* Event Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {event.scope_description && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Scope Description
            </h3>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {event.scope_description}
            </p>
          </Card>
        )}
        {event.target_assets && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Target Assets
            </h3>
            <pre className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono text-sm">
              {event.target_assets}
            </pre>
          </Card>
        )}
      </div>

      {event.reward_policy && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Reward Policy
          </h3>
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
            {event.reward_policy}
          </p>
        </Card>
      )}

      {/* Submit Modal */}
      {showSubmitModal && (
        <EventFindingSubmissionModal
          eventId={id}
          onClose={() => setShowSubmitModal(false)}
          onSuccess={() => {
            setShowSubmitModal(false);
            refetch();
          }}
        />
      )}
    </div>
  );
}
