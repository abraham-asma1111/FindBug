'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useRouter } from 'next/navigation';
import { Calendar, Users, Target, Clock, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

interface PTaaSEngagement {
  id: string;
  name: string;
  description: string;
  status: string;
  testing_methodology: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  team_size: number;
  assigned_researchers: string[];
  pricing_model: string;
  base_price: number;
  organization_id: string;
  created_at: string;
}

const statusConfig = {
  DRAFT: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  IN_PROGRESS: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
  COMPLETED: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  CANCELLED: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function ResearcherPTaaSEngagementList() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const { data: engagements, isLoading, error } = useApiQuery<PTaaSEngagement[]>({
    endpoint: statusFilter === 'all' 
      ? '/ptaas/researcher/engagements'
      : `/ptaas/researcher/engagements?status=${statusFilter}`,
    queryKey: ['researcher-ptaas-engagements', statusFilter]
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-2xl border border-[#e6ddd4] bg-white p-6 animate-pulse">
            <div className="h-32 bg-[#faf6f1] rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Failed to load engagements</h3>
            <p className="text-sm text-red-700">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const engagementsList = engagements || [];
  
  // Count engagements by status
  const statusCounts = {
    all: engagementsList.length,
    DRAFT: engagementsList.filter(e => e.status === 'DRAFT').length,
    IN_PROGRESS: engagementsList.filter(e => e.status === 'IN_PROGRESS').length,
    COMPLETED: engagementsList.filter(e => e.status === 'COMPLETED').length,
  };

  return (
    <div className="space-y-6">
      {/* Filter Tabs - Always show */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            statusFilter === 'all'
              ? 'bg-[#2d2a26] text-white'
              : 'bg-white border border-[#e6ddd4] text-[#6d6760] hover:bg-[#faf6f1]'
          }`}
        >
          All ({statusCounts.all})
        </button>
        {['DRAFT', 'IN_PROGRESS', 'COMPLETED'].map((status) => {
          const count = statusCounts[status as keyof typeof statusCounts];
          const label = status.replace('_', ' ');
          return (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-[#2d2a26] text-white'
                  : 'bg-white border border-[#e6ddd4] text-[#6d6760] hover:bg-[#faf6f1]'
              }`}
            >
              {label} ({count})
            </button>
          );
        })}
      </div>

      {/* Engagement Cards or Empty State */}
      {engagementsList.length === 0 ? (
        <div className="rounded-2xl border border-[#e6ddd4] bg-white p-12">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
              <Target className="h-8 w-8 text-[#8b8177]" />
            </div>
            <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">
              No PTaaS Engagements Yet
            </h3>
            <p className="text-sm text-[#6d6760] max-w-md mx-auto">
              You'll see penetration testing engagements here when organizations invite you to their security testing programs.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {engagementsList.map((engagement) => {
            const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.DRAFT;
            const StatusIcon = statusInfo.icon;
            
            return (
              <button
                key={engagement.id}
                onClick={() => router.push(`/researcher/programs/ptaas/${engagement.id}`)}
                className="w-full rounded-2xl border border-[#e6ddd4] bg-white p-6 hover:shadow-lg transition-all text-left"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">
                      {engagement.name}
                    </h3>
                    <p className="text-sm text-[#6d6760] line-clamp-2">
                      {engagement.description}
                    </p>
                  </div>
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color} ml-4 flex-shrink-0`}>
                    <StatusIcon className="h-3.5 w-3.5" />
                    {statusInfo.label}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-[#e6ddd4]">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-blue-50 p-2">
                      <Target className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177]">Methodology</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">{engagement.testing_methodology}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-green-50 p-2">
                      <Users className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177]">Team Size</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">{engagement.team_size}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-purple-50 p-2">
                      <Calendar className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177]">Duration</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">{engagement.duration_days} days</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-orange-50 p-2">
                      <Calendar className="h-4 w-4 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-xs text-[#8b8177]">Start Date</p>
                      <p className="text-sm font-semibold text-[#2d2a26]">
                        {new Date(engagement.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </p>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
