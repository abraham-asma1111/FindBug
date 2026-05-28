'use client';

import Link from 'next/link';
import { aiRt, aiRtModelLabels, aiRtStatusColors } from './aiRedTeamingStyles';

interface AIRedTeamingEngagement {
  id: string;
  name: string;
  target_ai_system: string;
  model_type: string;
  status: string;
  start_date?: string;
  end_date?: string;
  total_findings?: number;
  critical_findings?: number;
  high_findings?: number;
  assigned_experts?: string[];
  created_at: string;
}

interface AIRedTeamingEngagementListProps {
  engagements: AIRedTeamingEngagement[];
  onUpdate: () => void;
}

export default function AIRedTeamingEngagementList({
  engagements,
}: AIRedTeamingEngagementListProps) {
  return (
    <div className={aiRt.grid}>
      {engagements.map((engagement) => (
        <div key={engagement.id} className={`${aiRt.card} ${aiRt.cardHover} flex flex-col`}>
          <div className="flex items-center justify-between gap-1">
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                aiRtStatusColors[engagement.status] || aiRtStatusColors.draft
              }`}
            >
              {engagement.status}
            </span>
            <span className={aiRt.label}>
              {aiRtModelLabels[engagement.model_type] || engagement.model_type}
            </span>
          </div>

          <h3 className={`${aiRt.title} mt-2`}>{engagement.name}</h3>
          <p className={`${aiRt.subtitle} mt-1`}>{engagement.target_ai_system}</p>

          {(engagement.total_findings ?? 0) > 0 ? (
            <div className={`${aiRt.divider} space-y-1`}>
              <div className="flex justify-between text-xs">
                <span className={aiRt.body}>Findings</span>
                <span className={aiRt.stat}>{engagement.total_findings}</span>
              </div>
              {(engagement.critical_findings ?? 0) > 0 ? (
                <div className="flex justify-between text-xs">
                  <span className={aiRt.body}>Critical</span>
                  <span className="font-semibold text-red-600 dark:text-red-300">{engagement.critical_findings}</span>
                </div>
              ) : null}
            </div>
          ) : null}

          {engagement.assigned_experts?.length ? (
            <p className={`${aiRt.body} mt-1`}>{engagement.assigned_experts.length} expert(s)</p>
          ) : null}

          <Link
            href={`/organization/ai-red-teaming/${engagement.id}`}
            className="mt-2 block w-full rounded-lg bg-[#2d2a26] px-3 py-1.5 text-center text-xs font-semibold text-white hover:bg-[#1f1c19] dark:bg-slate-600 dark:hover:bg-slate-500"
          >
            View engagement
          </Link>
        </div>
      ))}
    </div>
  );
}
