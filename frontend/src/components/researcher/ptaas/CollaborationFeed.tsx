'use client';

import { useApiQuery } from '@/hooks/useApiQuery';
import { 
  MessageSquare, Flag, CheckCircle, AlertCircle, 
  Clock, User, Pin, TrendingUp 
} from 'lucide-react';

interface CollaborationUpdate {
  id: string;
  update_type: string;
  title: string;
  content: string;
  priority: string;
  is_pinned: boolean;
  created_at: string;
  created_by?: string;
}

interface CollaborationFeedProps {
  engagementId: string;
}

const updateTypeConfig = {
  FINDING_SUBMITTED: { 
    label: 'Finding Submitted', 
    color: 'bg-blue-100 text-blue-700 border-blue-200', 
    icon: Flag 
  },
  FINDING_VALIDATED: { 
    label: 'Finding Validated', 
    color: 'bg-green-100 text-green-700 border-green-200', 
    icon: CheckCircle 
  },
  PHASE_COMPLETED: { 
    label: 'Phase Completed', 
    color: 'bg-purple-100 text-purple-700 border-purple-200', 
    icon: CheckCircle 
  },
  MILESTONE_REACHED: { 
    label: 'Milestone Reached', 
    color: 'bg-orange-100 text-orange-700 border-orange-200', 
    icon: TrendingUp 
  },
  COMMENT: { 
    label: 'Comment', 
    color: 'bg-gray-100 text-gray-700 border-gray-200', 
    icon: MessageSquare 
  },
  RETEST_REQUIRED: { 
    label: 'Retest Required', 
    color: 'bg-orange-100 text-orange-700 border-orange-200', 
    icon: AlertCircle 
  },
  GENERAL: { 
    label: 'Update', 
    color: 'bg-gray-100 text-gray-700 border-gray-200', 
    icon: MessageSquare 
  },
};

const priorityConfig = {
  HIGH: { color: 'text-red-600', label: 'High Priority' },
  MEDIUM: { color: 'text-orange-600', label: 'Medium Priority' },
  LOW: { color: 'text-blue-600', label: 'Low Priority' },
};

export default function CollaborationFeed({ engagementId }: CollaborationFeedProps) {
  const { data: updates, isLoading, error } = useApiQuery<CollaborationUpdate[]>({
    endpoint: `/ptaas/engagements/${engagementId}/collaboration`,
    queryKey: ['collaboration-feed', engagementId],
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-xl border border-[#e6ddd4] bg-white p-4 animate-pulse">
            <div className="h-16 bg-[#faf6f1] rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-900 mb-1">Failed to load activity feed</h4>
            <p className="text-sm text-red-700">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!updates || updates.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
          <MessageSquare className="h-8 w-8 text-[#8b8177]" />
        </div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">No activity yet</h3>
        <p className="text-sm text-[#6d6760]">
          Collaboration updates and activity will appear here
        </p>
      </div>
    );
  }

  // Separate pinned and regular updates
  const pinnedUpdates = updates.filter(u => u.is_pinned);
  const regularUpdates = updates.filter(u => !u.is_pinned);

  return (
    <div className="space-y-4">
      {/* Pinned Updates */}
      {pinnedUpdates.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-[#2d2a26] flex items-center gap-2">
            <Pin className="h-4 w-4 text-orange-600" />
            Pinned Updates
          </h4>
          {pinnedUpdates.map((update) => (
            <UpdateCard key={update.id} update={update} isPinned />
          ))}
        </div>
      )}

      {/* Regular Updates */}
      {regularUpdates.length > 0 && (
        <div className="space-y-3">
          {pinnedUpdates.length > 0 && (
            <h4 className="text-sm font-semibold text-[#2d2a26] mt-6">Recent Activity</h4>
          )}
          {regularUpdates.map((update) => (
            <UpdateCard key={update.id} update={update} />
          ))}
        </div>
      )}
    </div>
  );
}

function UpdateCard({ update, isPinned = false }: { update: CollaborationUpdate; isPinned?: boolean }) {
  const typeInfo = updateTypeConfig[update.update_type as keyof typeof updateTypeConfig] || updateTypeConfig.GENERAL;
  const TypeIcon = typeInfo.icon;
  const priorityInfo = priorityConfig[update.priority as keyof typeof priorityConfig];

  const timeAgo = getTimeAgo(update.created_at);

  return (
    <div className={`rounded-xl border bg-white p-4 transition-all hover:shadow-sm ${
      isPinned ? 'border-orange-300 bg-orange-50' : 'border-[#e6ddd4]'
    }`}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`rounded-lg p-2 border ${typeInfo.color}`}>
          <TypeIcon className="h-4 w-4" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h5 className="font-semibold text-[#2d2a26]">{update.title}</h5>
              {isPinned && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                  <Pin className="h-3 w-3" />
                  Pinned
                </span>
              )}
              {priorityInfo && update.priority !== 'LOW' && (
                <span className={`text-xs font-medium ${priorityInfo.color}`}>
                  {priorityInfo.label}
                </span>
              )}
            </div>
            <span className="text-xs text-[#8b8177] whitespace-nowrap">{timeAgo}</span>
          </div>

          <p className="text-sm text-[#2d2a26] mb-2 whitespace-pre-wrap">{update.content}</p>

          <div className="flex items-center gap-3 text-xs text-[#8b8177]">
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border ${typeInfo.color}`}>
              {typeInfo.label}
            </span>
            {update.created_by && (
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {update.created_by}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  });
}
