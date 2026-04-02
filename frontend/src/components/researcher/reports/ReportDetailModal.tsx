'use client';

import { useEffect, useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Modal from '@/components/ui/Modal';
import Badge from '@/components/ui/Badge';
import Spinner from '@/components/ui/Spinner';
import ReportComments from './ReportComments';
import ReportTimeline from './ReportTimeline';

interface ReportDetailModalProps {
  reportId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

interface ReportDetail {
  id: string;
  report_number: string;
  title: string;
  description: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  affected_asset?: string;
  suggested_severity: string;
  vulnerability_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  program: {
    id: string;
    name: string;
  };
  researcher: {
    id: string;
    username: string;
  };
  attachments?: Array<{
    id: string;
    filename: string;
    file_type: string;
    file_size: number;
    uploaded_at: string;
  }>;
}

export default function ReportDetailModal({ reportId, isOpen, onClose }: ReportDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'details' | 'comments' | 'timeline'>('details');
  
  const { data: report, isLoading, error } = useApiQuery<ReportDetail>(
    reportId || '',
    { enabled: !!reportId && isOpen }
  );

  // Reset to details tab when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab('details');
    }
  }, [isOpen]);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-[#7f1d1d] text-white';
      case 'high':
        return 'bg-[#ef2330] text-white';
      case 'medium':
        return 'bg-[#f59e0b] text-white';
      case 'low':
        return 'bg-[#10b981] text-white';
      default:
        return 'bg-[#6b7280] text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'new':
        return 'bg-[#3b82f6] text-white';
      case 'triaged':
        return 'bg-[#8b5cf6] text-white';
      case 'accepted':
        return 'bg-[#10b981] text-white';
      case 'rejected':
        return 'bg-[#ef4444] text-white';
      case 'resolved':
        return 'bg-[#059669] text-white';
      case 'duplicate':
        return 'bg-[#6b7280] text-white';
      default:
        return 'bg-[#8b8177] text-white';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-[#2d2a26]">
                {report?.report_number || 'Loading...'}
              </h2>
              {report && (
                <>
                  <Badge className={getSeverityColor(report.suggested_severity)}>
                    {report.suggested_severity?.toUpperCase()}
                  </Badge>
                  <Badge className={getStatusColor(report.status)}>
                    {report.status?.toUpperCase()}
                  </Badge>
                </>
              )}
            </div>
            {report && (
              <p className="text-sm text-[#6d6760]">
                Submitted {formatDate(report.created_at)}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-[#8b8177] hover:text-[#2d2a26] transition"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <Spinner size="lg" />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
            <p className="font-semibold">Error Loading Report</p>
            <p className="mt-1">Unable to load report details. Please try again.</p>
          </div>
        )}

        {/* Report Content */}
        {report && (
          <div className="space-y-5">
            {/* Tabs */}
            <div className="flex gap-2 border-b border-[#e6ddd4]">
              <button
                onClick={() => setActiveTab('details')}
                className={`px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
                  activeTab === 'details'
                    ? 'border-[#ef2330] text-[#ef2330]'
                    : 'border-transparent text-[#6d6760] hover:text-[#2d2a26]'
                }`}
              >
                Details
              </button>
              <button
                onClick={() => setActiveTab('comments')}
                className={`px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
                  activeTab === 'comments'
                    ? 'border-[#ef2330] text-[#ef2330]'
                    : 'border-transparent text-[#6d6760] hover:text-[#2d2a26]'
                }`}
              >
                Comments
              </button>
              <button
                onClick={() => setActiveTab('timeline')}
                className={`px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
                  activeTab === 'timeline'
                    ? 'border-[#ef2330] text-[#ef2330]'
                    : 'border-transparent text-[#6d6760] hover:text-[#2d2a26]'
                }`}
              >
                Timeline
              </button>
            </div>

            {/* Details Tab */}
            {activeTab === 'details' && (
              <div className="space-y-5">
                {/* Program Info */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Program
                  </p>
                  <p className="text-sm font-medium text-[#2d2a26]">{report.program.name}</p>
                </div>

                {/* Title */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Title
                  </p>
                  <p className="text-base font-semibold text-[#2d2a26]">{report.title}</p>
                </div>

                {/* Vulnerability Type */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                    Vulnerability Type
                  </p>
                  <p className="text-sm text-[#2d2a26]">{report.vulnerability_type}</p>
                </div>

                {/* Description */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                    Description
                  </p>
                  <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                    {report.description}
                  </p>
                </div>

                {/* Steps to Reproduce */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                    Steps to Reproduce
                  </p>
                  <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                    {report.steps_to_reproduce}
                  </p>
                </div>

                {/* Impact Assessment */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                    Impact Assessment
                  </p>
                  <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                    {report.impact_assessment}
                  </p>
                </div>

                {/* Affected Asset */}
                {report.affected_asset && (
                  <div className="rounded-2xl bg-[#faf6f1] p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
                      Affected Asset
                    </p>
                    <p className="text-sm text-[#2d2a26]">{report.affected_asset}</p>
                  </div>
                )}

                {/* Attachments */}
                {report.attachments && report.attachments.length > 0 && (
                  <div className="rounded-2xl bg-[#faf6f1] p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                      Evidence Files ({report.attachments.length})
                    </p>
                    <div className="space-y-2">
                      {report.attachments.map((attachment) => (
                        <div
                          key={attachment.id}
                          className="flex items-center justify-between bg-white rounded-xl px-4 py-3 border border-[#d8d0c8]"
                        >
                          <div className="flex items-center gap-3">
                            <svg className="w-5 h-5 text-[#8b8177]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <div>
                              <p className="text-sm font-medium text-[#2d2a26]">{attachment.filename}</p>
                              <p className="text-xs text-[#6d6760]">
                                {formatFileSize(attachment.file_size)} • {attachment.file_type}
                              </p>
                            </div>
                          </div>
                          <button className="text-[#ef2330] hover:text-[#d41f2c] transition text-sm font-medium">
                            Download
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="rounded-2xl bg-[#faf6f1] p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                    Report Information
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-[#6d6760]">Report ID</p>
                      <p className="text-[#2d2a26] font-medium mt-1">{report.report_number}</p>
                    </div>
                    <div>
                      <p className="text-[#6d6760]">Status</p>
                      <p className="text-[#2d2a26] font-medium mt-1 capitalize">{report.status}</p>
                    </div>
                    <div>
                      <p className="text-[#6d6760]">Submitted</p>
                      <p className="text-[#2d2a26] font-medium mt-1">{formatDate(report.created_at)}</p>
                    </div>
                    <div>
                      <p className="text-[#6d6760]">Last Updated</p>
                      <p className="text-[#2d2a26] font-medium mt-1">{formatDate(report.updated_at)}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Comments Tab */}
            {activeTab === 'comments' && reportId && (
              <ReportComments reportId={reportId} />
            )}

            {/* Timeline Tab */}
            {activeTab === 'timeline' && reportId && (
              <ReportTimeline reportId={reportId} />
            )}
          </div>
        )}

        {/* Footer Actions */}
        {report && (
          <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4]">
            <button
              onClick={onClose}
              className="inline-flex rounded-full border border-[#d8d0c8] px-6 py-2.5 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </Modal>
  );
}
