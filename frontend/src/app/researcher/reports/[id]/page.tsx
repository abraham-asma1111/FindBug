'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Spinner from '@/components/ui/Spinner';
import ReportComments from '@/components/researcher/reports/ReportComments';
import ReportTimeline from '@/components/researcher/reports/ReportTimeline';
import MediaViewer from '@/components/common/MediaViewer';
import { api } from '@/lib/api';
import { Eye, Download } from 'lucide-react';

interface ReportDetail {
  id: string;
  title: string;
  description: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  affected_asset?: string;
  suggested_severity: 'critical' | 'high' | 'medium' | 'low';
  vulnerability_type?: string;
  status: string;
  submitted_at: string;
  program: {
    id: string;
    name: string;
  };
  researcher: {
    id: string;
    name: string;
    email: string;
  };
  bounty_amount?: number;
  attachments?: Array<{
    id: string;
    filename: string;
    original_filename?: string;
    file_type: string;
    file_size: number;
    storage_path: string;
    uploaded_at?: string;
  }>;
}

const severityColors: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-[#2d2a26]',
  low: 'bg-[#2d78a8] text-white',
};

const statusColors: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  pending: 'bg-[#faf1e1] text-[#9a6412]',
  approved: 'bg-[#eef7ef] text-[#24613a]',
  rejected: 'bg-[#fff2f1] text-[#b42318]',
  resolved: 'bg-[#f3ede6] text-[#5f5851]',
};

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const reportId = params.id as string;
  const [activeTab, setActiveTab] = useState('details');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isMediaViewerOpen, setIsMediaViewerOpen] = useState(false);
  const [selectedAttachmentIndex, setSelectedAttachmentIndex] = useState(0);

  const { data: report, isLoading, isError } = useApiQuery<ReportDetail>(
    `/reports/${reportId}`,
    { enabled: !!reportId }
  );

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
      return;
    }

    try {
      setIsDeleting(true);
      await api.delete(`/reports/${reportId}`);
      alert('Report deleted successfully');
      router.push('/researcher/reports');
    } catch (error: any) {
      console.error('Delete error:', error);
      alert(error.response?.data?.detail || 'Failed to delete report');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEdit = () => {
    // Navigate to edit page or show edit modal
    alert('Edit functionality coming soon');
  };

  const handleViewAttachment = (index: number) => {
    setSelectedAttachmentIndex(index);
    setIsMediaViewerOpen(true);
  };

  const handleDownloadAttachment = (attachment: any) => {
    const link = document.createElement('a');
    link.href = `/api/v1/files/serve/${attachment.storage_path}`;
    link.download = attachment.original_filename || attachment.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isMediaFile = (fileType: string) => {
    return fileType?.startsWith('image/') || fileType?.startsWith('video/') || fileType === 'application/pdf';
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title=""
          subtitle=""
          navItems={getPortalNavItems(user.role)}
        >
          {/* Breadcrumb Navigation */}
          <div className="mb-6">
            <nav className="flex items-center gap-2 text-sm">
              <button
                onClick={() => router.push('/researcher/reports')}
                className="text-[#6d6760] dark:text-gray-400 hover:text-[#2d2a26] dark:hover:text-white transition"
              >
                My reports
              </button>
              <svg
                className="h-4 w-4 text-[#8b8177] dark:text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
              <span className="font-semibold text-[#ef2330]">
                {isLoading ? 'Loading...' : report?.title || 'Report Details'}
              </span>
            </nav>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <Spinner size="lg" />
            </div>
          ) : isError || !report ? (
            <div className="rounded-2xl border border-[#f2c0bc] dark:border-red-900 bg-[#fff2f1] dark:bg-[#111111] p-6 text-center">
              <p className="text-sm text-[#b42318] dark:text-red-400">
                Failed to load report details. Please try again.
              </p>
              <button
                onClick={() => router.push('/researcher/reports')}
                className="mt-4 rounded-full bg-[#ef2330] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
              >
                Back to Reports
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Header */}
              <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold text-[#2d2a26] dark:text-white mb-3">
                      {report.title}
                    </h1>
                    <div className="flex flex-wrap items-center gap-3">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          severityColors[report.suggested_severity] || 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300'
                        }`}
                      >
                        {report.suggested_severity.toUpperCase()}
                      </span>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          statusColors[report.status] || 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300'
                        }`}
                      >
                        {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                      </span>
                      {report.vulnerability_type && (
                        <span className="rounded-full bg-[#f3ede6] dark:bg-neutral-800 px-3 py-1 text-xs font-semibold text-[#5f5851] dark:text-gray-300">
                          {report.vulnerability_type}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {report.status === 'new' && (
                      <>
                        <button
                          onClick={handleEdit}
                          className="rounded-full border border-[#d8d0c8] dark:border-gray-700 px-4 py-2 text-sm font-semibold text-[#2d2a26] dark:text-white transition hover:border-[#c8bfb6] dark:hover:border-gray-600 hover:bg-[#fcfaf7] dark:hover:bg-neutral-800"
                        >
                          Edit
                        </button>
                        <button
                          onClick={handleDelete}
                          disabled={isDeleting}
                          className="rounded-full border border-[#f2c0bc] dark:border-red-900 px-4 py-2 text-sm font-semibold text-[#b42318] dark:text-red-400 transition hover:bg-[#fff2f1] dark:hover:bg-neutral-800"
                        >
                          {isDeleting ? 'Deleting...' : 'Delete'}
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Metadata */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t border-[#e6ddd4] dark:border-gray-800">
                  <div>
                    <p className="text-xs text-[#8b8177] dark:text-gray-400 mb-1">Program</p>
                    <p className="text-sm font-semibold text-[#2d2a26] dark:text-white">
                      {report.program?.name || 'Unknown Program'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#8b8177] dark:text-gray-400 mb-1">Submitted</p>
                    <p className="text-sm font-semibold text-[#2d2a26] dark:text-white">
                      {new Date(report.submitted_at).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#8b8177] dark:text-gray-400 mb-1">Bounty</p>
                    <p className="text-sm font-semibold text-[#2d2a26] dark:text-white">
                      {report.bounty_amount ? `${report.bounty_amount.toLocaleString()} ETB` : 'Pending'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-4 border-b border-[#e6ddd4] dark:border-gray-800">
                <button
                  onClick={() => setActiveTab('details')}
                  className={`pb-3 px-1 text-sm font-semibold transition ${
                    activeTab === 'details'
                      ? 'border-b-2 border-[#ef2330] text-[#ef2330]'
                      : 'text-[#6d6760] dark:text-gray-400 hover:text-[#2d2a26] dark:hover:text-white'
                  }`}
                >
                  Details
                </button>
                <button
                  onClick={() => setActiveTab('timeline')}
                  className={`pb-3 px-1 text-sm font-semibold transition ${
                    activeTab === 'timeline'
                      ? 'border-b-2 border-[#ef2330] text-[#ef2330]'
                      : 'text-[#6d6760] dark:text-gray-400 hover:text-[#2d2a26] dark:hover:text-white'
                  }`}
                >
                  Timeline
                </button>
                <button
                  onClick={() => setActiveTab('comments')}
                  className={`pb-3 px-1 text-sm font-semibold transition ${
                    activeTab === 'comments'
                      ? 'border-b-2 border-[#ef2330] text-[#ef2330]'
                      : 'text-[#6d6760] dark:text-gray-400 hover:text-[#2d2a26] dark:hover:text-white'
                  }`}
                >
                  Comments
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'details' && (
                <div className="space-y-6">
                  {/* Description */}
                  <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                    <h3 className="text-sm font-semibold text-[#2d2a26] dark:text-white mb-3">Description</h3>
                    <p className="text-sm text-[#6d6760] dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {report.description}
                    </p>
                  </div>

                  {/* Steps to Reproduce */}
                  <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                    <h3 className="text-sm font-semibold text-[#2d2a26] dark:text-white mb-3">Steps to Reproduce</h3>
                    <p className="text-sm text-[#6d6760] dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {report.steps_to_reproduce}
                    </p>
                  </div>

                  {/* Impact Assessment */}
                  <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                    <h3 className="text-sm font-semibold text-[#2d2a26] dark:text-white mb-3">Impact Assessment</h3>
                    <p className="text-sm text-[#6d6760] dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {report.impact_assessment}
                    </p>
                  </div>

                  {/* Affected Asset */}
                  {report.affected_asset && (
                    <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                      <h3 className="text-sm font-semibold text-[#2d2a26] dark:text-white mb-3">Affected Asset</h3>
                      <p className="text-sm text-[#6d6760] dark:text-gray-300">{report.affected_asset}</p>
                    </div>
                  )}

                  {/* Attachments */}
                  {report.attachments && report.attachments.length > 0 && (
                    <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                      <h3 className="text-sm font-semibold text-[#2d2a26] dark:text-white mb-4">
                        Evidence Files ({report.attachments.length})
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {report.attachments.map((attachment: any, index: number) => {
                          const isMedia = isMediaFile(attachment.file_type);
                          const isImage = attachment.file_type?.startsWith('image/');
                          const isVideo = attachment.file_type?.startsWith('video/');
                          
                          return (
                            <div
                              key={attachment.id}
                              className="group relative rounded-xl border border-[#e6ddd4] dark:border-gray-800 bg-[#faf6f1] dark:bg-neutral-900 overflow-hidden"
                            >
                              {/* Preview Thumbnail */}
                              {isImage && (
                                <div className="aspect-video bg-gray-100 dark:bg-neutral-900 relative overflow-hidden">
                                  <img
                                    src={`/api/v1/files/serve/${attachment.storage_path}`}
                                    alt={attachment.filename}
                                    className="w-full h-full object-cover"
                                  />
                                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center">
                                    <button
                                      onClick={() => handleViewAttachment(index)}
                                      className="opacity-0 group-hover:opacity-100 transition-opacity rounded-full bg-white p-3 shadow-lg hover:scale-110 transform"
                                    >
                                      <Eye className="h-5 w-5 text-gray-900" />
                                    </button>
                                  </div>
                                </div>
                              )}
                              
                              {isVideo && (
                                <div className="aspect-video bg-gray-100 dark:bg-neutral-900 relative overflow-hidden">
                                  <video
                                    src={`/api/v1/files/serve/${attachment.storage_path}`}
                                    className="w-full h-full object-cover"
                                  />
                                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center">
                                    <button
                                      onClick={() => handleViewAttachment(index)}
                                      className="opacity-0 group-hover:opacity-100 transition-opacity rounded-full bg-white p-3 shadow-lg hover:scale-110 transform"
                                    >
                                      <Eye className="h-5 w-5 text-gray-900" />
                                    </button>
                                  </div>
                                </div>
                              )}
                              
                              {/* File Info */}
                              <div className="p-4">
                                <div className="flex items-start justify-between gap-3">
                                  <div className="flex items-start gap-3 flex-1 min-w-0">
                                    <svg className="h-5 w-5 text-[#8b8177] dark:text-gray-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                                    </svg>
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium text-[#2d2a26] dark:text-white truncate">
                                        {attachment.filename}
                                      </p>
                                      <p className="text-xs text-[#6d6760] dark:text-gray-400">
                                        {attachment.file_type} • {(attachment.file_size / 1024).toFixed(2)} KB
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex gap-2 flex-shrink-0">
                                    {isMedia && (
                                      <button
                                        onClick={() => handleViewAttachment(index)}
                                        className="p-2 rounded-lg hover:bg-[#f3ede6] dark:hover:bg-neutral-800 transition"
                                        title="View"
                                      >
                                        <Eye className="h-4 w-4 text-[#6d6760] dark:text-gray-400" />
                                      </button>
                                    )}
                                    <button
                                      onClick={() => handleDownloadAttachment(attachment)}
                                      className="p-2 rounded-lg hover:bg-[#f3ede6] dark:hover:bg-neutral-800 transition"
                                      title="Download"
                                    >
                                      <Download className="h-4 w-4 text-[#6d6760] dark:text-gray-400" />
                                    </button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'timeline' && (
                <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                  <ReportTimeline reportId={reportId} />
                </div>
              )}

              {activeTab === 'comments' && (
                <div className="rounded-2xl border border-[#e6ddd4] dark:border-gray-800 bg-white dark:bg-[#111111] p-6">
                  <ReportComments reportId={reportId} />
                </div>
              )}

              {/* Media Viewer Modal */}
              {report && report.attachments && report.attachments.length > 0 && (
                <MediaViewer
                  attachments={report.attachments}
                  initialIndex={selectedAttachmentIndex}
                  isOpen={isMediaViewerOpen}
                  onClose={() => setIsMediaViewerOpen(false)}
                />
              )}
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
