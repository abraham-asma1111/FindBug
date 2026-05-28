"use client";

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import Tabs from "@/components/ui/Tabs";
import { useToast } from "@/components/ui/Toast";
import { LiveEventDashboard } from "@/components/organization/live-events/LiveEventDashboard";
import { ResearcherInvitationModal } from "@/components/organization/live-events/ResearcherInvitationModal";
import { useRouter } from "next/navigation";

interface LiveEvent {
  id: string;
  name: string;
  description: string;
  status: "draft" | "scheduled" | "active" | "closed" | "archived";
  start_time: string;
  end_time: string;
  max_participants: number | null;
  prize_pool: number | null;
  scope_description: string | null;
  target_assets: string | null;
  reward_policy: string | null;
  created_at: string;
}

const statusColors = {
  draft: "bg-gray-500",
  scheduled: "bg-blue-500",
  active: "bg-green-500",
  closed: "bg-yellow-500",
  archived: "bg-gray-400",
};

export default function LiveEventDetailPage({ params }: { params: { id: string } }) {
  const { showToast } = useToast();
  const { id } = params;
  const router = useRouter();
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");

  const { data: event, isLoading, refetch } = useApiQuery<LiveEvent>(
    `/live-events/${id}`,
    ["live-event", id]
  );

  const updateStatusMutation = useApiMutation(`/live-events/${id}/status`, "PATCH", {
    onSuccess: () => {
      showToast("Event status updated", "success");
      refetch();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to update status", "error");
    },
  });

  const startEventMutation = useApiMutation(`/live-events/${id}/start`, "POST", {
    onSuccess: () => {
      showToast("Event started successfully", "success");
      refetch();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to start event", "error");
    },
  });

  const closeEventMutation = useApiMutation(`/live-events/${id}/close`, "POST", {
    onSuccess: () => {
      showToast("Event closed successfully", "success");
      refetch();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to close event", "error");
    },
  });

  const distributePrizesMutation = useApiMutation(`/live-events/${id}/distribute-prizes`, "POST", {
    onSuccess: (data: any) => {
      showToast(data.message || "Prizes distributed successfully", "success");
      refetch();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to distribute prizes", "error");
    },
  });

  const handleSchedule = () => {
    updateStatusMutation.mutate({ status: "scheduled" });
  };

  const handleStart = () => {
    startEventMutation.mutate({});
  };

  const handleClose = () => {
    closeEventMutation.mutate({});
  };

  const handleDistributePrizes = () => {
    if (confirm("Are you sure you want to distribute prizes? This action cannot be undone.")) {
      distributePrizesMutation.mutate({});
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Event not found</p>
        <Button onClick={() => router.back()} className="mt-4">
          Go Back
        </Button>
      </div>
    );
  }

  const tabs = [
    { id: "dashboard", label: "Dashboard" },
    { id: "details", label: "Details" },
    { id: "participants", label: "Participants" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {event.name}
            </h1>
            <Badge className={statusColors[event.status]}>
              {event.status.toUpperCase()}
            </Badge>
          </div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {event.description}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {event.status === "draft" && (
            <>
              <Button variant="secondary" onClick={() => setShowInviteModal(true)}>
                Invite Researchers
              </Button>
              <Button onClick={handleSchedule}>
                Schedule Event
              </Button>
            </>
          )}
          {event.status === "scheduled" && (
            <>
              <Button variant="secondary" onClick={() => setShowInviteModal(true)}>
                Invite More
              </Button>
              <Button onClick={handleStart}>
                Start Event
              </Button>
            </>
          )}
          {event.status === "active" && (
            <Button onClick={handleClose} variant="danger">
              Close Event
            </Button>
          )}
          {event.status === "closed" && event.prize_pool && (
            <Button onClick={handleDistributePrizes}>
              Distribute Prizes
            </Button>
          )}
        </div>
      </div>

      {/* Event Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Start Time</div>
          <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
            {new Date(event.start_time).toLocaleString()}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">End Time</div>
          <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
            {new Date(event.end_time).toLocaleString()}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Prize Pool</div>
          <div className="mt-1 text-lg font-semibold text-green-600 dark:text-green-400">
            {event.prize_pool ? `${event.prize_pool.toLocaleString()} ETB` : "N/A"}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Max Participants</div>
          <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
            {event.max_participants || "Unlimited"}
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === "dashboard" && (
          <LiveEventDashboard eventId={id} />
        )}
        {activeTab === "details" && (
          <div className="space-y-6">
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
          </div>
        )}
        {activeTab === "participants" && (
          <Card className="p-6">
            <p className="text-gray-600 dark:text-gray-400">
              Participants list coming soon...
            </p>
          </Card>
        )}
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <ResearcherInvitationModal
          eventId={id}
          onClose={() => setShowInviteModal(false)}
          onSuccess={() => {
            setShowInviteModal(false);
            refetch();
          }}
        />
      )}
    </div>
  );
}
