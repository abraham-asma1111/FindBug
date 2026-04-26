'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import Modal from '@/components/ui/Modal';
import { api } from '@/lib/api';
import { AlertCircle, CheckCircle, Clock, Flag, ArrowLeft, FileText, Image, Video } from 'lucide-react';

interface Finding {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  cvss_score?: number;
  affected_component?: string;
  reproduction_steps?: string;  // Backend field name
  impact_analysis?: string;  // Backend field name
  remediation?: string;
  exploit_screenshots?: string[];
  exploit_video_url?: string;
  discovered_at?: string;
  validated?: boolean;
  retest_required?: boolean;
  triage_notes?: string;
  engagement_id: string;
}

const severityColors = {
  CRITICAL: 'bg-red-100 text-red-700 border-red-300',
  HIGH: 'bg-orange-100 text-orange-700 border-orange-300',
  MEDIUM: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  LOW: 'bg-blue-100 text-blue-700 border-blue-300',
  INFO: 'bg-gray-100 text-gray-700 border-gray-300',
};

const statusColors = {
  SUBMITTED: 'bg-blue-100 text-blue-700',
  VALIDATED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  RETEST_REQUESTED: 'bg-orange-100 text-orange-700',
  FIXED: 'bg-green-100 text-green-700',
};

export default function OrganizationFindingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const findingId = params.findingId as string;
  const user = useAuthStore((state) => state.user);
  
  const [showRetestModal, setShowRetestModal] = useState(false);
  const [retestNotes, setRetestNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);

  const { data: finding, isLoading, error, refetch } = useApiQuery<Finding>({
    endpoint: `/ptaas/findings/${findingId}`,
    queryKey: ['finding', findingId]
  });

  // Debug: Log the finding data
  if (finding) {
    console.log('Finding data:', finding);
    console.log('exploit_screenshots:', finding.exploit_screenshots);
  }

  const handleRequestRetest = async () => {
    setIsSubmitting(true);
    try {
      await api.post(`/ptaas/findings/${findingId}/retest`, {
        fix_description: retestNotes,
        fix_implemented_at: new Date().toISOString()
      });
      setShowRetestModal(false);
      setRetestNotes('');
      refetch();
      
      // Show success message
      const successDiv = document.createElement('div');
      successDiv.className = 'fixed top-4 right-4 z-50 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg animate-fade-in';
      successDiv.innerHTML = `
        <div class="flex items-center gap-3">
          <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <p class="font-semibold text-green-900">Retest Submitted Successfully!</p>
            <p class="text-sm text-green-700">The researcher will be notified to verify the fix.</p>
          </div>
        </div>
      `;
      document.body.appendChild(successDiv);
      setTimeout(() => {
        successDiv.remove();
      }, 5000);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to request retest';
      console.error('Retest error:', error.response?.data);
      
      // Show error message
      const errorDiv = document.createElement('div');
      errorDiv.className = 'fixed top-4 right-4 z-50 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg animate-fade-in';
      errorDiv.innerHTML = `
        <div class="flex items-center gap-3">
          <svg class="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <p class="font-semibold text-red-900">Failed to Submit Retest</p>
            <p class="text-sm text-red-700">${errorMessage}</p>
          </div>
        </div>
      `;
      document.body.appendChild(errorDiv);
      setTimeout(() => {
        errorDiv.remove();
      }, 5000);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user ? (
          <PortalShell
            user={user}
            title="Finding Details"
            subtitle="Loading..."
            navItems={getPortalNavItems(user.role)}
            headerAlign="left"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="animate-pulse space-y-4">
              <div className="h-64 bg-[#faf6f1] rounded-2xl"></div>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  if (error || !finding) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user ? (
          <PortalShell
            user={user}
            title="Finding Not Found"
            subtitle="Unable to load finding details"
            navItems={getPortalNavItems(user.role)}
            headerAlign="left"
            eyebrowText="Organization Portal"
            eyebrowClassName="text-xl tracking-[0.18em]"
          >
            <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">Failed to load finding</h3>
                  <p className="text-sm text-red-700">{error?.message || 'Finding not found'}</p>
                </div>
              </div>
            </div>
          </PortalShell>
        ) : null}
      </ProtectedRoute>
    );
  }

  const severityClass = severityColors[finding.severity as keyof typeof severityColors] || severityColors.INFO;
  const statusClass = statusColors[finding.status as keyof typeof statusColors] || statusColors.SUBMITTED;

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Finding Details"
          subtitle="Review and triage security finding"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Back Button */}
            <Button
              variant="outline"
              onClick={() => router.back()}
              icon={ArrowLeft}
            >
              Back
            </Button>

            {/* Single Page Layout */}
            <div className="rounded-2xl border border-[#e6ddd4] bg-white shadow-sm">
              {/* Header Section */}
              <div className="p-8 border-b border-[#e6ddd4]">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <Flag className="h-6 w-6 text-[#8b8177]" />
                      <h1 className="text-2xl font-semibold text-[#2d2a26]">{finding.title}</h1>
                    </div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium border ${severityClass}`}>
                        {finding.severity}
                      </span>
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusClass}`}>
                        {finding.status}
                      </span>
                      {finding.cvss_score && (
                        <span className="text-sm text-[#6d6760]">
                          CVSS: <span className="font-semibold">{finding.cvss_score}</span>
                        </span>
                      )}
                      {finding.discovered_at && (
                        <span className="text-sm text-[#8b8177]">
                          Discovered: {new Date(finding.discovered_at).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric'
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => setShowRetestModal(true)}
                    >
                      Request Retest
                    </Button>
                  </div>
                </div>

                {/* Triage Status Inline */}
                {(finding.validated || finding.triage_notes) && (
                  <div className="mt-4 p-4 rounded-lg border border-blue-200 bg-blue-50">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        {finding.validated && (
                          <p className="text-sm font-medium text-blue-900 mb-1">✓ Validated</p>
                        )}
                        {finding.triage_notes && (
                          <p className="text-sm text-blue-800">{finding.triage_notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Content Section */}
              <div className="p-8 space-y-8">
                {/* Description */}
                <div>
                  <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Description</h3>
                  <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                    {finding.description}
                  </p>
                </div>

                {/* Affected Component */}
                {finding.affected_component && (
                  <div>
                    <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Affected Component</h3>
                    <p className="text-sm text-[#2d2a26] font-mono bg-[#faf6f1] p-3 rounded-lg">
                      {finding.affected_component}
                    </p>
                  </div>
                )}

                {/* Steps to Reproduce */}
                {finding.reproduction_steps && (
                  <div>
                    <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Steps to Reproduce</h3>
                    <div className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed bg-[#faf6f1] p-4 rounded-lg">
                      {finding.reproduction_steps}
                    </div>
                  </div>
                )}

                {/* Impact */}
                {finding.impact_analysis && (
                  <div>
                    <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Impact</h3>
                    <p className="text-sm text-[#2d2a26] whitespace-pre-wrap leading-relaxed">
                      {finding.impact_analysis}
                    </p>
                  </div>
                )}

                {/* Remediation */}
                {finding.remediation && (
                  <div>
                    <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Recommended Remediation</h3>
                    <div className="p-4 rounded-lg border border-green-200 bg-green-50">
                      <p className="text-sm text-green-900 whitespace-pre-wrap leading-relaxed">
                        {finding.remediation}
                      </p>
                    </div>
                  </div>
                )}

                {/* Evidence */}
                {(finding.exploit_screenshots?.length || finding.exploit_video_url) && (
                  <div>
                    <h3 className="text-base font-semibold text-[#2d2a26] mb-3 pb-2 border-b border-[#e6ddd4]">Evidence</h3>
                    
                    {/* Screenshots */}
                    {finding.exploit_screenshots && finding.exploit_screenshots.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-sm font-medium text-[#6d6760] mb-3 flex items-center gap-2">
                          <Image className="h-4 w-4" />
                          Screenshots ({finding.exploit_screenshots.length})
                        </h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          {finding.exploit_screenshots.map((url, idx) => {
                            // Handle both external URLs and internal file paths
                            const imageUrl = url.startsWith('http') 
                              ? url 
                              : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/api/v1/files/serve/${url}`;
                            
                            return (
                              <button
                                key={idx}
                                onClick={() => setLightboxImage(imageUrl)}
                                className="relative aspect-video rounded-lg overflow-hidden border border-[#e6ddd4] hover:border-blue-500 transition-colors group"
                              >
                                <img
                                  src={imageUrl}
                                  alt={`Screenshot ${idx + 1}`}
                                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                  loading="lazy"
                                  crossOrigin="anonymous"
                                  onError={(e) => {
                                    console.error('Failed to load thumbnail:', imageUrl);
                                    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext fill="%236b7280" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-family="sans-serif"%3EImage unavailable%3C/text%3E%3C/svg%3E';
                                  }}
                                />
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Video */}
                    {finding.exploit_video_url && (
                      <div>
                        <h4 className="text-sm font-medium text-[#6d6760] mb-3 flex items-center gap-2">
                          <Video className="h-4 w-4" />
                          Exploit Video
                        </h4>
                        <video
                          controls
                          className="w-full max-w-2xl rounded-lg border border-[#e6ddd4]"
                          src={finding.exploit_video_url}
                        >
                          Your browser does not support the video tag.
                        </video>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Retest Modal */}
            <Modal
              isOpen={showRetestModal}
              onClose={() => setShowRetestModal(false)}
              title="Request Retest"
            >
              <div className="space-y-4">
                <p className="text-sm text-[#6d6760]">
                  Request the researcher to verify that this vulnerability has been fixed.
                </p>

                <Textarea
                  label="Fix Description"
                  value={retestNotes}
                  onChange={(e) => setRetestNotes(e.target.value)}
                  rows={4}
                  placeholder="Describe what was fixed and what the researcher should verify... (minimum 20 characters)"
                  required
                />

                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowRetestModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleRequestRetest}
                    isLoading={isSubmitting}
                    disabled={!retestNotes.trim() || retestNotes.trim().length < 20}
                    className="flex-1"
                  >
                    Request Retest
                  </Button>
                </div>
              </div>
            </Modal>

            {/* Lightbox */}
            {lightboxImage && (
              <div
                className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
                onClick={() => setLightboxImage(null)}
              >
                <button
                  className="absolute top-4 right-4 text-white text-4xl hover:text-gray-300 w-12 h-12 flex items-center justify-center"
                  onClick={() => setLightboxImage(null)}
                  aria-label="Close"
                >
                  ×
                </button>
                <div className="relative max-w-7xl max-h-[90vh] flex items-center justify-center">
                  <img
                    src={lightboxImage}
                    alt="Evidence"
                    className="max-w-full max-h-[90vh] object-contain rounded-lg"
                    onClick={(e) => e.stopPropagation()}
                    crossOrigin="anonymous"
                    onError={(e) => {
                      console.error('Failed to load lightbox image:', lightboxImage);
                      // Show error message in lightbox
                      const errorDiv = document.createElement('div');
                      errorDiv.className = 'text-white text-center p-8';
                      errorDiv.innerHTML = `
                        <svg class="h-16 w-16 mx-auto mb-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <p class="text-xl font-semibold mb-2">Failed to load image</p>
                        <p class="text-sm text-gray-400">The image could not be loaded from the source</p>
                        <p class="text-xs text-gray-500 mt-2 break-all">${lightboxImage}</p>
                      `;
                      e.currentTarget.replaceWith(errorDiv);
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
