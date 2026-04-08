'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Spinner from '@/components/ui/Spinner';
import Avatar from '@/components/ui/Avatar';

interface Comment {
  id: string;
  comment_text: string;
  comment_type: string;
  is_internal: boolean;
  created_at: string;
  author_id?: string;
  author_role?: string;
  user: {
    id: string;
    username: string;
    role: string;
  } | null;
}

interface ReportCommentsProps {
  reportId: string;
}

export default function ReportComments({ reportId }: ReportCommentsProps) {
  const [newComment, setNewComment] = useState('');

  const { data: commentsData, isLoading, refetch } = useApiQuery<{ comments: Comment[]; total: number }>(
    `/reports/${reportId}/comments`,
    { enabled: !!reportId }
  );

  const { mutate: addComment, isLoading: isSubmitting } = useApiMutation(
    `/reports/${reportId}/comments`,
    'POST',
    {
      onSuccess: () => {
        setNewComment('');
        refetch();
      },
    }
  );

  const comments = commentsData?.comments || [];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      addComment({
        comment_text: newComment.trim(),
        comment_type: 'comment',
        is_internal: false,
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role?.toLowerCase()) {
      case 'researcher':
        return 'bg-[#3b82f6] text-white';
      case 'organization':
        return 'bg-[#8b5cf6] text-white';
      case 'triage_specialist':
        return 'bg-[#f59e0b] text-white';
      case 'admin':
        return 'bg-[#ef4444] text-white';
      default:
        return 'bg-[#6b7280] text-white';
    }
  };

  const getCommentAuthorName = (comment: Comment) => {
    if (comment.user?.username) {
      return comment.user.username;
    }

    if (comment.author_role) {
      return formatRoleLabel(comment.author_role);
    }

    return 'Unknown user';
  };

  const getCommentAuthorRole = (comment: Comment) => {
    return comment.user?.role || comment.author_role || 'unknown';
  };

  const formatRoleLabel = (role: string) => {
    return role.replace(/[_-]/g, ' ').replace(/\b\w/g, (character) => character.toUpperCase());
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner size="md" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="rounded-2xl bg-[#faf6f1] p-8 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
              No comments yet
            </p>
            <p className="mt-2 text-sm text-[#6d6760]">
              Be the first to add a comment to this report.
            </p>
          </div>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="rounded-2xl bg-[#faf6f1] p-5">
              <div className="flex items-start gap-4">
                {/* Avatar */}
                <Avatar
                  fallback={getCommentAuthorName(comment)}
                  size="md"
                  className="flex-shrink-0"
                />

                {/* Comment Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-sm font-semibold text-[#2d2a26]">
                      {getCommentAuthorName(comment)}
                    </p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${getRoleBadgeColor(
                        getCommentAuthorRole(comment)
                      )}`}
                    >
                      {formatRoleLabel(getCommentAuthorRole(comment)).toUpperCase()}
                    </span>
                    <span className="text-xs text-[#8b8177]">•</span>
                    <span className="text-xs text-[#8b8177]">
                      {formatDate(comment.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                    {comment.comment_text}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Comment Form */}
      <form onSubmit={handleSubmit} className="rounded-2xl bg-[#faf6f1] p-5">
        <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
          Add Comment
        </label>
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write your comment here..."
          rows={4}
          disabled={isSubmitting}
          className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none resize-vertical disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <div className="flex justify-end mt-3">
          <button
            type="submit"
            disabled={isSubmitting || !newComment.trim()}
            className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Posting...
              </>
            ) : (
              'Post Comment'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
