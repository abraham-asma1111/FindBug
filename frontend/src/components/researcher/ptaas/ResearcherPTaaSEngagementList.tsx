'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useRouter } from 'next/navigation';
import { Calendar, Target, AlertCircle, CheckCircle, Clock, TrendingUp, Eye } from 'lucide-react';
import Button from '@/components/ui/Button';

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
      <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-[#faf6f1] rounded"></div>
          <div className="h-64 bg-[#faf6f1] rounded"></div>
        </div>
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-[#2d2a26]">PTaaS Engagements</h2>
          <p className="mt-1 text-sm text-[#6d6760]">
            View and manage your assigned penetration testing engagements
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
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

      {/* Table or Empty State */}
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
        <div className="rounded-2xl border border-[#e6ddd4] bg-white overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#faf6f1] border-b border-[#e6ddd4]">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Engagement
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Methodology
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Timeline
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Team Size
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-[#2d2a26] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e6ddd4]">
                {engagementsList.map((engagement) => {
                  const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.DRAFT;
                  const StatusIcon = statusInfo.icon;
                  
                  return (
                    <tr 
                      key={engagement.id}
                      className="hover:bg-[#faf6f1] transition-colors cursor-pointer"
                      onClick={() => router.push(`/researcher/programs/ptaas/${engagement.id}`)}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-start gap-3">
                          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold flex-shrink-0">
                            {engagement.name.charAt(0).toUpperCase()}
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-semibold text-[#2d2a26] truncate">
                              {engagement.name}
                            </p>
                            <p className="text-sm text-[#6d6760] line-clamp-1 mt-0.5">
                              {engagement.description}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
                          <StatusIcon className="h-3.5 w-3.5" />
                          {statusInfo.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-[#8b8177]" />
                          <span className="text-sm text-[#2d2a26]">{engagement.testing_methodology}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-[#8b8177]" />
                          <div className="text-sm">
                            <p className="text-[#2d2a26] font-medium">{engagement.duration_days} days</p>
                            <p className="text-[#8b8177] text-xs">
                              {new Date(engagement.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="flex -space-x-2">
                            {Array.from({ length: Math.min(engagement.team_size, 3) }).map((_, i) => (
                              <div
                                key={i}
                                className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 border-2 border-white flex items-center justify-center text-white text-xs font-semibold"
                              >
                                {i + 1}
                              </div>
                            ))}
                            {engagement.team_size > 3 && (
                              <div className="w-8 h-8 rounded-full bg-[#e6ddd4] border-2 border-white flex items-center justify-center text-[#6d6760] text-xs font-semibold">
                                +{engagement.team_size - 3}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/researcher/programs/ptaas/${engagement.id}`);
                          }}
                          icon={Eye}
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
