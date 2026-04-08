'use client';

import { useState } from 'react';
import Link from 'next/link';
import Card from '@/components/ui/Card';

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

const statusColors: Record<string, string> = {
  draft: 'bg-[#f3ede6] text-[#5f5851]',
  pending: 'bg-[#faf1e1] text-[#9a6412]',
  active: 'bg-[#eef5fb] text-[#2d78a8]',
  completed: 'bg-[#eef7ef] text-[#24613a]',
  archived: 'bg-[#f3ede6] text-[#8b8177]',
};

const modelTypeLabels: Record<string, string> = {
  llm: 'LLM',
  ml_model: 'ML Model',
  ai_agent: 'AI Agent',
  chatbot: 'Chatbot',
  recommendation_system: 'Recommendation System',
  computer_vision: 'Computer Vision',
};

export default function AIRedTeamingEngagementList({
  engagements,
  onUpdate,
}: AIRedTeamingEngagementListProps) {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {engagements.map((engagement) => (
        <Card
          key={engagement.id}
          className="group relative flex flex-col p-6 transition-all hover:shadow-md"
        >
          {/* Status Badge */}
          <div className="mb-4 flex items-center justify-between">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                statusColors[engagement.status] || statusColors.draft
              }`}
            >
              {engagement.status}
            </span>
            <span className="text-xs text-[#8b8177] dark:text-slate-400">
              {modelTypeLabels[engagement.model_type] || engagement.model_type}
            </span>
          </div>

          {/* Engagement Name */}
          <h3 className="mb-2 text-lg font-bold text-[#2d2a26] dark:text-slate-100 line-clamp-2">
            {engagement.name}
          </h3>

          {/* Target System */}
          <p className="mb-4 text-sm text-[#6d6760] dark:text-slate-400 line-clamp-2">
            {engagement.target_ai_system}
          </p>

          {/* Findings Summary */}
          {engagement.total_findings !== undefined && engagement.total_findings > 0 && (
            <div className="mb-4 space-y-2 border-t border-[#e6ddd4] dark:border-gray-700 pt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#6d6760] dark:text-slate-400">Total Findings</span>
                <span className="font-bold text-[#2d2a26] dark:text-slate-100">
                  {engagement.total_findings}
                </span>
              </div>
              {engagement.critical_findings !== undefined && engagement.critical_findings > 0 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-[#6d6760] dark:text-slate-400">Critical</span>
                  <span className="font-bold text-[#9d1f1f]">
                    {engagement.critical_findings}
                  </span>
                </div>
              )}
              {engagement.high_findings !== undefined && engagement.high_findings > 0 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-[#6d6760] dark:text-slate-400">High</span>
                  <span className="font-bold text-[#d6561c]">
                    {engagement.high_findings}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Timeline */}
          {engagement.start_date && (
            <div className="mb-4 space-y-1 text-xs text-[#8b8177] dark:text-slate-400">
              <div className="flex items-center justify-between">
                <span>Start:</span>
                <span>
                  {new Date(engagement.start_date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </span>
              </div>
              {engagement.end_date && (
                <div className="flex items-center justify-between">
                  <span>End:</span>
                  <span>
                    {new Date(engagement.end_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Assigned Experts */}
          {engagement.assigned_experts && engagement.assigned_experts.length > 0 && (
            <div className="mb-4 text-xs text-[#6d6760] dark:text-slate-400">
              {engagement.assigned_experts.length} expert{engagement.assigned_experts.length !== 1 ? 's' : ''} assigned
            </div>
          )}

          {/* View Button */}
          <Link
            href={`/organization/ai-red-teaming/${engagement.id}`}
            className="mt-auto flex w-full items-center justify-center gap-2 rounded-lg bg-[#2d2a26] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#1f1c19] dark:bg-slate-700 dark:hover:bg-slate-600"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
            View Engagement
          </Link>
        </Card>
      ))}
    </div>
  );
}
