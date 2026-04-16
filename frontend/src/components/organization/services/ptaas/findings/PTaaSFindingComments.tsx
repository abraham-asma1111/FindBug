'use client';

import React, { useState } from 'react';
import { useApiQuery, useApiMutation } from '@/hooks/useApiQuery';
import { MessageSquare, Trash2, Edit2, Paperclip } from 'lucide-react';
import Button from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';

interface Comment {
  id: string;
  content: string;
  created_by: string;
  created_at: string;
  attachments?: string[];
}

interface PTaaSFindingCommentsProps {
  findingId: string;
}

export default function PTaaSFindingComments({ findingId }: PTaaSFindingCommentsProps) {
  const { showToast } = useToast();
  const [newComment, setNewComment] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');

  const { data: comments, isLoading, refetch } = useApiQuery<Comment[]>(
    `/ptaas/findings/${findingId}/comments`
  );

  const addCommentMutation = useApiMutation(
    `/ptaas/findings/${findingId}/comments`,
    'POST',
    {
      onSuccess: () => {
        showToast('Comment added successfully', 'success');
        setNewComment('');
        refetch();
      },
      onError: () => {
        showToast('Failed to add comment', 'error');
      },
    }
  );

  const updateCommentMutation = useApiMutation(
    `/ptaas/comments/${editingId}`,
    'PATCH',
    {
      onSuccess: () => {
        showToast('Comment updated successfully', 'success');
        setEditingId(null);
        setEditContent('');
        refetch();
      },
      onError: () => {
        showToast('Failed to update comment', 'error');
      },
    }
  );

  const deleteCommentMutation = useApiMutation(
    `/ptaas/comments/{id}`,
    'DELETE',
    {
      onSuccess: () => {
        showToast('Comment deleted successfully', 'success');
        refetch();
      },
      onError: () => {
        showToast('Failed to delete comment', 'error');
      },
    }
  );

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    
    addCommentMutation.mutate({
      content: newComment,
      attachments: [],
    });
  };

  const handleUpdateComment = () => {
    if (!editContent.trim()) return;
    
    updateCommentMutation.mutate({
      content: editContent,
    });
  };

  const handleDeleteComment = (commentId: string) => {
    if (confirm('Are you sure you want to delete this comment?')) {
      deleteCommentMutation.mutate({}, `/ptaas/comments/${commentId}`);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3b82f6]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Comment Input */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1]">
          Add Comment
        </label>
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          rows={3}
          className="w-full px-4 py-3 rounded-lg border border-[#e6ddd4] dark:border-[#3d3a36] bg-white dark:bg-[#2d2a26] text-[#2d2a26] dark:text-[#faf6f1] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]"
        />
        <div className="flex justify-end gap-2">
          <Button
            onClick={handleAddComment}
            disabled={!newComment.trim() || addCommentMutation.isLoading}
            className="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Post Comment
          </Button>
        </div>
      </div>

      {/* Comments List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
          Comments ({comments?.length || 0})
        </h3>

        {comments && comments.length > 0 ? (
          <div className="space-y-4">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="p-4 rounded-lg bg-[#faf6f1] dark:bg-[#3d3a36] border border-[#e6ddd4] dark:border-[#4d4a46]"
              >
                {editingId === comment.id ? (
                  <div className="space-y-3">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 rounded border border-[#e6ddd4] dark:border-[#3d3a36] bg-white dark:bg-[#2d2a26] text-[#2d2a26] dark:text-[#faf6f1]"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={handleUpdateComment}
                        size="sm"
                        className="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
                      >
                        Save
                      </Button>
                      <Button
                        onClick={() => {
                          setEditingId(null);
                          setEditContent('');
                        }}
                        size="sm"
                        variant="outline"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">
                          User {comment.created_by}
                        </p>
                        <p className="text-sm text-[#6b6662] dark:text-[#a39e9a]">
                          {formatDate(comment.created_at)}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setEditingId(comment.id);
                            setEditContent(comment.content);
                          }}
                          className="p-1 text-[#6b6662] hover:text-[#3b82f6] transition-colors"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 text-[#6b6662] hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    <p className="text-[#2d2a26] dark:text-[#e6ddd4] whitespace-pre-wrap">
                      {comment.content}
                    </p>

                    {comment.attachments && comment.attachments.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {comment.attachments.map((attachment, idx) => (
                          <a
                            key={idx}
                            href={attachment}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 px-3 py-1 rounded bg-white dark:bg-[#2d2a26] text-sm text-[#3b82f6] hover:underline"
                          >
                            <Paperclip className="h-3 w-3" />
                            Attachment {idx + 1}
                          </a>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-[#6b6662] dark:text-[#a39e9a]">
            No comments yet. Be the first to comment!
          </div>
        )}
      </div>
    </div>
  );
}
