"use client";

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";

interface Report {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

interface EventFindingSubmissionModalProps {
  eventId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function EventFindingSubmissionModal({
  eventId,
  onClose,
  onSuccess,
}: EventFindingSubmissionModalProps) {
  const { showToast } = useToast();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  // Get researcher's reports that aren't already linked to an event
  const { data: reports, isLoading } = useApiQuery<Report[]>(
    "/reports?status=triaged,accepted",
    ["researcher-reports"]
  );

  const submitMutation = useApiMutation(`/live-events/${eventId}/submit`, "POST", {
    onSuccess: () => {
      showToast("Finding submitted successfully! Your score will be updated.", "success");
      onSuccess();
    },
    onError: (error: any) => {
      showToast(error.message || "Failed to submit finding", "error");
    },
  });

  const handleSubmit = () => {
    if (!selectedReportId) {
      showToast("Please select a report to submit", "error");
      return;
    }

    submitMutation.mutate({ report_id: selectedReportId });
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Submit Finding to Event" size="lg">
      <div className="space-y-6">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Select a validated vulnerability report to submit to this event. Your score will be calculated based on severity and bonuses.
        </p>

        {/* Reports List */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Select Report
          </label>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          ) : !reports || reports.length === 0 ? (
            <div className="text-center py-8 text-gray-600 dark:text-gray-400">
              No validated reports available. Submit and get your reports triaged first.
            </div>
          ) : (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-96 overflow-y-auto">
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {reports.map((report) => (
                  <label
                    key={report.id}
                    className={`flex items-start gap-3 p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer ${
                      selectedReportId === report.id ? "bg-blue-50 dark:bg-blue-900/20" : ""
                    }`}
                  >
                    <input
                      type="radio"
                      name="report"
                      value={report.id}
                      checked={selectedReportId === report.id}
                      onChange={() => setSelectedReportId(report.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {report.title}
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-sm">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${
                            report.severity === "critical"
                              ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                              : report.severity === "high"
                              ? "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300"
                              : report.severity === "medium"
                              ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
                              : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                          }`}
                        >
                          {report.severity.toUpperCase()}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">
                          {report.status}
                        </span>
                        <span className="text-gray-500 dark:text-gray-500">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Scoring Info */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">
            Scoring System
          </h4>
          <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
            <li>• Critical: 100 points | High: 50 | Medium: 25 | Low: 10 | Info: 5</li>
            <li>• First Blood Bonus: +50% (first to find this severity)</li>
            <li>• Speed Bonus: +25% (submitted in first hour)</li>
            <li>• Uniqueness Bonus: +20% (unique vulnerability type)</li>
            <li>• Duplicates: 0 points</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={submitMutation.isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitMutation.isLoading || !selectedReportId}
          >
            {submitMutation.isLoading ? "Submitting..." : "Submit Finding"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
