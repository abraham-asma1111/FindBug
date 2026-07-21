'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import { Plus, Calendar, Users, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import PTaaSEngagementCreateModal from './PTaaSEngagementCreateModal';

interface PTaaSEngagement {
  id: string;
  name: string;
  description: string;
  scope: string;
  methodology?: string;
  testing_methodology?: string;
  start_date: string;
  end_date: string;
  status: string;
  budget: number;
  assigned_researchers: number;
  findings_count: number;
  created_at: string;
}

const statusConfig = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  active: { label: 'Active', color: 'bg-blue-100 text-blue-700', icon: CheckCircle },
  in_progress: { label: 'In Progress', color: 'bg-yellow-100 text-yellow-700', icon: AlertCircle },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function PTaaSEngagementList() {
  const router = useRouter();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: engagements, isLoading, error, refetch } = useApiQuery<PTaaSEngagement[]>({
    endpoint: '/ptaas/engagements',
    queryKey: ['ptaas-engagements'],
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#ef2330] border-r-transparent"></div>
          <p className="mt-4 text-sm text-[#6d6760]">Loading engagements...</p>
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
            <h3 className="font-semibold text-red-900">Error loading engagements</h3>
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
          title="No PTaaS Engagements"
          description="Create your first penetration testing engagement to get started. Assign expert researchers and track findings in real-time."
          action={{
            label: 'Create Engagement',
            onClick: () => setIsCreateModalOpen(true),
            icon: Plus,
          }}
        />
        <PTaaSEngagementCreateModal
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
            <h2 className="text-2xl font-semibold text-[#2d2a26]">PTaaS Engagements</h2>
            <p className="mt-1 text-sm text-[#6d6760]">
              Manage penetration testing engagements and track progress
            </p>
          </div>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            icon={Plus}
          >
            Create Engagement
          </Button>
        </div>

        {/* Engagement Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {engagements.map((engagement) => {
            const normalizedStatus = engagement.status?.toLowerCase?.() || 'draft';
            const statusInfo =
              statusConfig[normalizedStatus as keyof typeof statusConfig] || statusConfig.draft;
            const StatusIcon = statusInfo.icon;
            const methodologyLabel = engagement.testing_methodology || engagement.methodology || 'Custom';
            const shortId = typeof engagement.id === 'string' ? engagement.id.slice(0, 8) : String(engagement.id);

            return (
              <div
                key={engagement.id}
                onClick={() => router.push(`/organization/services/ptaas/${engagement.id}`)}
                className="group cursor-pointer rounded-[24px] border border-[#e6ddd4] bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-[#cbdff0] hover:shadow-md dark:border-gray-700 dark:bg-[#111111] dark:hover:border-gray-600"
              >
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${statusInfo.color} dark:bg-gray-800 dark:text-gray-200`}
                  >
                    <StatusIcon className="h-3.5 w-3.5" />
                    {statusInfo.label}
                  </span>
                  <span className="text-xs font-medium text-[#8b8177] dark:text-gray-500">#{shortId}</span>
                </div>

                {/* Engagement Info */}
                <div className="mt-4 min-h-[88px]">
                  <h3 className="text-base font-semibold tracking-tight text-[#2d2a26] group-hover:text-[#0f4c81] dark:text-gray-100 dark:group-hover:text-blue-300">
                    {engagement.name}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#6d6760] dark:text-gray-400">
                    {engagement.description}
                  </p>
                </div>

                {/* Methodology Badge */}
                <div className="mt-3">
                  <span className="inline-flex items-center rounded-full border border-[#cbdff0] bg-[#edf7fe] px-3 py-1 text-xs font-semibold text-[#0f4c81] dark:border-gray-700 dark:bg-gray-800 dark:text-blue-300">
                    {methodologyLabel}
                  </span>
                </div>

                {/* Stats */}
                <div className="mt-5 grid grid-cols-2 gap-3 border-t border-[#e6ddd4] pt-4 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-[#8b8177] dark:text-gray-500" />
                    <div>
                      <p className="text-xs font-medium text-[#8b8177] dark:text-gray-500">Researchers</p>
                      <p className="text-sm font-semibold text-[#2d2a26] dark:text-gray-100">
                        {engagement.assigned_researchers || 0}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-[#8b8177] dark:text-gray-500" />
                    <div>
                      <p className="text-xs font-medium text-[#8b8177] dark:text-gray-500">Findings</p>
                      <p className="text-sm font-semibold text-[#2d2a26] dark:text-gray-100">
                        {engagement.findings_count || 0}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div className="mt-4 flex items-center gap-2 text-xs font-medium text-[#8b8177] dark:text-gray-500">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>
                    {new Date(engagement.start_date).toLocaleDateString()} - {new Date(engagement.end_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <PTaaSEngagementCreateModal
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
