'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import { Plus, Code, AlertCircle, CheckCircle, Clock, FileCode, UserPlus, FileText } from 'lucide-react';
import CodeReviewEngagementCreateModal from './CodeReviewEngagementCreateModal';
import CodeReviewAssignReviewerModal from './CodeReviewAssignReviewerModal';
import CodeReviewEngagementReportModal from './CodeReviewEngagementReportModal';
import CodeReviewEngagementReportModal from './CodeReviewEngagementReportModal';

interface CodeReviewEngagement {
  id: string;
  title: string;
  repository_url: string;
  review_type: string;
  status: string;
  reviewer_id?: string | null;
  assigned_reviewer_ids?: string[] | null;
  findings_count: number;
  report_submitted_at?: string | null;
  created_at: string;
}

function assignedReviewerCount(engagement: CodeReviewEngagement): number {
  if (engagement.assigned_reviewer_ids?.length) {
    return engagement.assigned_reviewer_ids.length;
  }
  return engagement.reviewer_id ? 1 : 0;
}

interface EngagementListResponse {
  engagements: CodeReviewEngagement[];
  total: number;
}

const statusConfig: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  pending: { label: 'Pending', color: 'bg-gray-100 text-gray-700', icon: Clock },
  matching: { label: 'Matching', color: 'bg-blue-100 text-blue-700', icon: Clock },
  assigned: { label: 'Assigned', color: 'bg-indigo-100 text-indigo-700', icon: UserPlus },
  in_progress: { label: 'In progress', color: 'bg-yellow-100 text-yellow-700', icon: Code },
  under_review: { label: 'Under review', color: 'bg-amber-100 text-amber-800', icon: Code },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

function formatReviewType(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function CodeReviewEngagementList() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [assignTarget, setAssignTarget] = useState<CodeReviewEngagement | null>(null);
  const [reportTarget, setReportTarget] = useState<CodeReviewEngagement | null>(null);

  const { data, isLoading, error, refetch } = useApiQuery<EngagementListResponse>(
    '/code-review/engagements'
  );

  const engagements = data?.engagements ?? [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#10b981] border-r-transparent" />
          <p className="mt-4 text-sm text-[#6d6760]">Loading code reviews...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="mt-0.5 h-5 w-5 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Error loading code reviews</h3>
            <p className="mt-1 text-sm text-red-700">{error.message}</p>
            <Button variant="outline" size="sm" onClick={() => refetch()} className="mt-3">
              Try again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!engagements.length) {
    return (
      <>
        <EmptyState
          title="No code review engagements"
          description="Request an expert white-box review. Assign a researcher, then track findings and the final report handoff."
          action={{
            label: 'Request code review',
            onClick: () => setIsCreateModalOpen(true),
            icon: Plus,
          }}
        />
        <CodeReviewEngagementCreateModal
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
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-[#2d2a26]">Code review engagements</h2>
            <p className="mt-1 text-sm text-[#6d6760]">
              White-box reviews with file-level findings and structured report delivery
            </p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)} icon={Plus}>
            Request review
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {engagements.map((engagement) => {
            const statusInfo = statusConfig[engagement.status] || statusConfig.pending;
            const StatusIcon = statusInfo.icon;
            const reviewerCount = assignedReviewerCount(engagement);
            const canAssign = reviewerCount === 0 && ['pending', 'matching'].includes(engagement.status);

            return (
              <div
                key={engagement.id}
                className="rounded-2xl border border-[#e6ddd4] bg-white p-6 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}
                  >
                    <StatusIcon className="h-3.5 w-3.5" />
                    {statusInfo.label}
                  </span>
                  <span className="text-xs text-[#8b8177]">{formatReviewType(engagement.review_type)}</span>
                </div>

                <div className="mt-4">
                  <h3 className="font-semibold text-[#2d2a26]">{engagement.title}</h3>
                </div>

                <div className="mt-3 flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2">
                  <FileCode className="h-4 w-4 shrink-0 text-green-700" />
                  <p className="truncate text-xs font-medium text-green-700">{engagement.repository_url}</p>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[#e6ddd4] pt-4 text-sm">
                  <div>
                    <p className="text-xs text-[#8b8177]">Reviewer</p>
                    <p className="font-semibold text-[#2d2a26]">
                      {reviewerCount > 0 ? `${reviewerCount} assigned` : 'Unassigned'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#8b8177]">Findings</p>
                    <p className="font-semibold text-[#2d2a26]">{engagement.findings_count}</p>
                  </div>
                </div>

                {engagement.report_submitted_at ? (
                  <p className="mt-3 text-xs text-green-700">
                    Report submitted {new Date(engagement.report_submitted_at).toLocaleDateString()}
                  </p>
                ) : null}

                {canAssign ? (
                  <Button
                    className="mt-4 w-full"
                    size="sm"
                    variant="outline"
                    icon={UserPlus}
                    onClick={() => setAssignTarget(engagement)}
                  >
                    Assign reviewers
                  </Button>
                ) : reviewerCount > 0 ? (
                  <Button
                    className="mt-4 w-full"
                    size="sm"
                    variant="outline"
                    icon={UserPlus}
                    onClick={() => setAssignTarget(engagement)}
                  >
                    Add more reviewers
                  </Button>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>

      <CodeReviewEngagementCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          setIsCreateModalOpen(false);
          refetch();
        }}
      />

      {assignTarget ? (
        <CodeReviewAssignReviewerModal
          isOpen={!!assignTarget}
          onClose={() => setAssignTarget(null)}
          engagementId={assignTarget.id}
          engagementTitle={assignTarget.title}
          onSuccess={() => {
            setAssignTarget(null);
            refetch();
          }}
        />
      ) : null}

      {reportTarget ? (
        <CodeReviewEngagementReportModal
          isOpen={!!reportTarget}
          onClose={() => {
            setReportTarget(null);
            refetch();
          }}
          engagement={reportTarget}
        />
      ) : null}
    </>
  );
}
