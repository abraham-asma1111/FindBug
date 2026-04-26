'use client';

import { useState, useEffect } from 'react';
import SlidePanel from '@/components/ui/SlidePanel';
import Button from '@/components/ui/Button';
import TriageFeedbackPanel from './TriageFeedbackPanel';
import RetestSubmissionModal from './RetestSubmissionModal';
import RetestCompletionModal from './RetestCompletionModal';
import { api } from '@/lib/api';
import { 
  AlertCircle, CheckCircle, Clock, XCircle, 
  FileText, Code, Image, Video, Shield, 
  TrendingUp, Users, Database, Wrench, X, RefreshCw
} from 'lucide-react';

interface Finding {
  id: string;
  title: string;
  severity: string;
  status: string;
  vulnerability_type?: string;
  cwe_id?: string;
  owasp_category?: string;
  cvss_score?: number;
  cvss_vector?: string;
  affected_component?: string;
  affected_url?: string;
  description?: string;
  reproduction_steps?: string;
  proof_of_exploit?: string;
  exploit_code?: string;
  exploit_screenshots?: string[];
  exploit_video_url?: string;
  impact_description?: string;
  business_impact?: string;
  confidentiality_impact?: string;
  integrity_impact?: string;
  availability_impact?: string;
  affected_users?: string;
  data_at_risk?: string;
  remediation_recommendation?: string;
  remediation_priority?: string;
  remediation_effort?: string;
  remediation_steps?: string[];
  code_fix_example?: string;
  discovered_at?: string;
  validated?: boolean;
  retest_required?: boolean;
  retest_notes?: string;
  triage_notes?: string;
}

interface RetestRequest {
  id: string;
  finding_id: string;
  engagement_id: string;
  requested_by: string;
  requested_at: string;
  status: string;
  fix_description: string;
  fix_implemented_at?: string;
  fix_evidence?: string[];
  assigned_to?: string;
  assigned_at?: string;
  retest_started_at?: string;
  retest_completed_at?: string;
  retest_result?: string;
  retest_notes?: string;
  retest_evidence?: string[];
  is_eligible: boolean;
  eligibility_expires_at: string;
  eligibility_reason?: string;
  is_free_retest: boolean;
  retest_count: number;
  created_at: string;
  updated_at: string;
}

interface FindingDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  finding: Finding | null;
  onEdit?: () => void;
  onRetestSubmitted?: () => void;
}

const severityConfig = {
  Critical: { color: 'bg-red-100 text-red-700 border-red-200', icon: AlertCircle },
  High: { color: 'bg-orange-100 text-orange-700 border-orange-200', icon: TrendingUp },
  Medium: { color: 'bg-yellow-100 text-yellow-700 border-yellow-200', icon: AlertCircle },
  Low: { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Shield },
  Info: { color: 'bg-gray-100 text-gray-700 border-gray-200', icon: FileText },
};

const statusConfig = {
  SUBMITTED: { label: 'Submitted', color: 'bg-blue-100 text-blue-700', icon: Clock },
  TRIAGED: { label: 'Triaged', color: 'bg-purple-100 text-purple-700', icon: CheckCircle },
  VALIDATED: { label: 'Validated', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  REJECTED: { label: 'Rejected', color: 'bg-red-100 text-red-700', icon: XCircle },
  RETEST_REQUIRED: { label: 'Retest Required', color: 'bg-orange-100 text-orange-700', icon: AlertCircle },
  FIXED: { label: 'Fixed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
};

export default function FindingDetailModal({ isOpen, onClose, finding, onEdit, onRetestSubmitted }: FindingDetailModalProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showRetestModal, setShowRetestModal] = useState(false);
  const [lightboxMedia, setLightboxMedia] = useState<{url: string, type: 'image' | 'video'} | null>(null);
  const [retestRequests, setRetestRequests] = useState<RetestRequest[]>([]);
  const [loadingRetests, setLoadingRetests] = useState(false);
  const [selectedRetestForCompletion, setSelectedRetestForCompletion] = useState<RetestRequest | null>(null);

  // Fetch retest requests when modal opens
  useEffect(() => {
    if (isOpen && finding?.id) {
      fetchRetestRequests();
    }
  }, [isOpen, finding?.id]);

  const fetchRetestRequests = async () => {
    if (!finding?.id) return;
    
    setLoadingRetests(true);
    try {
      const response = await api.get<RetestRequest[]>(`/ptaas/findings/${finding.id}/retests`);
      setRetestRequests(response.data || []);
    } catch (error) {
      console.error('Failed to fetch retest requests:', error);
      setRetestRequests([]);
    } finally {
      setLoadingRetests(false);
    }
  };

  if (!finding) return null;

  const severityInfo = severityConfig[finding.severity as keyof typeof severityConfig] || severityConfig.Info;
  const statusInfo = statusConfig[finding.status as keyof typeof statusConfig] || statusConfig.SUBMITTED;
  const SeverityIcon = severityInfo.icon;
  const StatusIcon = statusInfo.icon;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'technical', label: 'Technical Details' },
    { id: 'impact', label: 'Impact Analysis' },
    { id: 'remediation', label: 'Remediation' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'retests', label: `Retest Requests${retestRequests.length > 0 ? ` (${retestRequests.length})` : ''}` },
  ];

  return (
    <SlidePanel isOpen={isOpen} onClose={onClose} title="Finding Details" width="full">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
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
            <h2 className="text-xl font-semibold text-[#2d2a26]">{finding.title}</h2>
            {finding.discovered_at && (
              <p className="text-sm text-[#6d6760] mt-1">
                Discovered {new Date(finding.discovered_at).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            {finding.retest_required && (
              <Button 
                size="sm" 
                onClick={() => setShowRetestModal(true)}
                className="bg-orange-600 hover:bg-orange-700"
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Submit Retest
              </Button>
            )}
            {onEdit && (
              <Button size="sm" variant="outline" onClick={onEdit}>
                Edit
              </Button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-[#faf6f1] rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-[#6d6760]" />
            </button>
          </div>
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
        <div className="max-h-[60vh] overflow-y-auto">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Triage Feedback */}
              <TriageFeedbackPanel 
                feedback={{
                  validated: finding.validated,
                  retest_required: finding.retest_required,
                  retest_notes: finding.retest_notes,
                  triage_notes: finding.triage_notes,
                  status: finding.status
                }}
              />

              {/* Quick Info */}
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

              {/* Description */}
              {finding.description && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Description
                  </label>
                  <div className="mt-2 p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                    <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.description}</p>
                  </div>
                </div>
              )}

              {/* Reproduction Steps */}
              {finding.reproduction_steps && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Code className="h-4 w-4" />
                    Reproduction Steps
                  </label>
                  <div className="mt-2 p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                    <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.reproduction_steps}</p>
                  </div>
                </div>
              )}

              {/* Triage Notes */}
              {finding.triage_notes && (
                <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                  <div className="flex gap-3">
                    <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-blue-900 mb-1">Additional Triage Notes</h4>
                      <p className="text-sm text-blue-700 whitespace-pre-wrap">{finding.triage_notes}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'technical' && (
            <div className="space-y-6">
              {/* CVSS Details */}
              {finding.cvss_vector && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177]">CVSS Vector</label>
                  <div className="mt-2 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4] font-mono text-sm">
                    {finding.cvss_vector}
                  </div>
                </div>
              )}

              {/* Affected URL */}
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

              {/* Proof of Exploit */}
              {finding.proof_of_exploit && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177]">Proof of Exploit</label>
                  <div className="mt-2 p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                    <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.proof_of_exploit}</p>
                  </div>
                </div>
              )}

              {/* Exploit Code */}
              {finding.exploit_code && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Code className="h-4 w-4" />
                    Exploit Code
                  </label>
                  <div className="mt-2 p-4 rounded-xl bg-gray-900 border border-gray-700">
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
              {/* Impact Description */}
              {finding.impact_description && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177]">Impact Description</label>
                  <div className="mt-2 p-4 rounded-xl bg-[#faf6f1] border border-[#e6ddd4]">
                    <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{finding.impact_description}</p>
                  </div>
                </div>
              )}

              {/* Business Impact */}
              {finding.business_impact && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177]">Business Impact</label>
                  <div className="mt-2 p-4 rounded-xl bg-orange-50 border border-orange-200">
                    <p className="text-sm text-orange-900 whitespace-pre-wrap">{finding.business_impact}</p>
                  </div>
                </div>
              )}

              {/* CIA Triad */}
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

              {/* Recommendation */}
              {finding.remediation_recommendation && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Wrench className="h-4 w-4" />
                    Remediation Recommendation
                  </label>
                  <div className="mt-2 p-4 rounded-xl bg-green-50 border border-green-200">
                    <p className="text-sm text-green-900 whitespace-pre-wrap">{finding.remediation_recommendation}</p>
                  </div>
                </div>
              )}

              {/* Remediation Steps */}
              {finding.remediation_steps && finding.remediation_steps.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177]">Remediation Steps</label>
                  <div className="mt-2 space-y-2">
                    {finding.remediation_steps.map((step, idx) => (
                      <div key={idx} className="flex gap-3 p-3 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold flex-shrink-0">
                          {idx + 1}
                        </div>
                        <p className="text-sm text-[#2d2a26]">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Code Fix Example */}
              {finding.code_fix_example && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Code className="h-4 w-4" />
                    Code Fix Example
                  </label>
                  <div className="mt-2 p-4 rounded-xl bg-gray-900 border border-gray-700">
                    <pre className="text-sm text-gray-100 overflow-x-auto">
                      <code>{finding.code_fix_example}</code>
                    </pre>
                  </div>
                </div>
              )}

              {/* Retest Info */}
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
              {/* Evidence Files (Images and Videos) */}
              {finding.exploit_screenshots && finding.exploit_screenshots.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Image className="h-4 w-4" />
                    Evidence Files ({finding.exploit_screenshots.length})
                  </label>
                  <div className="mt-2 grid grid-cols-2 gap-4">
                    {finding.exploit_screenshots.map((url, idx) => {
                      // Convert storage key to backend proxy URL
                      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
                      const fileUrl = url.startsWith('http') ? url : `${apiUrl}/api/v1/files/serve/${url}`;
                      
                      // Detect if file is a video based on extension
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

              {/* Video URL (separate field) */}
              {finding.exploit_video_url && (
                <div>
                  <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                    <Video className="h-4 w-4" />
                    Video Demonstration
                  </label>
                  <div 
                    className="mt-2 rounded-xl border border-[#e6ddd4] overflow-hidden bg-black cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => {
                      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
                      const videoUrl = finding.exploit_video_url!.startsWith('http') 
                        ? finding.exploit_video_url! 
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

          {activeTab === 'retests' && (
            <div className="space-y-6">
              {loadingRetests ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-sm text-[#6d6760]">Loading retest requests...</p>
                </div>
              ) : retestRequests.length > 0 ? (
                <div className="space-y-4">
                  {retestRequests.map((retest) => {
                    const statusColors = {
                      PENDING: 'bg-yellow-100 text-yellow-700 border-yellow-200',
                      APPROVED: 'bg-blue-100 text-blue-700 border-blue-200',
                      IN_PROGRESS: 'bg-purple-100 text-purple-700 border-purple-200',
                      COMPLETED: 'bg-green-100 text-green-700 border-green-200',
                      REJECTED: 'bg-red-100 text-red-700 border-red-200',
                    };

                    const resultColors = {
                      FIXED: 'bg-green-100 text-green-700',
                      NOT_FIXED: 'bg-red-100 text-red-700',
                      PARTIALLY_FIXED: 'bg-orange-100 text-orange-700',
                      NEW_ISSUE: 'bg-purple-100 text-purple-700',
                    };

                    return (
                      <div 
                        key={retest.id} 
                        className="rounded-xl border border-[#e6ddd4] bg-white p-6 space-y-4"
                      >
                        {/* Header */}
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <RefreshCw className="h-5 w-5 text-blue-600" />
                            <div>
                              <div className="flex items-center gap-2">
                                <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium border ${statusColors[retest.status as keyof typeof statusColors] || statusColors.PENDING}`}>
                                  {retest.status.replace('_', ' ')}
                                </span>
                                {retest.is_free_retest && (
                                  <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium bg-green-100 text-green-700">
                                    Free Retest
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-[#8b8177] mt-1">
                                Requested {new Date(retest.requested_at).toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-[#8b8177]">Retest #{retest.retest_count}</p>
                            {retest.eligibility_expires_at && (
                              <p className="text-xs text-orange-600 mt-1">
                                Expires {new Date(retest.eligibility_expires_at).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Fix Description */}
                        <div>
                          <label className="text-sm font-medium text-[#8b8177]">Fix Description from Organization</label>
                          <div className="mt-2 p-4 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                            <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{retest.fix_description}</p>
                          </div>
                        </div>

                        {/* Fix Implementation Date */}
                        {retest.fix_implemented_at && (
                          <div>
                            <label className="text-sm font-medium text-[#8b8177]">Fix Implemented</label>
                            <p className="mt-1 text-sm text-[#2d2a26]">
                              {new Date(retest.fix_implemented_at).toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric' 
                              })}
                            </p>
                          </div>
                        )}

                        {/* Fix Evidence */}
                        {retest.fix_evidence && retest.fix_evidence.length > 0 && (
                          <div>
                            <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Fix Evidence ({retest.fix_evidence.length})
                            </label>
                            <div className="mt-2 space-y-2">
                              {retest.fix_evidence.map((url, idx) => (
                                <a
                                  key={idx}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="block p-3 rounded-lg bg-blue-50 border border-blue-200 hover:bg-blue-100 transition-colors"
                                >
                                  <p className="text-sm text-blue-700 break-all">{url}</p>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Retest Result */}
                        {retest.retest_result && (
                          <div>
                            <label className="text-sm font-medium text-[#8b8177]">Retest Result</label>
                            <div className="mt-2">
                              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${resultColors[retest.retest_result as keyof typeof resultColors]}`}>
                                {retest.retest_result.replace('_', ' ')}
                              </span>
                            </div>
                          </div>
                        )}

                        {/* Retest Notes */}
                        {retest.retest_notes && (
                          <div>
                            <label className="text-sm font-medium text-[#8b8177]">Retest Notes</label>
                            <div className="mt-2 p-4 rounded-lg bg-[#faf6f1] border border-[#e6ddd4]">
                              <p className="text-sm text-[#2d2a26] whitespace-pre-wrap">{retest.retest_notes}</p>
                            </div>
                          </div>
                        )}

                        {/* Retest Evidence */}
                        {retest.retest_evidence && retest.retest_evidence.length > 0 && (
                          <div>
                            <label className="text-sm font-medium text-[#8b8177] flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Retest Evidence ({retest.retest_evidence.length})
                            </label>
                            <div className="mt-2 space-y-2">
                              {retest.retest_evidence.map((url, idx) => (
                                <a
                                  key={idx}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="block p-3 rounded-lg bg-green-50 border border-green-200 hover:bg-green-100 transition-colors"
                                >
                                  <p className="text-sm text-green-700 break-all">{url}</p>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Timeline */}
                        <div className="pt-4 border-t border-[#e6ddd4]">
                          <label className="text-sm font-medium text-[#8b8177] mb-3 block">Timeline</label>
                          <div className="space-y-2 text-xs text-[#6d6760]">
                            <div className="flex items-center gap-2">
                              <Clock className="h-3.5 w-3.5" />
                              <span>Requested: {new Date(retest.requested_at).toLocaleString()}</span>
                            </div>
                            {retest.assigned_at && (
                              <div className="flex items-center gap-2">
                                <CheckCircle className="h-3.5 w-3.5 text-blue-600" />
                                <span>Assigned: {new Date(retest.assigned_at).toLocaleString()}</span>
                              </div>
                            )}
                            {retest.retest_started_at && (
                              <div className="flex items-center gap-2">
                                <RefreshCw className="h-3.5 w-3.5 text-purple-600" />
                                <span>Started: {new Date(retest.retest_started_at).toLocaleString()}</span>
                              </div>
                            )}
                            {retest.retest_completed_at && (
                              <div className="flex items-center gap-2">
                                <CheckCircle className="h-3.5 w-3.5 text-green-600" />
                                <span>Completed: {new Date(retest.retest_completed_at).toLocaleString()}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Action Button for Pending/Approved Retests */}
                        {(retest.status === 'PENDING' || retest.status === 'APPROVED' || retest.status === 'IN_PROGRESS') && !retest.retest_completed_at && (
                          <div className="pt-4 border-t border-[#e6ddd4]">
                            <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                              <div className="flex items-start gap-3">
                                <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                  <h4 className="font-semibold text-blue-900 mb-1">Action Required</h4>
                                  <p className="text-sm text-blue-700 mb-3">
                                    The organization has requested a retest for this finding. Please review the fix description and evidence provided, then complete your retest.
                                  </p>
                                  <Button 
                                    size="sm" 
                                    className="bg-blue-600 hover:bg-blue-700"
                                    onClick={() => setSelectedRetestForCompletion(retest)}
                                  >
                                    <RefreshCw className="h-4 w-4 mr-1" />
                                    Complete Retest
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
                    <RefreshCw className="h-8 w-8 text-[#8b8177]" />
                  </div>
                  <p className="text-sm font-medium text-[#2d2a26] mb-1">No Retest Requests</p>
                  <p className="text-sm text-[#6d6760]">
                    The organization hasn't requested any retests for this finding yet.
                  </p>
                </div>
              )}
            </div>
          )}

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
      </div>

      {/* Retest Submission Modal */}
      <RetestSubmissionModal
        isOpen={showRetestModal}
        onClose={() => setShowRetestModal(false)}
        findingId={finding.id}
        findingTitle={finding.title}
        retestNotes={finding.retest_notes}
        onSuccess={() => {
          setShowRetestModal(false);
          if (onRetestSubmitted) {
            onRetestSubmitted();
          }
        }}
      />

      {/* Retest Completion Modal */}
      {selectedRetestForCompletion && (
        <RetestCompletionModal
          isOpen={!!selectedRetestForCompletion}
          onClose={() => setSelectedRetestForCompletion(null)}
          retestId={selectedRetestForCompletion.id}
          findingTitle={finding.title}
          fixDescription={selectedRetestForCompletion.fix_description}
          onSuccess={() => {
            setSelectedRetestForCompletion(null);
            fetchRetestRequests(); // Refresh the retest list
            if (onRetestSubmitted) {
              onRetestSubmitted();
            }
          }}
        />
      )}
    </SlidePanel>
  );
}
