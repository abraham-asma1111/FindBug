'use client';

import { 
  MessageSquare, Flag, FileText, TrendingUp, 
  Users, CheckCircle, Clock 
} from 'lucide-react';

interface Activity {
  id: number;
  type: string;
  title: string;
  content: string;
  priority?: string;
  is_pinned: boolean;
  created_at: string;
}

interface ActivityFeedProps {
  activities: Activity[];
}

export default function PTaaSActivityFeed({ activities }: ActivityFeedProps) {
  const activityIcons: Record<string, any> = {
    comment: MessageSquare,
    finding: Flag,
    deliverable: FileText,
    phase_change: TrendingUp,
    assignment: Users,
    status_change: CheckCircle,
    milestone: CheckCircle,
    update: MessageSquare,
  };

  const priorityColors: Record<string, string> = {
    high: 'border-l-red-500',
    medium: 'border-l-yellow-500',
    low: 'border-l-blue-500',
  };

  if (activities.length === 0) {
    return (
      <div className="rounded-xl border border-[#e6ddd4] bg-white p-6">
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-6">Recent Activity</h3>
        <div className="text-center py-12">
          <Clock className="mx-auto h-10 w-10 text-[#8b8177] mb-2" />
          <p className="text-sm text-[#6d6760]">No recent activity</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[#e6ddd4] bg-white p-6">
      <h3 className="text-lg font-semibold text-[#2d2a26] mb-6">Recent Activity</h3>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {activities.map((activity) => {
          const Icon = activityIcons[activity.type] || MessageSquare;
          const priorityColor = activity.priority 
            ? priorityColors[activity.priority.toLowerCase()] || 'border-l-[#e6ddd4]'
            : 'border-l-[#e6ddd4]';

          return (
            <div
              key={activity.id}
              className={`flex gap-3 p-4 rounded-lg bg-[#faf6f1] border-l-4 ${priorityColor} ${
                activity.is_pinned ? 'ring-2 ring-blue-200' : ''
              }`}
            >
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-white border border-[#e6ddd4] flex items-center justify-center">
                  <Icon className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-[#2d2a26]">
                    {activity.title}
                    {activity.is_pinned && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                        Pinned
                      </span>
                    )}
                  </h4>
                  <span className="text-xs text-[#8b8177] whitespace-nowrap">
                    {new Date(activity.created_at).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                
                <p className="text-sm text-[#6d6760] line-clamp-2">{activity.content}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
