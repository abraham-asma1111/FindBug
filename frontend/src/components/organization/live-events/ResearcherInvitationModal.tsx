"use client";

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import Checkbox from "@/components/ui/Checkbox";
import { useToast } from "@/components/ui/Toast";

interface Researcher {
  id: string;
  user_id: string;
  username: string;
  reputation_score: number;
  total_reports: number;
}

interface ResearcherInvitationModalProps {
  eventId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function ResearcherInvitationModal({
  eventId,
  onClose,
  onSuccess,
}: ResearcherInvitationModalProps) {
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedResearchers, setSelectedResearchers] = useState<Set<string>>(new Set());
  const [expiresInDays, setExpiresInDays] = useState("7");

  // TODO: Replace with actual researchers endpoint
  const { data: researchers, isLoading } = useApiQuery<Researcher[]>(
    `/researchers?search=${searchQuery}`,
    ["researchers", searchQuery]
  );

  const inviteMutation = useApiMutation(`/live-events/${eventId}/invite`, "POST", {
    onSuccess: () => {
      showToast("Invitations sent successfully", "success");
      onSuccess();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to send invitations", "error");
    },
  });

  const handleToggleResearcher = (researcherId: string) => {
    const newSelected = new Set(selectedResearchers);
    if (newSelected.has(researcherId)) {
      newSelected.delete(researcherId);
    } else {
      newSelected.add(researcherId);
    }
    setSelectedResearchers(newSelected);
  };

  const handleSelectAll = () => {
    if (!researchers) return;
    if (selectedResearchers.size === researchers.length) {
      setSelectedResearchers(new Set());
    } else {
      setSelectedResearchers(new Set(researchers.map((r) => r.id)));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedResearchers.size === 0) {
      showToast("Please select at least one researcher", "error");
      return;
    }

    inviteMutation.mutate({
      researcher_ids: Array.from(selectedResearchers),
      expires_in_days: parseInt(expiresInDays),
    });
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Invite Researchers" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Researchers
          </label>
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by username or reputation..."
          />
        </div>

        {/* Expiry */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Invitation Expires In (Days)
          </label>
          <Input
            type="number"
            value={expiresInDays}
            onChange={(e) => setExpiresInDays(e.target.value)}
            min="1"
            max="30"
          />
        </div>

        {/* Researchers List */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Select Researchers ({selectedResearchers.size} selected)
            </label>
            {researchers && researchers.length > 0 && (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={handleSelectAll}
              >
                {selectedResearchers.size === researchers.length ? "Deselect All" : "Select All"}
              </Button>
            )}
          </div>

          <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
            ) : !researchers || researchers.length === 0 ? (
              <div className="text-center py-8 text-gray-600 dark:text-gray-400">
                No researchers found
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {researchers.map((researcher) => (
                  <label
                    key={researcher.id}
                    className="flex items-center gap-3 p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                  >
                    <Checkbox
                      checked={selectedResearchers.has(researcher.id)}
                      onChange={() => handleToggleResearcher(researcher.id)}
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {researcher.username}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Reputation: {researcher.reputation_score} • Reports: {researcher.total_reports}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={inviteMutation.isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={inviteMutation.isLoading || selectedResearchers.size === 0}>
            {inviteMutation.isLoading ? "Sending..." : `Invite ${selectedResearchers.size} Researchers`}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
