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
import { useState } from 'react';

export default function OrganizationReportDetailPage() {
  const params = useParams();
  const user = useAuthStore((state) => state.user);
  const reportId = params.id as string;
  const [commentText, setCommentText] = useState('');

  // Fetch report details
  const { data: report, isLoading, error } = useApiQuery(
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
  const addCommentMutation = useApiMutation(
    `/reports/${reportId}/comments`,
    'POST',
    {
      onSuccess: () => {
        refetchComments();
        setCommentText('');
      },
    }
  );

  const handleAddComment = () => {
    if (!commentText.trim()) return;
    addCommentMutation.mutate({ comment_text: commentText });
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
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-gray-900 dark:border-slate-700 dark:border-t-slate-100"></div>
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
            {/* Report Header Section */}
            <section className="border-b border-gray-200 pb-8 dark:border-slate-700">
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
                <div className="space-y-3">
                  {report.attachments.map((attachment: any) => (
                    <div
                      key={attachment.id}
                      className="flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-700 dark:bg-slate-800"
                    >
                      <div className="flex items-center gap-3">
                        <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-slate-100">
                            {attachment.filename}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-slate-400">
                            {attachment.file_type} • {(attachment.file_size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                      </div>
                      <Button size="sm" variant="secondary">
                        Download
                      </Button>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Discussion Section */}
            <section className="border-t border-gray-200 pt-8 dark:border-slate-700">
              <h2 className="mb-6 text-xl font-bold uppercase tracking-wide text-gray-900 dark:text-slate-100">
                Discussion ({comments.length})
              </h2>

              {/* Add Comment Form */}
              <div className="mb-8 rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-slate-700 dark:bg-slate-800">
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
                      className="border-l-4 border-gray-300 bg-white pl-6 py-4 dark:border-slate-600 dark:bg-slate-800"
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
