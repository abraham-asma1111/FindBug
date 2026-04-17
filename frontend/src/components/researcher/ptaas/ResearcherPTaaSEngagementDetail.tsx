'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import api from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { 
  Calendar, Users, AlertCircle, CheckCircle, Clock, 
  Target, TrendingUp, Flag
} from 'lucide-react';

interface PTaaSEngagement {
  id: string;
  name: string;
  description: string;
  status: string;
  testing_methodology: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  scope: any;
  deliverables: any;
  team_size: number;
  assigned_researchers: string[];
  pricing_model: string;
  base_price: number;
  compliance_requirements: string[];
  organization_id: string;
  created_at: string;
}

interface Finding {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

interface ResearcherPTaaSEngagementDetailProps {
  engagementId: string;
}

const statusConfig = {
  DRAFT: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  IN_PROGRESS: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
  COMPLETED: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  CANCELLED: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function ResearcherPTaaSEngagementDetail({ engagementId }: ResearcherPTaaSEngagementDetailProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [showFindingModal, setShowFindingModal] = useState(false);
  const [acceptedNDA, setAcceptedNDA] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Finding form state
  const [findingForm, setFindingForm] = useState({
    title: '',
    severity: 'Medium',
    description: '',
    reproduction_steps: '',
    impact_analysis: '',
    remediation: '',
    proof_of_exploit: ''
  });

  const { data: engagement, isLoading, error, refetch } = useApiQuery<PTaaSEngagement>({
    endpoint: `/ptaas/researcher/engagements/${engagementId}`
  });

  const { data: findings } = useApiQuery<Finding[] | null>({
    endpoint: `/ptaas/engagements/${engagementId}/findings`
  });

  const handleAcceptEngagement = async () => {
    if (!acceptedNDA) {
      alert('Please accept the NDA and testing rules');
      return;
    }

    setIsAccepting(true);
    try {
      await api.post(`/ptaas/researcher/engagements/${engagementId}/accept`, {});
      alert('Engagement accepted successfully!');
      setShowAcceptModal(false);
      refetch();
    } catch (error: any) {
      alert(error.message || 'Failed to accept engagement');
    } finally {
      setIsAccepting(false);
    }
  };

  const handleSubmitFinding = async () => {
    setIsSubmitting(true);
    try {
      await api.post(`/ptaas/findings`, {
        engagement_id: engagementId,
        ...findingForm
      });
      alert('Finding submitted successfully!');
      setShowFindingModal(false);
      setFindingForm({
        title: '',
        severity: 'Medium',
        description: '',
        reproduction_steps: '',
        impact_analysis: '',
        remediation: '',
        proof_of_exploit: ''
      });
    } catch (error: any) {
      alert(error.message || 'Failed to submit finding');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6 animate-pulse">
          <div className="h-64 bg-[#faf6f1] rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !engagement) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Failed to load engagement</h3>
            <p className="text-sm text-red-700">{error?.message || 'Engagement not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.DRAFT;
  const StatusIcon = statusInfo.icon;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'scope', label: 'Scope & Assets' },
    { id: 'testing', label: 'Testing' },
    { id: 'findings', label: `Findings (${findings?.length || 0})` },
    { id: 'team', label: 'Team' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-[#2d2a26]">{engagement.name}</h1>
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
                <StatusIcon className="h-3.5 w-3.5" />
                {statusInfo.label}
              </span>
            </div>
            <p className="mt-2 text-sm text-[#6d6760]">{engagement.description}</p>
          </div>
          {engagement.status === 'DRAFT' && (
            <Button size="sm" onClick={() => setShowAcceptModal(true)}>
              <CheckCircle className="h-4 w-4 mr-1" />
              Accept Engagement
            </Button>
          )}
        </div>

        {/* Quick Stats */}
        <div className="mt-6 grid grid-cols-4 gap-4 border-t border-[#e6ddd4] pt-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Methodology</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.testing_methodology}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-50 p-2">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Team Size</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.team_size}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-orange-50 p-2">
              <Flag className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Findings</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{findings?.length || 0}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-50 p-2">
              <Calendar className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Duration</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.duration_days} days</p>
            </div>
          </div>
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
      <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6">
        {activeTab === 'overview' && <OverviewTab engagement={engagement} />}
        {activeTab === 'scope' && <ScopeTab engagement={engagement} />}
        {activeTab === 'testing' && <TestingTab engagement={engagement} />}
        {activeTab === 'findings' && <FindingsTab findings={findings} onSubmit={() => setShowFindingModal(true)} engagementId={engagementId} />}
        {activeTab === 'team' && <TeamTab engagement={engagement} />}
      </div>

      {/* Accept Engagement Modal */}
      <Modal
        isOpen={showAcceptModal}
        onClose={() => setShowAcceptModal(false)}
        title="Accept Engagement"
      >
        <div className="space-y-4">
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">Non-Disclosure Agreement (NDA)</h4>
                <p className="text-sm text-blue-700 mb-3">
                  By accepting this engagement, you agree to:
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Keep all engagement details confidential</li>
                  <li>• Not disclose any vulnerabilities publicly</li>
                  <li>• Follow the defined scope and testing rules</li>
                  <li>• Report findings only through the platform</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={acceptedNDA}
              onChange={(e) => setAcceptedNDA(e.target.checked)}
              className="mt-1"
            />
            <label className="text-sm text-[#2d2a26]">
              I have read and agree to the NDA and testing rules
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setShowAcceptModal(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleAcceptEngagement}
              disabled={!acceptedNDA}
              isLoading={isAccepting}
              className="flex-1"
            >
              Accept Engagement
            </Button>
          </div>
        </div>
      </Modal>

      {/* Submit Finding Modal */}
      <Modal
        isOpen={showFindingModal}
        onClose={() => setShowFindingModal(false)}
        title="Submit Finding"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Title
            </label>
            <input
              type="text"
              value={findingForm.title}
              onChange={(e) => setFindingForm({ ...findingForm, title: e.target.value })}
              className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Brief title of the vulnerability"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Severity
            </label>
            <Select
              value={findingForm.severity}
              onChange={(e) => setFindingForm({ ...findingForm, severity: e.target.value })}
              options={[
                { value: 'Critical', label: 'Critical' },
                { value: 'High', label: 'High' },
                { value: 'Medium', label: 'Medium' },
                { value: 'Low', label: 'Low' },
                { value: 'Info', label: 'Info' },
              ]}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Description
            </label>
            <Textarea
              value={findingForm.description}
              onChange={(e) => setFindingForm({ ...findingForm, description: e.target.value })}
              rows={3}
              placeholder="Detailed description of the vulnerability"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Steps to Reproduce
            </label>
            <Textarea
              value={findingForm.reproduction_steps}
              onChange={(e) => setFindingForm({ ...findingForm, reproduction_steps: e.target.value })}
              rows={3}
              placeholder="Step-by-step reproduction instructions"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">
              Impact Analysis
            </label>
            <Textarea
              value={findingForm.impact_analysis}
              onChange={(e) => setFindingForm({ ...findingForm, impact_analysis: e.target.value })}
              rows={2}
              placeholder="Business and technical impact"
            />
          </div>

          <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
            <Button variant="outline" onClick={() => setShowFindingModal(false)} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleSubmitFinding}
              disabled={isSubmitting || !findingForm.title}
              isLoading={isSubmitting}
              className="flex-1"
            >
              Submit Finding
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// Overview Tab
function OverviewTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Engagement Details</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Start Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">
                {new Date(engagement.start_date).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-[#8b8177]">End Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">
                {new Date(engagement.end_date).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
          </div>
          {engagement.compliance_requirements && engagement.compliance_requirements.length > 0 && (
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Compliance Requirements</label>
              <ul className="mt-2 space-y-1">
                {engagement.compliance_requirements.map((req, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-[#2d2a26]">
                    <span className="text-blue-500">•</span>
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Scope Tab
function ScopeTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26]">Scope & Target Assets</h3>
      <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
        <pre className="text-sm text-[#2d2a26] whitespace-pre-wrap">
          {engagement.scope ? JSON.stringify(engagement.scope, null, 2) : 'No scope details available'}
        </pre>
      </div>
    </div>
  );
}

// Testing Tab
function TestingTab({ engagement }: { engagement: PTaaSEngagement }) {
  const methodologyPhases: Record<string, string[]> = {
    OWASP: ['Information Gathering', 'Configuration Testing', 'Identity Management', 'Authentication', 'Authorization', 'Session Management', 'Input Validation', 'Error Handling', 'Cryptography', 'Business Logic', 'Client-Side Testing'],
    PTES: ['Pre-engagement Interactions', 'Intelligence Gathering', 'Threat Modeling', 'Vulnerability Analysis', 'Exploitation', 'Post Exploitation', 'Reporting'],
    NIST: ['Planning', 'Discovery', 'Attack & Penetration', 'Reporting', 'Compliance Validation'],
  };

  const phases = methodologyPhases[engagement.testing_methodology] || [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">
          Testing Methodology: {engagement.testing_methodology}
        </h3>
        <div className="space-y-2">
          {phases.map((phase, idx) => (
            <div key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-[#e6ddd4] bg-[#faf6f1]">
              <input type="checkbox" className="w-4 h-4" />
              <span className="text-sm text-[#2d2a26]">{phase}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Findings Tab
function FindingsTab({ findings, onSubmit, engagementId }: { findings: Finding[] | null | undefined; onSubmit: () => void; engagementId: string }) {
  const router = useRouter();
  
  if (!findings || findings.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-16 w-16 rounded-full bg-[#faf6f1] flex items-center justify-center mb-4">
          <Flag className="h-8 w-8 text-[#8b8177]" />
        </div>
        <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">No findings submitted yet</h3>
        <p className="text-sm text-[#6d6760] mb-6">
          Start testing and submit your first security finding
        </p>
        <Button onClick={onSubmit}>
          <Flag className="h-4 w-4 mr-1" />
          Submit Finding
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Submitted Findings</h3>
        <Button size="sm" onClick={onSubmit}>
          <Flag className="h-4 w-4 mr-1" />
          Submit Finding
        </Button>
      </div>
      <div className="space-y-3">
        {findings.map((finding) => (
          <div 
            key={finding.id} 
            className="p-4 rounded-xl border border-[#e6ddd4] bg-[#faf6f1] hover:bg-white cursor-pointer transition-colors"
            onClick={() => router.push(`/researcher/programs/ptaas/${engagementId}/findings/${finding.id}`)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-medium text-[#2d2a26] mb-1">{finding.title}</h4>
                <p className="text-sm text-[#6d6760]">
                  Submitted {new Date(finding.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex gap-2">
                <span className="px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-700">
                  {finding.severity}
                </span>
                <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700">
                  {finding.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Team Tab
function TeamTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26]">Team Members</h3>
      <p className="text-sm text-[#6d6760]">
        {engagement.team_size} team member(s) assigned to this engagement
      </p>
      <div className="space-y-3">
        {engagement.assigned_researchers.map((researcherId, idx) => (
          <div key={idx} className="p-4 rounded-xl border border-[#e6ddd4] bg-[#faf6f1]">
            <p className="text-sm font-medium text-[#2d2a26]">Researcher {idx + 1}</p>
            <p className="text-xs text-[#8b8177] mt-1">{researcherId}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
