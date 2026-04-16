'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import { Plus, Code, Users, AlertCircle, CheckCircle, Clock, FileCode } from 'lucide-react';
import CodeReviewEngagementCreateModal from './CodeReviewEngagementCreateModal';

interface CodeReviewEngagement {
  id: number;
  name: string;
  description: string;
  repository_url: string;
  branch: string;
  language: string;
  status: string;
  start_date: string;
  end_date: string;
  assigned_reviewer_id: number | null;
  findings_count: number;
  created_at: string;
}

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-gray-100 text-gray-700', icon: Clock },
  in_review: { label: 'In Review', color: 'bg-yellow-100 text-yellow-700', icon: Code },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function CodeReviewEngagementList() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: engagements, isLoading, error, refetch } = useApiQuery<CodeReviewEngagement[]>({
    endpoint: '/code-review/engagements',
    queryKey: ['code-review-engagements'],
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#10b981] border-r-transparent"></div>
          <p className="mt-4 text-sm text-[#6d6760]">Loading code reviews...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900">Error loading code reviews</h3>
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

  if (!engagements || engagements.length === 0) {
    return (
      <>
        <EmptyState
          title="No Code Review Engagements"
          description="Request expert security code reviews from experienced researchers. Get detailed analysis of your codebase for vulnerabilities."
          action={{
            label: 'Request Code Review',
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
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-[#2d2a26]">Code Review Engagements</h2>
            <p className="mt-1 text-sm text-[#6d6760]">
              Manage security code reviews and track findings
            </p>
          </div>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            icon={Plus}
          >
            Request Review
          </Button>
        </div>

        {/* Engagement Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {engagements.map((engagement) => {
            const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.pending;
            const StatusIcon = statusInfo.icon;

            return (
              <div
                key={engagement.id}
                className="group cursor-pointer rounded-2xl border border-[#e6ddd4] bg-white p-6 transition-all hover:border-[#10b981] hover:shadow-md"
              >
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
                    <StatusIcon className="h-3.5 w-3.5" />
                    {statusInfo.label}
                  </span>
                  <span className="text-xs text-[#8b8177]">#{engagement.id}</span>
                </div>

                {/* Engagement Info */}
                <div className="mt-4">
                  <h3 className="font-semibold text-[#2d2a26] group-hover:text-[#10b981]">
                    {engagement.name}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm text-[#6d6760]">
                    {engagement.description}
                  </p>
                </div>

                {/* Repository Info */}
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2">
                  <FileCode className="h-4 w-4 text-green-700" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-medium text-green-700">
                      {engagement.repository_url.split('/').pop()}
                    </p>
                    <p className="text-xs text-green-600">
                      {engagement.branch} • {engagement.language}
                    </p>
                  </div>
                </div>

                {/* Stats */}
                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[#e6ddd4] pt-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Reviewer</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {engagement.assigned_reviewer_id ? 'Assigned' : 'Pending'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Findings</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {engagement.findings_count || 0}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div className="mt-4 text-xs text-[#8b8177]">
                  Due: {new Date(engagement.end_date).toLocaleDateString()}
                </div>
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
    </>
  );
}
