'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, ChevronLeft, CheckCircle, XCircle, User, FileText, Calendar, Download, Image as ImageIcon } from 'lucide-react';
import Link from 'next/link';

interface KYCDetail {
  id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  status: string;
  verification_level: string;
  submitted_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  rejection_reason: string | null;
  documents: Array<{
    id: string;
    document_type: string;
    file_url: string;
    uploaded_at: string;
  }>;
  personal_info: {
    full_name: string;
    date_of_birth: string;
    country: string;
    address: string;
  };
}

const statusColors: Record<string, string> = {
  pending: 'bg-[#F59E0B] text-white',
  approved: 'bg-[#10B981] text-white',
  rejected: 'bg-[#EF4444] text-white',
  under_review: 'bg-[#3B82F6] text-white',
};

export default function KYCDetailPage() {
  const params = useParams();
  const kycId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const [notes, setNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: kyc, isLoading, error, refetch } = useApiQuery<KYCDetail>({
    endpoint: `/kyc/verifications/${kycId}`,
  });

  const approveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/kyc/verifications'] });
      alert('KYC approved successfully');
    },
    onError: (error: any) => {
      alert(`Failed to approve KYC: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const rejectMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      queryClient.invalidateQueries({ queryKey: ['/kyc/verifications'] });
      alert('KYC rejected');
      setRejectionReason('');
    },
    onError: (error: any) => {
      alert(`Failed to reject KYC: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const handleApprove = () => {
    if (!confirm('Are you sure you want to approve this KYC verification?')) return;
    approveMutation.mutate({
      endpoint: `/kyc/verifications/${kycId}/approve`,
      notes,
    });
  };

  const handleReject = () => {
    if (!rejectionReason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }
    if (!confirm('Are you sure you want to reject this KYC verification?')) return;
    rejectMutation.mutate({
      endpoint: `/kyc/verifications/${kycId}/reject`,
      rejection_reason: rejectionReason,
    });
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="KYC Details"
          subtitle="Review and verify KYC submission"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/finance/kyc" className="text-[#3B82F6] hover:underline text-sm">
              KYC Verifications
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">KYC Details</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading KYC verification...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load KYC verification</p>
              </div>
            </div>
          ) : kyc ? (
            <div className="space-y-6">
              {/* KYC Header */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                      KYC Verification for {kyc.user_name}
                    </h2>
                    <div className="flex items-center gap-3 text-sm text-[#94A3B8]">
                      <span className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        {kyc.user_email}
                      </span>
                      <span>•</span>
                      <span>Submitted {new Date(kyc.submitted_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>Level: {kyc.verification_level}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColors[kyc.status] || 'bg-[#94A3B8] text-white'}`}>
                      {kyc.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Personal Information */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Personal Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Full Name</p>
                    <p className="text-[#F8FAFC] font-medium">{kyc.personal_info.full_name}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Date of Birth</p>
                    <p className="text-[#F8FAFC] font-medium">{kyc.personal_info.date_of_birth}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Country</p>
                    <p className="text-[#F8FAFC] font-medium">{kyc.personal_info.country}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-1">Address</p>
                    <p className="text-[#F8FAFC] font-medium">{kyc.personal_info.address}</p>
                  </div>
                </div>
              </div>

              {/* Documents */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Verification Documents ({kyc.documents.length})
                </h3>

                {kyc.documents.length === 0 ? (
                  <div className="text-center py-8 text-[#94A3B8]">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No documents uploaded</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {kyc.documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center gap-3 p-3 bg-[#0F172A] rounded-lg border border-[#334155]"
                      >
                        <ImageIcon className="w-5 h-5 text-[#3B82F6]" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-[#F8FAFC]">
                            {doc.document_type}
                          </p>
                          <p className="text-xs text-[#94A3B8]">
                            Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                          </p>
                        </div>
                        <a
                          href={doc.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 rounded-lg hover:bg-[#334155] transition-colors"
                        >
                          <Download className="w-4 h-4 text-[#94A3B8]" />
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Review Information */}
              {kyc.reviewed_by && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Review Information</h3>
                  <div className="p-4 bg-[#0F172A] rounded-lg border border-[#334155]">
                    <p className="text-[#F8FAFC] mb-1">Reviewed by: {kyc.reviewed_by}</p>
                    <p className="text-sm text-[#94A3B8]">
                      {kyc.reviewed_at ? new Date(kyc.reviewed_at).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                </div>
              )}

              {/* Rejection Reason */}
              {kyc.rejection_reason && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Rejection Reason</h3>
                  <div className="p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg">
                    <p className="text-[#F8FAFC]">{kyc.rejection_reason}</p>
                  </div>
                </div>
              )}

              {/* Action Form (Only for Pending) */}
              {kyc.status === 'pending' && (
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Review KYC</h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Review Notes (Optional)
                    </label>
                    <Textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      placeholder="Add any notes about this verification..."
                    />
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={handleApprove}
                      disabled={approveMutation.isLoading}
                      className="gap-2 bg-[#10B981] hover:bg-[#059669]"
                    >
                      <CheckCircle className="w-4 h-4" />
                      {approveMutation.isLoading ? 'Approving...' : 'Approve KYC'}
                    </Button>

                    <Button
                      onClick={() => {
                        const reason = prompt('Enter rejection reason:');
                        if (reason) {
                          setRejectionReason(reason);
                          setTimeout(() => handleReject(), 100);
                        }
                      }}
                      disabled={rejectMutation.isLoading}
                      variant="outline"
                      className="gap-2 border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white"
                    >
                      <XCircle className="w-4 h-4" />
                      {rejectMutation.isLoading ? 'Rejecting...' : 'Reject KYC'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Timeline */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Timeline
                </h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[#3B82F6]"></div>
                    <div>
                      <p className="text-[#F8FAFC] font-medium">KYC Submitted</p>
                      <p className="text-sm text-[#94A3B8]">{new Date(kyc.submitted_at).toLocaleString()}</p>
                    </div>
                  </div>
                  {kyc.reviewed_at && (
                    <div className="flex gap-3">
                      <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${kyc.status === 'approved' ? 'bg-[#10B981]' : 'bg-[#EF4444]'}`}></div>
                      <div>
                        <p className="text-[#F8FAFC] font-medium">KYC {kyc.status === 'approved' ? 'Approved' : 'Rejected'}</p>
                        <p className="text-sm text-[#94A3B8]">{new Date(kyc.reviewed_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Back Button */}
              <div className="flex gap-3">
                <Link href="/finance/kyc">
                  <Button variant="outline" className="gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Back to KYC List
                  </Button>
                </Link>
              </div>
            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
