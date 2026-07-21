'use client';

import { AlertCircle, CheckCircle, XCircle, MessageSquare, Clock } from 'lucide-react';

interface TriageFeedback {
  validated?: boolean;
  retest_required?: boolean;
  retest_notes?: string;
  triage_notes?: string;
  status?: string;
}

interface TriageFeedbackPanelProps {
  feedback: TriageFeedback;
}

export default function TriageFeedbackPanel({ feedback }: TriageFeedbackPanelProps) {
  // If no triage feedback yet
  if (!feedback.triage_notes && feedback.status === 'SUBMITTED') {
    return (
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div className="flex gap-3">
          <Clock className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Pending Triage</h4>
            <p className="text-sm text-blue-700">
              Your finding is awaiting review by our security triage team. You'll be notified once it's been validated.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // If triaged but not validated
  if (feedback.status === 'TRIAGED' && !feedback.validated) {
    return (
      <div className="space-y-4">
        <div className="rounded-xl border border-purple-200 bg-purple-50 p-4">
          <div className="flex gap-3">
            <MessageSquare className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-purple-900 mb-1">Triaged - Under Review</h4>
              <p className="text-sm text-purple-700">
                Your finding has been triaged and is currently under detailed review.
              </p>
            </div>
          </div>
        </div>

        {feedback.triage_notes && (
          <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
            <h5 className="text-sm font-semibold text-[#2d2a26] mb-2">Triage Notes</h5>
            <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{feedback.triage_notes}</p>
          </div>
        )}
      </div>
    );
  }

  // If validated
  if (feedback.validated) {
    return (
      <div className="space-y-4">
        <div className="rounded-xl border border-green-200 bg-green-50 p-4">
          <div className="flex gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-green-900 mb-1">Validated ✓</h4>
              <p className="text-sm text-green-700">
                Great work! Your finding has been validated by our security team and will be forwarded to the client.
              </p>
            </div>
          </div>
        </div>

        {feedback.triage_notes && (
          <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
            <h5 className="text-sm font-semibold text-[#2d2a26] mb-2 flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Validation Notes
            </h5>
            <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{feedback.triage_notes}</p>
          </div>
        )}

        {feedback.retest_required && (
          <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h5 className="font-semibold text-orange-900 mb-1">Retest Required</h5>
                <p className="text-sm text-orange-700 mb-2">
                  The client has implemented a fix. Please verify that the vulnerability has been properly remediated.
                </p>
                {feedback.retest_notes && (
                  <div className="mt-3 p-3 rounded-lg bg-white border border-orange-200">
                    <p className="text-sm text-orange-900 whitespace-pre-wrap">{feedback.retest_notes}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // If rejected
  if (feedback.status === 'REJECTED') {
    return (
      <div className="space-y-4">
        <div className="rounded-xl border border-red-200 bg-red-50 p-4">
          <div className="flex gap-3">
            <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-red-900 mb-1">Not Accepted</h4>
              <p className="text-sm text-red-700">
                This finding was not accepted. Please review the feedback below and consider submitting a new finding if you believe there's a valid security issue.
              </p>
            </div>
          </div>
        </div>

        {feedback.triage_notes && (
          <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
            <h5 className="text-sm font-semibold text-[#2d2a26] mb-2">Rejection Reason</h5>
            <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{feedback.triage_notes}</p>
          </div>
        )}
      </div>
    );
  }

  // Default - show any available notes
  if (feedback.triage_notes) {
    return (
      <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
        <h5 className="text-sm font-semibold text-[#2d2a26] mb-2 flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          Triage Feedback
        </h5>
        <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{feedback.triage_notes}</p>
      </div>
    );
  }

  return null;
}
