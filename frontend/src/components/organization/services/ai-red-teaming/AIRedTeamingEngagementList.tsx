'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, Brain, Users, AlertCircle, CheckCircle, Clock, Shield } from 'lucide-react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import AIRedTeamingEngagementCreateModal from '@/components/organization/ai-red-teaming/AIRedTeamingEngagementCreateModal';
import { aiRt, aiRtModelLabels, aiRtStatusColors } from '@/components/organization/ai-red-teaming/aiRedTeamingStyles';

interface AIRedTeamingEngagement {
  id: string;
  name: string;
  target_ai_system: string;
  model_type: string;
  status: string;
  total_findings?: number;
  assigned_experts?: string[] | null;
  start_date?: string | null;
  end_date?: string | null;
}

const statusIcons: Record<string, typeof Clock> = {
  draft: Clock,
  active: Shield,
  testing: Brain,
  completed: CheckCircle,
  cancelled: AlertCircle,
};

export default function AIRedTeamingEngagementList() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: engagements, isLoading, error, refetch } = useApiQuery<AIRedTeamingEngagement[]>(
    '/ai-red-teaming/engagements',
    { enabled: true }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="inline-block h-7 w-7 animate-spin rounded-full border-4 border-violet-500 border-r-transparent" />
        <p className="ml-3 text-xs text-[#6d6760] dark:text-slate-400">Loading engagements...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-300 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950/40">
        <p className="text-sm font-medium text-red-800 dark:text-red-200">{error.message}</p>
        <Button variant="outline" size="sm" className="mt-2" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!engagements?.length) {
    return (
      <>
        <EmptyState
          title="No AI Red Teaming engagements"
          description="Create an engagement, set up the sandbox, publish to researchers, and review AI vulnerability reports."
          action={{
            label: 'Create engagement',
            onClick: () => setIsCreateModalOpen(true),
            icon: Plus,
          }}
        />
        {isCreateModalOpen ? (
          <AIRedTeamingEngagementCreateModal
            onClose={() => setIsCreateModalOpen(false)}
            onSuccess={() => {
              setIsCreateModalOpen(false);
              refetch();
            }}
          />
        ) : null}
      </>
    );
  }

  return (
    <>
      <div className={aiRt.page}>
        <div className="flex items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-semibold text-[#2d2a26] dark:text-slate-100">AI Red Teaming</h2>
            <p className="text-xs text-[#6d6760] dark:text-slate-400">
              Prompt injection, jailbreaks, and model safety testing
            </p>
          </div>
          <Button size="sm" onClick={() => setIsCreateModalOpen(true)} icon={Plus}>
            Create
          </Button>
        </div>

        <div className={aiRt.grid}>
          {engagements.map((engagement) => {
            const StatusIcon = statusIcons[engagement.status] || Clock;
            const statusClass = aiRtStatusColors[engagement.status] || aiRtStatusColors.draft;
            const experts = engagement.assigned_experts?.length ?? 0;

            return (
              <div key={engagement.id} className={`${aiRt.card} ${aiRt.cardHover} flex flex-col`}>
                <div className="flex items-center justify-between gap-1">
                  <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${statusClass}`}>
                    <StatusIcon className="h-3 w-3" />
                    {engagement.status}
                  </span>
                  <span className={aiRt.label}>{aiRtModelLabels[engagement.model_type] || engagement.model_type}</span>
                </div>

                <h3 className={`${aiRt.title} mt-2`}>{engagement.name}</h3>
                <p className={`${aiRt.subtitle} mt-1`}>{engagement.target_ai_system}</p>

                <div className={`${aiRt.accentBox} mt-2`}>
                  <p className={`${aiRt.accentText} truncate`}>{engagement.target_ai_system}</p>
                </div>

                <div className={`${aiRt.divider} grid grid-cols-2 gap-2`}>
                  <div>
                    <p className={aiRt.label}>Experts</p>
                    <p className={aiRt.stat}>{experts}</p>
                  </div>
                  <div>
                    <p className={aiRt.label}>Findings</p>
                    <p className={aiRt.stat}>{engagement.total_findings ?? 0}</p>
                  </div>
                </div>

                <Link
                  href={`/organization/ai-red-teaming/${engagement.id}`}
                  className="mt-2 block w-full rounded-lg bg-violet-600 px-3 py-1.5 text-center text-xs font-semibold text-white hover:bg-violet-700 dark:bg-violet-700 dark:hover:bg-violet-600"
                >
                  Manage
                </Link>
              </div>
            );
          })}
        </div>
      </div>

      {isCreateModalOpen ? (
        <AIRedTeamingEngagementCreateModal
          onClose={() => setIsCreateModalOpen(false)}
          onSuccess={() => {
            setIsCreateModalOpen(false);
            refetch();
          }}
        />
      ) : null}
    </>
  );
}
