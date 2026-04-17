'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useAuthStore } from '@/store/authStore';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import Button from '@/components/ui/Button';
import { 
  ArrowLeft, AlertCircle, CheckCircle, Clock, FileText, Code, Shield, 
  TrendingUp, Users, Database, Wrench, Image, Video, X, ChevronRight 
} from 'lucide-react';
import { useState } from 'react';

export default function ResearcherFindingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const findingId = params.findingId as string;
  const engagementId = params.id as string;
  const [activeTab, setActiveTab] = useState('overview');
  const [lightboxMedia, setLightboxMedia] = useState<{url: string, type: 'image' | 'video'} | null>(null);
  const user = useAuthStore((state) => state.user);

  const { data: finding, isLoading } = useApiQuery<any>({
    endpoint: `/ptaas/findings/${findingId}`
  });

  // Show loading state while user or finding data is loading
  if (!user || isLoading) {
    return (
      <div className="min-h-screen bg-[#faf6f1] dark:bg-black">
        <div className="grid min-h-screen lg:grid-cols-[280px_minmax(0,1fr)]">
          {/* Sidebar skeleton */}
          <aside className="border-b border-[#ddd4cb] dark:border-gray-800 bg-[#faf6f1] dark:bg-neutral-900 px-6 py-8">
            <div className="space-y-8">
              <div className="h-10 bg-[#e6ddd4] dark:bg-neutral-800 rounded animate-pulse"></div>
              <div className="space-y-2">
                <div className="h-10 bg-[#e6ddd4] dark:bg-neutral-800 rounded animate-pulse"></div>
                <div className="h-10 bg-[#e6ddd4] dark:bg-neutral-800 rounded animate-pulse"></div>
                <div className="h-10 bg-[#e6ddd4] dark:bg-neutral-800 rounded animate-pulse"></div>
              </div>
            </div>
          </aside>
          
          {/* Main content skeleton */}
          <div className="flex min-h-screen min-w-0 flex-col">
            <header className="sticky top-0 z-20 border-b border-[#ddd4cb] dark:border-gray-800 bg-[#fcfaf7]/95 dark:bg-neutral-900/95 backdrop-blur px-6 py-5">
              <div className="h-8 bg-[#e6ddd4] dark:bg-neutral-800 rounded w-1/3 animate-pulse"></div>
            </header>
            <main className="flex-1 px-6 py-8">
              <div className="space-y-4">
                <div className="rounded-2xl border border-[#e6ddd4] bg-white px-4 py-3">
                  <div className="h-5 bg-[#faf6f1] rounded w-1/3 animate-pulse"></div>
                </div>
                <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6">
                  <div className="space-y-4 animate-pulse">
                    <div className="h-8 bg-[#faf6f1] rounded w-2/3"></div>
                    <div className="h-64 bg-[#faf6f1] rounded"></div>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </div>
    );
  }

  if (!finding) {
    return (
      <PortalShell
        user={user}
        title="Finding Not Found"
        subtitle="The requested finding could not be found"
        navItems={getPortalNavItems(user.role)}
      >
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">Finding not found</h3>
              <p className="text-sm text-red-700">The finding you're looking for doesn't exist or you don't have access to it.</p>
            </div>
          </div>
        </div>
      </PortalShell>
    );
  }

  const severityConfig: Record<string, { color: string; icon: any }> = {
    Critical: { color: 'bg-red-100 text-red-700 border-red-200', icon: AlertCircle },
    High: { color: 'bg-orange-100 text-orange-700 border-orange-200', icon: TrendingUp },
    Medium: { color: 'bg-yellow-100 text-yellow-700 border-yellow-200', icon: AlertCircle },
    Low: { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Shield },
    Info: { color: 'bg-gray-100 text-gray-700 border-gray-200', icon: FileText },
  };

  const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
    SUBMITTED: { label: 'Submitted', color: 'bg-blue-100 text-blue-700', icon: Clock },
    TRIAGED: { label: 'Triaged', color: 'bg-purple-100 text-purple-700', icon: CheckCircle },
    VALIDATED: { label: 'Validated', color: 'bg-green-100 text-green-700', icon: CheckCircle },
    REJECTED: { label: 'Rejected', color: 'bg-red-100 text-red-700', icon: AlertCircle },
  };

  const severityInfo = severityConfig[finding.severity] || severityConfig.Info;
  const statusInfo = statusConfig[finding.status] || statusConfig.SUBMITTED;
  const SeverityIcon = severityInfo.icon;
  const StatusIcon = statusInfo.icon;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'technical', label: 'Technical Details' },
    { id: 'impact', label: 'Impact Analysis' },
    { id: 'remediation', label: 'Remediation' },
    { id: 'evidence', label: 'Evidence' },
  ];

  return (
    <PortalShell
      user={user}
      title={finding.title}
      subtitle={`${finding.severity} severity finding`}
      navItems={getPortalNavItems(user.role)}
    >
      <div className="space-y-4">
        {/* Breadcrumb Navigation */}
        <div className="rounded-2xl border border-[#e6ddd4] bg-white px-4 py-3">
          <nav className="flex items-center gap-2 text-sm">
            <Link 
              href="/researcher/programs/ptaas" 
              className="text-[#6d6760] hover:text-[#2d2a26] transition-colors"
            >
              PTaaS Engagements
            </Link>
            <ChevronRight className="h-4 w-4 text-[#8b8177]" />
            <Link 
              href={`/researcher/programs/ptaas/${engagementId}`}
              className="text-[#6d6760] hover:text-[#2d2a26] transition-colors"
            >
              Engagement Details
            </Link>
            <ChevronRight className="h-4 w-4 text-[#8b8177]" />
            <span className="text-[#2d2a26] font-medium">Finding Details</span>
          </nav>
        </div>

        {/* Finding Detail */}
        <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium border ${severityInfo.color}`}>
                <SeverityIcon className="h-3.5 w-3.5" />
                {finding.severity}
              </span>
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
                <StatusIcon className="h-3.5 w-3.5" />
                {statusInfo.label}
              </span>
              {finding.cvss_score && (
                <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700">
                  CVSS: {finding.cvss_score}
                </span>
              )}
            </div>
            <h2 className="text-xl font-semibold text-[#2d2a26] mb-2">{finding.title}</h2>
            {finding.discovered_at && (
              <p className="text-sm text-[#6d6760]">
                Discovered {new Date(finding.discovered_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            )}
          </div>

          {/* Tabs */}
          <div className="border-b border-[#e6ddd4]">
            <div className="flex gap-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                    activeTab === tab.id
                      ? 'text-[#3b82f6] border-[#3b82f6]'
                      : 'text-[#6d6760] border-transparent hover:text-[#2d2a26]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Quick Info Grid */}
                <div className="grid grid-cols-2 gap-4">
                  {finding.vulnerability_type && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">Vulnerability Type</label>
                      <p className="mt-1 text-sm text-[#2d2a26]">{finding.vulnerability_type}</p>
                    </div>
                  )}
                  {finding.affected_component && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">Affected Component</label>
                      <p className="mt-1 text-sm text-[#2d2a26]">{finding.affected_component}</p>
                    </div>
                  )}
                  {finding.cwe_id && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">CWE ID</label>
                      <p className="mt-1 text-sm text-[#2d2a26]">{finding.cwe_id}</p>
                    </div>
                  )}
                  {finding.owasp_category && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">OWASP Category</label>
                      <p className="mt-1 text-sm text-[#2d2a26]">{finding.owasp_category}</p>
                    </div>
                  )}
                </div>

                {finding.description && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2 flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Description
                    </h3>
                    <div className="p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                      <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.description}</p>
                    </div>
                  </div>
                )}

                {finding.reproduction_steps && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2 flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Reproduction Steps
                    </h3>
                    <div className="p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                      <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.reproduction_steps}</p>
                    </div>
                  </div>
                )}

                {finding.triage_notes && (
                  <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                    <div className="flex gap-3">
                      <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-blue-900 mb-1">Triage Notes</h4>
                        <p className="text-sm text-blue-700 whitespace-pre-wrap">{finding.triage_notes}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'technical' && (
              <div className="space-y-6">
                {finding.cvss_vector && (
                  <div>
                    <label className="text-sm font-medium text-[#8b8177]">CVSS Vector</label>
                    <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4] font-mono text-sm">
                      {finding.cvss_vector}
                    </div>
                  </div>
                )}

                {finding.affected_url && (
                  <div>
                    <label className="text-sm font-medium text-[#8b8177]">Affected URL</label>
                    <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                      <a 
                        href={finding.affected_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                      >
                        {finding.affected_url}
                      </a>
                    </div>
                  </div>
                )}

                {finding.proof_of_exploit && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2">Proof of Exploit</h3>
                    <div className="p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                      <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.proof_of_exploit}</p>
                    </div>
                  </div>
                )}

                {finding.exploit_code && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2 flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Exploit Code
                    </h3>
                    <div className="p-4 rounded-xl bg-gray-900 border border-gray-700">
                      <pre className="text-sm text-gray-100 overflow-x-auto">
                        <code>{finding.exploit_code}</code>
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'impact' && (
              <div className="space-y-6">
                {finding.impact_description && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2">Impact Description</h3>
                    <div className="p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                      <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.impact_description}</p>
                    </div>
                  </div>
                )}

                {finding.business_impact && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2">Business Impact</h3>
                    <div className="p-4 rounded-xl bg-orange-50 border border-orange-200">
                      <p className="text-sm text-orange-900 whitespace-pre-wrap">{finding.business_impact}</p>
                    </div>
                  </div>
                )}

                {/* CIA Triad */}
                {(finding.confidentiality_impact || finding.integrity_impact || finding.availability_impact) && (
                  <div className="grid grid-cols-3 gap-4">
                    {finding.confidentiality_impact && (
                      <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                        <div className="flex items-center gap-2 mb-2">
                          <Shield className="h-4 w-4 text-red-600" />
                          <span className="text-sm font-medium text-red-900">Confidentiality</span>
                        </div>
                        <p className="text-sm text-red-700">{finding.confidentiality_impact}</p>
                      </div>
                    )}
                    {finding.integrity_impact && (
                      <div className="p-4 rounded-xl bg-orange-50 border border-orange-200">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="h-4 w-4 text-orange-600" />
                          <span className="text-sm font-medium text-orange-900">Integrity</span>
                        </div>
                        <p className="text-sm text-orange-700">{finding.integrity_impact}</p>
                      </div>
                    )}
                    {finding.availability_impact && (
                      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="h-4 w-4 text-blue-600" />
                          <span className="text-sm font-medium text-blue-900">Availability</span>
                        </div>
                        <p className="text-sm text-blue-700">{finding.availability_impact}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Affected Users & Data */}
                <div className="grid grid-cols-2 gap-4">
                  {finding.affected_users && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Affected Users
                      </label>
                      <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                        <p className="text-sm text-[#2d2a26]">{finding.affected_users}</p>
                      </div>
                    </div>
                  )}
                  {finding.data_at_risk && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                        <Database className="h-4 w-4" />
                        Data at Risk
                      </label>
                      <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                        <p className="text-sm text-[#2d2a26]">{finding.data_at_risk}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'remediation' && (
              <div className="space-y-6">
                {/* Priority & Effort */}
                <div className="grid grid-cols-2 gap-4">
                  {finding.remediation_priority && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">Priority</label>
                      <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                        <p className="text-sm font-semibold text-[#2d2a26]">{finding.remediation_priority}</p>
                      </div>
                    </div>
                  )}
                  {finding.remediation_effort && (
                    <div>
                      <label className="text-sm font-medium text-[#8b8177]">Estimated Effort</label>
                      <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                        <p className="text-sm text-[#2d2a26]">{finding.remediation_effort}</p>
                      </div>
                    </div>
                  )}
                </div>

                {finding.remediation_recommendation && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2 flex items-center gap-2">
                      <Wrench className="h-4 w-4" />
                      Remediation Recommendation
                    </h3>
                    <div className="p-4 rounded-xl bg-green-50 border border-green-200">
                      <p className="text-sm text-green-900 whitespace-pre-wrap">{finding.remediation_recommendation}</p>
                    </div>
                  </div>
                )}

                {finding.remediation_steps && finding.remediation_steps.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-[#8b8177] mb-2 block">Remediation Steps</label>
                    <div className="space-y-2">
                      {finding.remediation_steps.map((step: string, idx: number) => (
                        <div key={idx} className="flex gap-3 p-3 rounded-lg border border-[#e6ddd4] bg-[#faf6f1]">
                          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold flex-shrink-0">
                            {idx + 1}
                          </div>
                          <p className="text-sm text-[#2d2a26]">{step}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {finding.code_fix_example && (
                  <div>
                    <h3 className="text-sm font-medium text-[#8b8177] mb-2 flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Code Fix Example
                    </h3>
                    <div className="p-4 rounded-xl bg-gray-900 border border-gray-700">
                      <pre className="text-sm text-gray-100 overflow-x-auto">
                        <code>{finding.code_fix_example}</code>
                      </pre>
                    </div>
                  </div>
                )}

                {finding.retest_required && (
                  <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
                    <div className="flex gap-3">
                      <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-orange-900 mb-1">Retest Required</h4>
                        {finding.retest_notes && (
                          <p className="text-sm text-orange-700 whitespace-pre-wrap">{finding.retest_notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'evidence' && (
              <div className="space-y-6">
                {finding.exploit_screenshots && finding.exploit_screenshots.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2 mb-3">
                      <Image className="h-4 w-4" />
                      Evidence Files ({finding.exploit_screenshots.length})
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      {finding.exploit_screenshots.map((url: string, idx: number) => {
                        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
                        const fileUrl = url.startsWith('http') ? url : `${apiUrl}/api/v1/files/serve/${url}`;
                        const isVideo = /\.(mp4|mov|avi|webm)$/i.test(url);
                        
                        return (
                          <div 
                            key={idx} 
                            className="rounded-xl border border-[#e6ddd4] overflow-hidden bg-black cursor-pointer hover:opacity-90 transition-opacity"
                            onClick={() => setLightboxMedia({ url: fileUrl, type: isVideo ? 'video' : 'image' })}
                          >
                            {isVideo ? (
                              <div className="relative w-full h-48 flex items-center justify-center bg-gray-900">
                                <Video className="h-12 w-12 text-white opacity-70" />
                                <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                                  Click to play
                                </div>
                              </div>
                            ) : (
                              <img 
                                src={fileUrl} 
                                alt={`Evidence ${idx + 1}`}
                                className="w-full h-48 object-cover"
                              />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {finding.exploit_video_url && (
                  <div>
                    <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2 mb-3">
                      <Video className="h-4 w-4" />
                      Video Demonstration
                    </label>
                    <div 
                      className="rounded-xl border border-[#e6ddd4] overflow-hidden bg-black cursor-pointer hover:opacity-90 transition-opacity"
                      onClick={() => {
                        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
                        const videoUrl = finding.exploit_video_url.startsWith('http') 
                          ? finding.exploit_video_url 
                          : `${apiUrl}/api/v1/files/serve/${finding.exploit_video_url}`;
                        setLightboxMedia({ url: videoUrl, type: 'video' });
                      }}
                    >
                      <div className="relative w-full h-64 flex items-center justify-center bg-gray-900">
                        <Video className="h-16 w-16 text-white opacity-70" />
                        <div className="absolute bottom-4 right-4 bg-black bg-opacity-70 text-white text-sm px-3 py-2 rounded">
                          Click to play video
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {!finding.exploit_screenshots?.length && !finding.exploit_video_url && (
                  <div className="text-center py-12">
                    <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
                      <Image className="h-8 w-8 text-[#8b8177]" />
                    </div>
                    <p className="text-sm text-[#6d6760]">No evidence files attached</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Lightbox Modal for Media */}
        {lightboxMedia && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-95 z-50 flex items-center justify-center p-4"
            onClick={() => setLightboxMedia(null)}
          >
            <button
              onClick={() => setLightboxMedia(null)}
              className="absolute top-4 right-4 text-white hover:text-gray-300 z-10 bg-black bg-opacity-50 rounded-full p-2"
            >
              <X className="h-8 w-8" />
            </button>
            
            <div 
              className="max-w-6xl max-h-[90vh] w-full"
              onClick={(e) => e.stopPropagation()}
            >
              {lightboxMedia.type === 'video' ? (
                <div className="text-center">
                  <video 
                    controls 
                    autoPlay
                    className="w-full max-h-[80vh] rounded-xl mb-4"
                    src={lightboxMedia.url}
                  >
                    Your browser does not support the video tag.
                  </video>
                  <a 
                    href={lightboxMedia.url}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Video
                  </a>
                </div>
              ) : (
                <div>
                  <img 
                    src={lightboxMedia.url} 
                    alt="Evidence"
                    className="w-full h-full max-h-[80vh] object-contain mb-4"
                  />
                  <div className="text-center">
                    <a 
                      href={lightboxMedia.url}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download Image
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </PortalShell>
  );
}
