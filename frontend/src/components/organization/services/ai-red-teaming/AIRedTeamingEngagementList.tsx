'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/ui/EmptyState';
import { Plus, Shield, Users, AlertCircle, CheckCircle, Clock, Brain } from 'lucide-react';
import AIRedTeamingEngagementCreateModal from './AIRedTeamingEngagementCreateModal';

interface AIRedTeamingEngagement {
  id: number;
  name: string;
  description: string;
  target_ai_system: string;
  model_type: string;
  status: string;
  start_date: string;
  end_date: string;
  assigned_experts: number;
  reports_count: number;
  created_at: string;
}

const statusConfig = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  active: { label: 'Active', color: 'bg-purple-100 text-purple-700', icon: Shield },
  testing: { label: 'Testing', color: 'bg-yellow-100 text-yellow-700', icon: Brain },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

const modelTypeLabels: Record<string, string> = {
  llm: 'LLM',
  ml_model: 'ML Model',
  ai_agent: 'AI Agent',
  chatbot: 'Chatbot',
  recommendation_system: 'Recommendation',
  computer_vision: 'Computer Vision',
};

export default function AIRedTeamingEngagementList() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: engagements, isLoading, error, refetch } = useApiQuery<AIRedTeamingEngagement[]>({
    endpoint: '/ai-red-teaming/engagements',
    queryKey: ['ai-red-teaming-engagements'],
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#8b5cf6] border-r-transparent"></div>
          <p className="mt-4 text-sm text-[#6d6760]">Loading AI Red Teaming engagements...</p>
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
          title="No AI Red Teaming Engagements"
          description="Create your first AI security testing engagement to identify vulnerabilities in LLMs and AI systems. Test for prompt injection, jailbreaking, data leakage, and model manipulation."
          action={{
            label: 'Create Engagement',
            onClick: () => setIsCreateModalOpen(true),
            icon: Plus,
          }}
        />
        <AIRedTeamingEngagementCreateModal
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
            <h2 className="text-2xl font-semibold text-[#2d2a26]">AI Red Teaming Engagements</h2>
            <p className="mt-1 text-sm text-[#6d6760]">
              Manage AI security testing and track vulnerability reports
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
            const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.draft;
            const StatusIcon = statusInfo.icon;

            return (
              <div
                key={engagement.id}
                className="group cursor-pointer rounded-2xl border border-[#e6ddd4] bg-white p-6 transition-all hover:border-[#8b5cf6] hover:shadow-md"
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
                  <h3 className="font-semibold text-[#2d2a26] group-hover:text-[#8b5cf6]">
                    {engagement.name}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm text-[#6d6760]">
                    {engagement.description}
                  </p>
                </div>

                {/* AI System Info */}
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-purple-50 px-3 py-2">
                  <Brain className="h-4 w-4 text-purple-700" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-medium text-purple-700">
                      {engagement.target_ai_system}
                    </p>
                    <p className="text-xs text-purple-600">
                      {modelTypeLabels[engagement.model_type] || engagement.model_type}
                    </p>
                  </div>
                </div>

                {/* Stats */}
                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[#e6ddd4] pt-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Experts</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {engagement.assigned_experts || 0}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-[#8b8177]" />
                    <div>
                      <p className="text-xs text-[#8b8177]">Reports</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {engagement.reports_count || 0}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div className="mt-4 text-xs text-[#8b8177]">
                  {new Date(engagement.start_date).toLocaleDateString()} - {new Date(engagement.end_date).toLocaleDateString()}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <AIRedTeamingEngagementCreateModal
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
