'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems, formatCurrency } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import MediaViewer from '@/components/common/MediaViewer';
import { useState } from 'react';
import { Eye, Download } from 'lucide-react';

export default function OrganizationReportDetailPage() {
  const params = useParams();
  const user = useAuthStore((state) => state.user);
  const reportId = params.id as string;
  const [commentText, setCommentText] = useState('');
  const [isMediaViewerOpen, setIsMediaViewerOpen] = useState(false);
  const [selectedAttachmentIndex, setSelectedAttachmentIndex] = useState(0);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);

  // Fetch report details
  const { data: report, isLoading, error, refetch: refetchReport } = useApiQuery(
    `/reports/${reportId}`,
    { enabled: !!user && !!reportId }
  );

  // Fetch comments
  const { data: commentsData, refetch: refetchComments } = useApiQuery(
    `/reports/${reportId}/comments`,
    { enabled: !!user && !!reportId }
  );

  const comments = commentsData?.comments || commentsData || [];

  // Add comment mutation
  const addCommentMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetchComments();
      setCommentText('');
    },
  });

  // Approve bounty mutation
  const approveBountyMutation = useApiMutation({
    method: 'POST',
    onSuccess: (data) => {
      refetchReport();
      setShowApprovalDialog(false);
      // Show success message
      alert(`Bounty approved successfully! Total cost: ${formatCurrency(data.total_cost)} (Bounty: ${formatCurrency(data.bounty_amount)} + Commission: ${formatCurrency(data.commission)})`);
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to approve bounty');
    }
  });

  const handleAddComment = () => {
    if (!commentText.trim()) return;
    addCommentMutation.mutate({ 
      endpoint: `/reports/${reportId}/comments`,
      comment_text: commentText 
    });
  };

  const handleApproveBounty = () => {
    approveBountyMutation.mutate({ endpoint: `/reports/${reportId}/approve-bounty` });
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

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="Report Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-gray-900 dark:border-gray-700 dark:border-t-slate-100"></div>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (error || !report) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="Report Not Found"
            subtitle="The report you're looking for doesn't exist"
            navItems={getPortalNavItems(user.role)}
            headerAlign="center"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
              <p className="text-sm text-red-800 dark:text-red-200">
                {error?.message || 'Report not found'}
              </p>
            </div>
            <div className="mt-6">
              <Link href="/organization/reports">
                <Button>Back to Reports</Button>
              </Link>
            </div>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title={report.title}
          subtitle={report.report_number || `Report #${reportId.slice(0, 8)}`}
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {/* Back Button */}
          <div className="mb-6">
            <Link
              href="/organization/reports"
              className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Reports
            </Link>
          </div>

          {/* Single Page Content - No Cards */}
          <div className="space-y-12">
            {/* Approve Bounty Section - Only show for valid reports that haven't been approved yet */}
            {report.status === 'valid' && report.bounty_amount && report.bounty_status !== 'approved' && (
              <section className="rounded-lg border-2 border-green-200 bg-green-50 p-6 dark:border-green-900 dark:bg-green-950">
                <div className="flex items-start justify-between gap-6">
                  <div className="flex-1">
                    <h3 className="mb-2 text-lg font-bold text-green-900 dark:text-green-100">
                      Ready for Bounty Approval
                    </h3>
                    <p className="mb-4 text-sm text-green-800 dark:text-green-200">
                      This vulnerability report has been validated and is ready for bounty payment approval.
                    </p>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-green-700 dark:text-green-300">
                          Bounty Amount
                        </p>
                        <p className="mt-1 text-lg font-bold text-green-900 dark:text-green-100">
                          {formatCurrency(report.bounty_amount)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-green-700 dark:text-green-300">
                          Platform Commission (30%)
                        </p>
                        <p className="mt-1 text-lg font-bold text-green-900 dark:text-green-100">
                          {formatCurrency(report.bounty_amount * 0.3)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-green-700 dark:text-green-300">
                          Total Cost
                        </p>
                        <p className="mt-1 text-lg font-bold text-red-600 dark:text-red-400">
                          {formatCurrency(report.bounty_amount * 1.3)}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <Button
                      onClick={() => setShowApprovalDialog(true)}
                      variant="primary"
                      size="lg"
                      disabled={approveBountyMutation.isLoading}
                    >
                      {approveBountyMutation.isLoading ? 'Approving...' : 'Approve Bounty'}
                    </Button>
                  </div>
                </div>
              </section>
            )}

            {/* Bounty Approved Status - Show when bounty is approved */}
            {report.bounty_status === 'approved' && (
              <section className="rounded-lg border-2 border-blue-200 bg-blue-50 p-6 dark:border-blue-900 dark:bg-blue-950">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-2 text-lg font-bold text-blue-900 dark:text-blue-100">
                      Bounty Approved
                    </h3>
                    <p className="mb-4 text-sm text-blue-800 dark:text-blue-200">
                      The bounty payment for this report has been approved and is now queued for processing by the Finance Officer.
                    </p>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-300">
                          Bounty Amount
                        </p>
                        <p className="mt-1 text-lg font-bold text-blue-900 dark:text-blue-100">
                          {formatCurrency(report.bounty_amount)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-300">
                          Commission (30%)
                        </p>
                        <p className="mt-1 text-lg font-bold text-blue-900 dark:text-blue-100">
                          {formatCurrency(report.bounty_amount * 0.3)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-300">
                          Total Paid
                        </p>
                        <p className="mt-1 text-lg font-bold text-blue-900 dark:text-blue-100">
                          {formatCurrency(report.bounty_amount * 1.3)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>The Finance Officer will process this payment and credit the researcher's wallet.</span>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Approval Confirmation Dialog */}
            {showApprovalDialog && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                <div className="mx-4 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-[#0a0a0a]">
                  <h3 className="mb-4 text-xl font-bold text-gray-900 dark:text-slate-100">
                    Confirm Bounty Approval
                  </h3>
                  <div className="mb-6 space-y-4">
                    <p className="text-sm text-gray-700 dark:text-slate-300">
                      You are about to approve the bounty payment for this vulnerability report. The following amount will be deducted from your organization wallet:
                    </p>
                    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-[#111111]">
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600 dark:text-slate-400">Bounty Amount:</span>
                          <span className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                            {formatCurrency(report.bounty_amount)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600 dark:text-slate-400">Platform Commission (30%):</span>
                          <span className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                            {formatCurrency(report.bounty_amount * 0.3)}
                          </span>
                        </div>
                        <div className="border-t border-gray-300 pt-2 dark:border-gray-600">
                          <div className="flex justify-between">
                            <span className="text-sm font-bold text-gray-900 dark:text-slate-100">Total Cost:</span>
                            <span className="text-lg font-bold text-red-600 dark:text-red-400">
                              {formatCurrency(report.bounty_amount * 1.3)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-slate-400">
                      ⚠️ This action cannot be undone. The funds will be transferred to the platform wallet and queued for payment processing by the Finance Officer.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      onClick={() => setShowApprovalDialog(false)}
                      variant="secondary"
                      className="flex-1"
                      disabled={approveBountyMutation.isLoading}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleApproveBounty}
                      variant="primary"
                      className="flex-1"
                      disabled={approveBountyMutation.isLoading}
                    >
                      {approveBountyMutation.isLoading ? 'Processing...' : 'Confirm Approval'}
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Report Header Section */}
            <section className="border-b border-gray-200 pb-8 dark:border-gray-700">
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className={`inline-flex items-center rounded-md px-3 py-1 text-xs font-bold uppercase ${
                  (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'critical'
                    ? 'bg-red-600 text-white'
                    : (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'high'
                      ? 'bg-orange-500 text-white'
                      : (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'medium'
                        ? 'bg-yellow-500 text-gray-900'
                        : (report.assigned_severity || report.suggested_severity)?.toLowerCase() === 'low'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-300 text-gray-800'
                }`}>
                  {report.assigned_severity || report.suggested_severity || 'Unscored'}
                </span>
                {/* Show BOUNTY APPROVED badge if bounty is approved, otherwise show regular status */}
                {report.bounty_status === 'approved' ? (
                  <span className="inline-flex items-center rounded-md bg-green-600 px-3 py-1 text-xs font-bold uppercase text-white">
                    <svg className="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Bounty Approved
                  </span>
                ) : (
                  <span className={`inline-flex items-center rounded-md px-3 py-1 text-xs font-bold uppercase ${
                    report.status === 'new'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : report.status === 'triaged'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : report.status === 'valid'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : report.status === 'resolved'
                            ? 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                            : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {report.status}
                  </span>
                )}
                {report.cvss_score && (
                  <span className="inline-flex items-center rounded-md bg-gray-200 px-3 py-1 text-xs font-bold uppercase text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                    CVSS {report.cvss_score.toFixed(1)}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Submitted</p>
                  <p className="mt-2 text-sm text-gray-900 dark:text-slate-100">
                    {report.created_at
                      ? new Date(report.created_at).toLocaleDateString('en-US', {
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Bounty</p>
                  <p className="mt-2 text-sm font-semibold text-red-600 dark:text-red-400">
                    {report.bounty_amount ? formatCurrency(report.bounty_amount) : 'Not set'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Program</p>
                  <p className="mt-2 text-sm text-gray-900 dark:text-slate-100">
                    {report.program?.name || '-'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400">Researcher</p>
                  <p className="mt-2 text-sm text-gray-900 dark:text-slate-100">
                    {report.researcher?.username || '-'}
                  </p>
                </div>
              </div>
            </section>

            {/* Report Description */}
            <section>
              <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                Report Description
              </h2>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <p className="whitespace-pre-wrap text-gray-700 dark:text-slate-300">
                  {report.description || 'No description provided'}
                </p>
              </div>
            </section>

            {/* Steps to Reproduce */}
            {report.steps_to_reproduce && (
              <section>
                <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Steps to Reproduce
                </h2>
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <p className="whitespace-pre-wrap text-gray-700 dark:text-slate-300">
                    {report.steps_to_reproduce}
                  </p>
                </div>
              </section>
            )}

            {/* Impact Assessment */}
            {report.impact_assessment && (
              <section>
                <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Impact Assessment
                </h2>
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <p className="whitespace-pre-wrap text-gray-700 dark:text-slate-300">
                    {report.impact_assessment}
                  </p>
                </div>
              </section>
            )}

            {/* Affected Asset */}
            {report.affected_asset && (
              <section>
                <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Affected Asset
                </h2>
                <p className="text-gray-700 dark:text-slate-300">{report.affected_asset}</p>
              </section>
            )}

            {/* Vulnerability Type */}
            {report.vulnerability_type && (
              <section>
                <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Vulnerability Type
                </h2>
                <p className="text-gray-700 dark:text-slate-300">{report.vulnerability_type}</p>
              </section>
            )}

            {/* Attachments */}
            {report.attachments && report.attachments.length > 0 && (
              <section>
                <h2 className="mb-4 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                  Attachments ({report.attachments.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.attachments.map((attachment: any, index: number) => {
                    const isMedia = isMediaFile(attachment.file_type);
                    const isImage = attachment.file_type?.startsWith('image/');
                    const isVideo = attachment.file_type?.startsWith('video/');
                    
                    return (
                      <div
                        key={attachment.id}
                        className="group relative rounded-lg border border-gray-200 bg-gray-50 overflow-hidden dark:border-gray-700 dark:bg-[#111111]"
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
                              <svg className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                              </svg>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                                  {attachment.filename}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-slate-400">
                                  {attachment.file_type} • {(attachment.file_size / 1024).toFixed(2)} KB
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2 flex-shrink-0">
                              {isMedia && (
                                <button
                                  onClick={() => handleViewAttachment(index)}
                                  className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-neutral-800 transition"
                                  title="View"
                                >
                                  <Eye className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                                </button>
                              )}
                              <button
                                onClick={() => handleDownloadAttachment(attachment)}
                                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-neutral-800 transition"
                                title="Download"
                              >
                                <Download className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Media Viewer Modal */}
                {report.attachments && report.attachments.length > 0 && (
                  <MediaViewer
                    attachments={report.attachments}
                    initialIndex={selectedAttachmentIndex}
                    isOpen={isMediaViewerOpen}
                    onClose={() => setIsMediaViewerOpen(false)}
                  />
                )}
              </section>
            )}

            {/* Discussion Section */}
            <section className="border-t border-gray-200 pt-8 dark:border-gray-700">
              <h2 className="mb-6 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                Discussion ({comments.length})
              </h2>

              {/* Add Comment Form */}
              <div className="mb-8 rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-gray-700 dark:bg-[#111111]">
                <Textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="Add a comment..."
                  rows={4}
                  className="mb-4"
                />
                <Button
                  onClick={handleAddComment}
                  disabled={!commentText.trim() || addCommentMutation.isLoading}
                  size="sm"
                >
                  {addCommentMutation.isLoading ? 'Adding...' : 'Add Comment'}
                </Button>
              </div>

              {/* Comments List */}
              <div className="space-y-6">
                {comments.length > 0 ? (
                  comments.map((comment: any) => (
                    <div
                      key={comment.id}
                      className="border-l-4 border-gray-300 bg-white dark:bg-[#111111] pl-6 py-4 dark:border-slate-600 dark:bg-[#111111]"
                    >
                      <div className="mb-2 flex items-center gap-3">
                        <p className="text-sm font-bold text-gray-900 dark:text-slate-100">
                          {comment.user?.email || comment.author_role || 'Unknown'}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-slate-400">
                          {comment.created_at
                            ? new Date(comment.created_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })
                            : ''}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-slate-300">
                        {comment.comment_text || comment.comment}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="py-8 text-center text-sm text-gray-500 dark:text-slate-400">
                    No comments yet. Be the first to comment!
                  </p>
                )}
              </div>
            </section>
          </div>
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
