'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Spinner from '@/components/ui/Spinner';
import Badge from '@/components/ui/Badge';

interface KYCStatus {
  status: string;
  submitted_at?: string;
  reviewed_at?: string;
  rejection_reason?: string;
  documents: Array<{
    document_type: string;
    status: string;
    uploaded_at: string;
  }>;
}

export default function KYCStatus() {
  const [uploadingDoc, setUploadingDoc] = useState<string | null>(null);

  const { data: kycData, isLoading, refetch } = useApiQuery<KYCStatus>(
    '/kyc/status',
    { enabled: true }
  );

  const { mutate: uploadDocument, isLoading: isUploading } = useApiMutation(
    '/kyc/submit',
    'POST',
    {
      onSuccess: () => {
        setUploadingDoc(null);
        refetch();
      },
    }
  );

  const handleFileUpload = async (documentType: string, file: File) => {
    setUploadingDoc(documentType);
    
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);

    // Note: This would need to be adjusted based on actual API requirements
    uploadDocument(formData as any);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
      case 'verified':
        return 'bg-[#10b981] text-white';
      case 'pending':
      case 'submitted':
        return 'bg-[#f59e0b] text-white';
      case 'rejected':
      case 'failed':
        return 'bg-[#ef4444] text-white';
      case 'not_started':
        return 'bg-[#6b7280] text-white';
      default:
        return 'bg-[#8b8177] text-white';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
      case 'verified':
        return (
          <svg className="w-6 h-6 text-[#10b981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'pending':
      case 'submitted':
        return (
          <svg className="w-6 h-6 text-[#f59e0b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'rejected':
      case 'failed':
        return (
          <svg className="w-6 h-6 text-[#ef4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-6 h-6 text-[#6b7280]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const requiredDocuments = [
    { type: 'id_card', label: 'Government ID', description: 'National ID, Passport, or Driver\'s License' },
    { type: 'proof_of_address', label: 'Proof of Address', description: 'Utility bill or bank statement (less than 3 months old)' },
    { type: 'tax_form', label: 'Tax Information', description: 'Tax ID or W-9 form' },
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  const status = kycData?.status || 'not_started';

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className="rounded-2xl bg-[#faf6f1] p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            {getStatusIcon(status)}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-bold text-[#2d2a26]">KYC Verification Status</h3>
              <Badge className={getStatusColor(status)}>
                {status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
            <p className="text-sm text-[#6d6760]">
              {status === 'approved' && 'Your identity has been verified. You can now withdraw funds.'}
              {status === 'pending' && 'Your documents are being reviewed. This usually takes 1-2 business days.'}
              {status === 'rejected' && 'Your verification was rejected. Please review the feedback and resubmit.'}
              {status === 'not_started' && 'Complete your KYC verification to enable withdrawals.'}
            </p>
            {kycData?.submitted_at && (
              <p className="text-xs text-[#8b8177] mt-2">
                Submitted: {new Date(kycData.submitted_at).toLocaleDateString()}
              </p>
            )}
            {kycData?.reviewed_at && (
              <p className="text-xs text-[#8b8177] mt-1">
                Reviewed: {new Date(kycData.reviewed_at).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>

        {/* Rejection Reason */}
        {status === 'rejected' && kycData?.rejection_reason && (
          <div className="mt-4 pt-4 border-t border-[#e6ddd4]">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
              Rejection Reason
            </p>
            <p className="text-sm text-[#b42318]">{kycData.rejection_reason}</p>
          </div>
        )}
      </div>

      {/* Required Documents */}
      {status !== 'approved' && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
            Required Documents
          </h3>

          {requiredDocuments.map((doc) => {
            const uploadedDoc = kycData?.documents?.find(d => d.document_type === doc.type);
            const docStatus = uploadedDoc?.status || 'not_uploaded';

            return (
              <div key={doc.type} className="rounded-2xl bg-[#faf6f1] p-5">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-semibold text-[#2d2a26]">{doc.label}</p>
                      {uploadedDoc && (
                        <Badge className={getStatusColor(docStatus)}>
                          {docStatus.replace('_', ' ').toUpperCase()}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-[#6d6760]">{doc.description}</p>
                    {uploadedDoc && (
                      <p className="text-xs text-[#8b8177] mt-2">
                        Uploaded: {new Date(uploadedDoc.uploaded_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>

                  {/* Upload Button */}
                  {(!uploadedDoc || docStatus === 'rejected') && (
                    <div>
                      <input
                        type="file"
                        id={`upload-${doc.type}`}
                        accept="image/*,.pdf"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            handleFileUpload(doc.type, file);
                          }
                        }}
                        className="hidden"
                        disabled={uploadingDoc === doc.type}
                      />
                      <label
                        htmlFor={`upload-${doc.type}`}
                        className={`inline-flex items-center gap-2 rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7] cursor-pointer ${
                          uploadingDoc === doc.type ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {uploadingDoc === doc.type ? (
                          <>
                            <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Uploading...
                          </>
                        ) : (
                          <>
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            {uploadedDoc ? 'Re-upload' : 'Upload'}
                          </>
                        )}
                      </label>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info Box */}
      <div className="rounded-2xl bg-[#eef5fb] border border-[#b8d4f1] p-5 text-sm text-[#2d78a8]">
        <p className="font-semibold mb-2">ℹ️ Important Information</p>
        <ul className="list-disc list-inside space-y-1 text-xs">
          <li>All documents must be clear and readable</li>
          <li>Accepted formats: JPG, PNG, PDF (max 5MB per file)</li>
          <li>Documents must be in English or Amharic</li>
          <li>Verification typically takes 1-2 business days</li>
          <li>You'll be notified via email once your verification is complete</li>
        </ul>
      </div>
    </div>
  );
}
