'use client';

import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiQuery } from '@/hooks/useApiQuery';
import { AlertCircle, FileCode } from 'lucide-react';

interface CodeReviewEngagement {
  id: string;
  title: string;
  repository_url: string;
  review_type: string;
  status: string;
  findings_count: number;
  report_submitted_at?: string | null;
  created_at: string;
}

interface CodeReviewFinding {
  id: string;
  title: string;
  description: string;
  severity: string;
  issue_type: string;
  file_path?: string | null;
  line_number?: number | null;
  status: string;
  created_at?: string;
}

interface FindingListResponse {
  findings: CodeReviewFinding[];
  total: number;
}

interface EngagementStats {
  total_findings: number;
  by_severity: Record<string, number>;
  by_issue_type: Record<string, number>;
}

interface CodeReviewEngagementReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagement: CodeReviewEngagement;
}

function formatLabel(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const severityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-blue-100 text-blue-800',
  info: 'bg-gray-100 text-gray-700',
};

export default function CodeReviewEngagementReportModal({
  isOpen,
  onClose,
  engagement,
}: CodeReviewEngagementReportModalProps) {
  const { data: findingsData, isLoading: loadingFindings, error: findingsError, refetch } = useApiQuery<FindingListResponse>(
    isOpen ? `/code-review/engagements/${engagement.id}/findings` : '',
    { enabled: isOpen }
  );

  const { data: stats, isLoading: loadingStats } = useApiQuery<EngagementStats>(
    isOpen ? `/code-review/engagements/${engagement.id}/stats` : '',
    { enabled: isOpen }
  );

  const findings = findingsData?.findings ?? [];
  const reportDelivered = Boolean(engagement.report_submitted_at) || engagement.status === 'completed';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Code review report" size="xl">
      <div className="space-y-6">
        <div className="rounded-xl border border-[#e6ddd4] bg-[#f8fbfa] p-4">
          <h3 className="text-lg font-semibold text-[#2d2a26]">{engagement.title}</h3>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-[#6d6760]">
            <span className="inline-flex items-center gap-1">
              <FileCode className="h-4 w-4" />
              {engagement.repository_url}
            </span>
            <span>{formatLabel(engagement.review_type)}</span>
            <span className="font-medium text-[#2d2a26]">Status: {formatLabel(engagement.status)}</span>
          </div>
          {reportDelivered ? (
            <p className="mt-3 text-sm font-medium text-green-700">
              Report delivered
              {engagement.report_submitted_at
                ? ` on ${new Date(engagement.report_submitted_at).toLocaleString()}`
                : ''}
            </p>
          ) : (
            <p className="mt-3 text-sm text-amber-700">
              Review in progress — findings may still be added until the researcher submits the final report.
            </p>
          )}
        </div>

        {!loadingStats && stats ? (
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-[#e6ddd4] bg-white p-4 text-center">
              <p className="text-2xl font-bold text-[#2d2a26]">{stats.total_findings}</p>
              <p className="text-xs text-[#8b8177]">Total findings</p>
            </div>
            <div className="rounded-xl border border-[#e6ddd4] bg-white p-4">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#8b8177]">By severity</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.by_severity || {}).map(([key, count]) =>
                  count > 0 ? (
                    <span key={key} className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityColors[key] || severityColors.info}`}>
                      {formatLabel(key)}: {count}
                    </span>
                  ) : null
                )}
              </div>
            </div>
            <div className="rounded-xl border border-[#e6ddd4] bg-white p-4">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#8b8177]">Issue types</p>
              <div className="flex flex-wrap gap-1 text-xs text-[#6d6760]">
                {Object.entries(stats.by_issue_type || {}).map(([key, count]) => (
                  <span key={key}>
                    {formatLabel(key)} ({count})
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : null}

        <div>
          <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#8b8177]">
            Findings ({findings.length})
          </h4>

          {loadingFindings ? (
            <p className="py-8 text-center text-sm text-[#6d6760]">Loading findings...</p>
          ) : findingsError ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <div>
                  <p className="text-sm font-medium text-red-800">Could not load findings</p>
                  <p className="mt-1 text-xs text-red-700">{findingsError.message}</p>
                  <Button size="sm" variant="outline" className="mt-2" onClick={() => refetch()}>
                    Retry
                  </Button>
                </div>
              </div>
            </div>
          ) : findings.length === 0 ? (
            <p className="rounded-xl border border-dashed border-[#e6ddd4] py-10 text-center text-sm text-[#6d6760]">
              No findings recorded yet.
            </p>
          ) : (
            <div className="max-h-96 space-y-3 overflow-y-auto pr-1">
              {findings.map((finding) => (
                <div key={finding.id} className="rounded-xl border border-[#e6ddd4] bg-white p-4">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="font-semibold text-[#2d2a26]">{finding.title}</p>
                    <div className="flex flex-wrap gap-2">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          severityColors[finding.severity] || severityColors.info
                        }`}
                      >
                        {formatLabel(finding.severity)}
                      </span>
                      <span className="rounded-full bg-[#f3ede6] px-2.5 py-0.5 text-xs font-medium text-[#2d2a26]">
                        {formatLabel(finding.issue_type)}
                      </span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm leading-relaxed text-[#6d6760]">{finding.description}</p>
                  {finding.file_path ? (
                    <p className="mt-2 font-mono text-xs text-[#8b8177]">
                      {finding.file_path}
                      {finding.line_number ? `:${finding.line_number}` : ''}
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end border-t border-[#e6ddd4] pt-4">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
