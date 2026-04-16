'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import SimpleTabs from '@/components/ui/SimpleTabs';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import { useToast } from '@/components/ui/Toast';
import { 
  Calendar, Users, AlertCircle, CheckCircle, Clock, 
  FileText, Target, TrendingUp, MessageSquare, Flag, Edit, Play, UserPlus 
} from 'lucide-react';
import PTaaSKPIMetrics from './dashboard/PTaaSKPIMetrics';
import PTaaSSeverityChart from './dashboard/PTaaSSeverityChart';
import PTaaSAssetCoverage from './dashboard/PTaaSAssetCoverage';
import PTaaSActivityFeed from './dashboard/PTaaSActivityFeed';
import PTaaSFindingAssignModal from './findings/PTaaSFindingAssignModal';
import PTaaSFindingStatusModal from './findings/PTaaSFindingStatusModal';
import PTaaSResearcherAssignModal from './PTaaSResearcherAssignModal';

interface PTaaSEngagement {
  id: string;
  name: string;
  description: string;
  scope: {
    in_scope_targets?: string[];
    out_of_scope_targets?: string[];
    testing_methodology?: string;
    custom_methodology_details?: string;
  };
  methodology: string;
  start_date: string;
  end_date: string;
  status: string;
  budget: number;
  assigned_researchers: string[];
  findings_count: number;
  created_at: string;
}

interface PTaaSEngagementDetailProps {
  engagement: PTaaSEngagement;
}

const statusConfig = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-700', icon: Clock },
  active: { label: 'Active', color: 'bg-blue-100 text-blue-700', icon: CheckCircle },
  in_progress: { label: 'In Progress', color: 'bg-yellow-100 text-yellow-700', icon: TrendingUp },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: AlertCircle },
};

export default function PTaaSEngagementDetail({ engagement }: PTaaSEngagementDetailProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showLaunchModal, setShowLaunchModal] = useState(false);
  const { showToast } = useToast();

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'findings', label: 'Findings', count: engagement.findings_count },
    { id: 'deliverables', label: 'Deliverables' },
    { id: 'team', label: 'Team', count: engagement.assigned_researchers?.length || 0 },
    { id: 'activity', label: 'Activity' },
  ];

  const statusInfo = statusConfig[engagement.status as keyof typeof statusConfig] || statusConfig.draft;
  const StatusIcon = statusInfo.icon;

  // Launch engagement mutation
  const { mutate: launchEngagement, isLoading: isLaunching } = useApiMutation(
    `/ptaas/engagements/${engagement.id}/start`,
    'POST',
    {
      onSuccess: () => {
        showToast('Engagement launched successfully!', 'success');
        setShowLaunchModal(false);
        window.location.reload(); // Refresh to show updated status
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to launch engagement', 'error');
      },
    }
  );

  // Complete engagement mutation
  const { mutate: completeEngagement, isLoading: isCompleting } = useApiMutation(
    `/ptaas/engagements/${engagement.id}/complete`,
    'POST',
    {
      onSuccess: () => {
        showToast('Engagement marked as complete!', 'success');
        window.location.reload();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to complete engagement', 'error');
      },
    }
  );

  const handleLaunch = () => {
    launchEngagement({});
  };

  const handleComplete = () => {
    if (confirm('Are you sure you want to mark this engagement as complete?')) {
      completeEngagement({});
    }
  };

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
          <div className="flex gap-2">
            {engagement.status === 'draft' && (
              <>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowEditModal(true)}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button 
                  size="sm"
                  onClick={() => setShowLaunchModal(true)}
                  isLoading={isLaunching}
                >
                  <Play className="h-4 w-4 mr-1" />
                  Launch Engagement
                </Button>
              </>
            )}
            {(engagement.status === 'active' || engagement.status === 'in_progress') && (
              <>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowAssignModal(true)}
                >
                  <UserPlus className="h-4 w-4 mr-1" />
                  Assign Researchers
                </Button>
                <Button 
                  size="sm"
                  onClick={handleComplete}
                  isLoading={isCompleting}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Mark Complete
                </Button>
              </>
            )}
            {engagement.status === 'completed' && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open(`/organization/services/ptaas/${engagement.id}/report`, '_blank')}
              >
                <FileText className="h-4 w-4 mr-1" />
                View Final Report
              </Button>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-6 grid grid-cols-4 gap-4 border-t border-[#e6ddd4] pt-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Methodology</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.methodology}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-50 p-2">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Researchers</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.assigned_researchers?.length || 0}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-orange-50 p-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Findings</p>
              <p className="text-sm font-semibold text-[#2d2a26]">{engagement.findings_count || 0}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-50 p-2">
              <Calendar className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-[#8b8177]">Timeline</p>
              <p className="text-sm font-semibold text-[#2d2a26]">
                {Math.ceil((new Date(engagement.end_date).getTime() - new Date(engagement.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <SimpleTabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Content */}
      <div className="rounded-2xl border border-[#e6ddd4] bg-white p-6">
        {activeTab === 'overview' && <OverviewTab engagement={engagement} />}
        {activeTab === 'dashboard' && <DashboardTab engagementId={engagement.id} />}
        {activeTab === 'findings' && <FindingsTab engagementId={engagement.id} />}
        {activeTab === 'deliverables' && <DeliverablesTab engagementId={engagement.id} />}
        {activeTab === 'team' && <TeamTab engagementId={engagement.id} />}
        {activeTab === 'activity' && <ActivityTab engagementId={engagement.id} />}
      </div>

      {/* Launch Confirmation Modal */}
      {showLaunchModal && (
        <Modal
          isOpen={showLaunchModal}
          onClose={() => setShowLaunchModal(false)}
          title="Launch Engagement"
        >
          <div className="space-y-4">
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">Ready to launch?</h4>
                  <p className="text-sm text-blue-700">
                    Once launched, assigned researchers will be notified and can begin testing. 
                    Make sure you've reviewed the scope, assigned researchers, and configured all settings.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between py-2 border-b border-[#e6ddd4]">
                <span className="text-[#6d6760]">Assigned Researchers</span>
                <span className="font-semibold text-[#2d2a26]">{engagement.assigned_researchers?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-[#e6ddd4]">
                <span className="text-[#6d6760]">Start Date</span>
                <span className="font-semibold text-[#2d2a26]">
                  {new Date(engagement.start_date).toLocaleDateString()}
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-[#6d6760]">End Date</span>
                <span className="font-semibold text-[#2d2a26]">
                  {new Date(engagement.end_date).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => setShowLaunchModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleLaunch}
                isLoading={isLaunching}
                className="flex-1"
              >
                Launch Engagement
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Edit Modal Placeholder */}
      {showEditModal && (
        <Modal
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          title="Edit Engagement"
        >
          <div className="text-center py-8">
            <p className="text-sm text-[#6d6760]">Edit functionality coming soon...</p>
            <Button className="mt-4" onClick={() => setShowEditModal(false)}>
              Close
            </Button>
          </div>
        </Modal>
      )}

      {/* Assign Researchers Modal */}
      {showAssignModal && (
        <PTaaSResearcherAssignModal
          isOpen={showAssignModal}
          onClose={() => setShowAssignModal(false)}
          engagementId={engagement.id}
          engagementName={engagement.name}
          onSuccess={() => window.location.reload()}
        />
      )}
    </div>
  );
}

// Overview Tab
function OverviewTab({ engagement }: { engagement: PTaaSEngagement }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-[#2d2a26]">Engagement Details</h3>
        <div className="mt-4 space-y-4">
          <div>
            <label className="text-sm font-medium text-[#8b8177]">Scope</label>
            <div className="mt-1 text-sm text-[#2d2a26] space-y-1">
              {engagement.scope?.in_scope_targets && engagement.scope.in_scope_targets.length > 0 && (
                <div>
                  <span className="font-medium">In-Scope: </span>
                  {engagement.scope.in_scope_targets.join(', ')}
                </div>
              )}
              {engagement.scope?.out_of_scope_targets && engagement.scope.out_of_scope_targets.length > 0 && (
                <div>
                  <span className="font-medium">Out-of-Scope: </span>
                  {engagement.scope.out_of_scope_targets.join(', ')}
                </div>
              )}
              {engagement.scope?.testing_methodology && (
                <div>
                  <span className="font-medium">Methodology: </span>
                  {engagement.scope.testing_methodology}
                </div>
              )}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Start Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">{new Date(engagement.start_date).toLocaleDateString()}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-[#8b8177]">End Date</label>
              <p className="mt-1 text-sm text-[#2d2a26]">{new Date(engagement.end_date).toLocaleDateString()}</p>
            </div>
          </div>
          {engagement.budget > 0 && (
            <div>
              <label className="text-sm font-medium text-[#8b8177]">Budget</label>
              <p className="mt-1 text-sm text-[#2d2a26]">{engagement.budget.toLocaleString()} ETB</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Dashboard Tab
function DashboardTab({ engagementId }: { engagementId: string }) {
  const { data: dashboard, isLoading, error, refetch } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}/dashboard`,
    queryKey: ['ptaas-dashboard', engagementId],
  });

  const { mutate: initializePhases, isLoading: isInitializing } = useApiMutation(
    `/ptaas/engagements/${engagementId}/initialize-phases`,
    'POST',
    {
      onSuccess: () => {
        refetch();
      },
    }
  );

  if (isLoading) {
    return <div className="text-center py-8 text-sm text-[#8b8177]">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Failed to load dashboard. Please try again.</p>
      </div>
    );
  }

  // If no phases initialized yet
  if (!dashboard || !dashboard.phases || dashboard.phases.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <Target className="mx-auto h-12 w-12 text-[#8b8177]" />
          <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">Initialize Testing Phases</h3>
          <p className="mt-2 text-sm text-[#6d6760] max-w-md mx-auto">
            Set up the testing phases to track progress through reconnaissance, scanning, exploitation, and reporting.
          </p>
          <Button
            className="mt-6"
            onClick={() => initializePhases({})}
            isLoading={isInitializing}
          >
            Initialize Phases
          </Button>
        </div>
      </div>
    );
  }

  const phases = dashboard.phases || [];
  const kpiMetrics = dashboard.kpi_metrics || {
    active_researchers: 0,
    total_findings: 0,
    findings_by_severity: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
    asset_coverage: { tested: 0, total: 0, percentage: 0, in_scope_assets: [], tested_assets: [] },
    overall_progress: 0
  };
  const collaboration = dashboard.collaboration || [];
  const completedPhases = phases.filter((p: any) => p.status === 'completed').length;
  const progressPercentage = phases.length > 0 ? (completedPhases / phases.length) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* KPI Metrics */}
      <PTaaSKPIMetrics metrics={kpiMetrics} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PTaaSSeverityChart findings={kpiMetrics.findings_by_severity} />
        <PTaaSAssetCoverage coverage={kpiMetrics.asset_coverage} />
      </div>

      {/* Activity Feed */}
      <PTaaSActivityFeed activities={collaboration} />

      {/* Progress Overview */}
      <div className="rounded-xl border border-[#e6ddd4] bg-gradient-to-br from-blue-50 to-white p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-[#2d2a26]">Testing Progress</h3>
            <p className="text-sm text-[#6d6760]">
              {completedPhases} of {phases.length} phases completed
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">{Math.round(progressPercentage)}%</div>
            <div className="text-xs text-[#8b8177]">Complete</div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="h-3 bg-[#e6ddd4] rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Phases List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Testing Phases</h3>
        {phases.map((phase: any, index: number) => (
          <PhaseCard key={phase.id} phase={phase} index={index} onRefresh={refetch} />
        ))}
      </div>
    </div>
  );
}

// Phase Card Component
function PhaseCard({ phase, index, onRefresh }: { phase: any; index: number; onRefresh: () => void }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { showToast } = useToast();

  const statusConfig = {
    NOT_STARTED: { label: 'Not Started', color: 'bg-gray-100 text-gray-700', icon: Clock },
    pending: { label: 'Pending', color: 'bg-gray-100 text-gray-700', icon: Clock },
    IN_PROGRESS: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
    in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
    COMPLETED: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
    completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
    BLOCKED: { label: 'Blocked', color: 'bg-red-100 text-red-700', icon: AlertCircle },
  };

  const statusInfo = statusConfig[phase.status as keyof typeof statusConfig] || statusConfig.NOT_STARTED;
  const StatusIcon = statusInfo.icon;

  // Start phase mutation
  const { mutate: startPhase, isLoading: isStarting } = useApiMutation(
    `/ptaas/phases/${phase.id}`,
    'PATCH',
    {
      onSuccess: () => {
        showToast('Phase started successfully!', 'success');
        onRefresh();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to start phase', 'error');
      },
    }
  );

  // Complete phase mutation
  const { mutate: completePhase, isLoading: isCompleting } = useApiMutation(
    `/ptaas/phases/${phase.id}`,
    'PATCH',
    {
      onSuccess: () => {
        showToast('Phase completed successfully!', 'success');
        onRefresh();
      },
      onError: (error: Error) => {
        showToast(error.message || 'Failed to complete phase', 'error');
      },
    }
  );

  const handleStartPhase = () => {
    startPhase({ status: 'IN_PROGRESS' });
  };

  const handleCompletePhase = () => {
    completePhase({ status: 'COMPLETED', progress_percentage: 100 });
  };
  
  const isNotStarted = phase.status === 'NOT_STARTED' || phase.status === 'pending';
  const isInProgress = phase.status === 'IN_PROGRESS' || phase.status === 'in_progress';
  const isCompleted = phase.status === 'COMPLETED' || phase.status === 'completed';

  return (
    <div className="rounded-xl border border-[#e6ddd4] bg-white overflow-hidden">
      {/* Phase Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-[#faf6f1] transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-50 text-blue-700 font-semibold">
            {index + 1}
          </div>
          <div className="text-left">
            <h4 className="font-semibold text-[#2d2a26]">{phase.name}</h4>
            <p className="text-sm text-[#6d6760]">{phase.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
            <StatusIcon className="h-3.5 w-3.5" />
            {statusInfo.label}
          </span>
          <svg
            className={`h-5 w-5 text-[#8b8177] transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Phase Details (Expanded) */}
      {isExpanded && (
        <div className="border-t border-[#e6ddd4] p-4 bg-[#faf6f1]">
          <div className="space-y-4">
            {/* Timeline */}
            {phase.start_date && (
              <div className="flex items-center gap-2 text-sm text-[#6d6760]">
                <Calendar className="h-4 w-4" />
                <span>
                  {new Date(phase.start_date).toLocaleDateString()}
                  {phase.end_date && ` - ${new Date(phase.end_date).toLocaleDateString()}`}
                </span>
              </div>
            )}

            {/* Checklist */}
            {phase.checklist && phase.checklist.length > 0 && (
              <div>
                <h5 className="text-sm font-semibold text-[#2d2a26] mb-2">Checklist</h5>
                <div className="space-y-2">
                  {phase.checklist.map((item: any) => (
                    <div key={item.id} className="flex items-center gap-2">
                      <div className={`h-4 w-4 rounded border-2 flex items-center justify-center ${
                        item.completed ? 'bg-green-500 border-green-500' : 'border-[#e6ddd4]'
                      }`}>
                        {item.completed && (
                          <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <span className={`text-sm ${item.completed ? 'text-[#8b8177] line-through' : 'text-[#2d2a26]'}`}>
                        {item.task}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              {isNotStarted && (
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={handleStartPhase}
                  isLoading={isStarting}
                >
                  <Play className="h-4 w-4 mr-1" />
                  Start Phase
                </Button>
              )}
              {isInProgress && (
                <Button 
                  size="sm"
                  onClick={handleCompletePhase}
                  isLoading={isCompleting}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Mark Complete
                </Button>
              )}
              {isCompleted && (
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="h-4 w-4" />
                  <span>Phase completed</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Findings Tab
function FindingsTab({ engagementId }: { engagementId: string }) {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  
  const { data: findings, isLoading, error, refetch } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}/findings`,
    queryKey: ['ptaas-findings', engagementId, severityFilter],
  });

  if (isLoading) {
    return <div className="text-center py-8 text-sm text-[#8b8177]">Loading findings...</div>;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Failed to load findings. Please try again.</p>
      </div>
    );
  }

  const severityConfig = {
    critical: { label: 'Critical', color: 'bg-red-100 text-red-700 border-red-200', count: 0 },
    high: { label: 'High', color: 'bg-orange-100 text-orange-700 border-orange-200', count: 0 },
    medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700 border-yellow-200', count: 0 },
    low: { label: 'Low', color: 'bg-blue-100 text-blue-700 border-blue-200', count: 0 },
    info: { label: 'Info', color: 'bg-gray-100 text-gray-700 border-gray-200', count: 0 },
  };

  // Count findings by severity
  const findingsList = findings || [];
  findingsList.forEach((finding: any) => {
    if (severityConfig[finding.severity as keyof typeof severityConfig]) {
      severityConfig[finding.severity as keyof typeof severityConfig].count++;
    }
  });

  // Filter findings
  const filteredFindings = severityFilter === 'all' 
    ? findingsList 
    : findingsList.filter((f: any) => f.severity === severityFilter);

  if (findingsList.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[#2d2a26]">Security Findings</h3>
          <Button size="sm" variant="outline">Export Report</Button>
        </div>
        <div className="text-center py-12">
          <AlertCircle className="mx-auto h-12 w-12 text-[#8b8177]" />
          <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">No findings reported yet</h3>
          <p className="mt-2 text-sm text-[#6d6760]">
            Findings will appear here as researchers discover and report vulnerabilities.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Security Findings</h3>
        <Button size="sm" variant="outline">Export Report</Button>
      </div>

      {/* Severity Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSeverityFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            severityFilter === 'all'
              ? 'bg-[#2d2a26] text-white'
              : 'bg-[#faf6f1] text-[#6d6760] hover:bg-[#e6ddd4]'
          }`}
        >
          All ({findingsList.length})
        </button>
        {Object.entries(severityConfig).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setSeverityFilter(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
              severityFilter === key
                ? config.color
                : 'bg-white text-[#6d6760] border-[#e6ddd4] hover:bg-[#faf6f1]'
            }`}
          >
            {config.label} ({config.count})
          </button>
        ))}
      </div>

      {/* Findings List */}
      <div className="space-y-3">
        {filteredFindings.map((finding: any) => (
          <FindingCard key={finding.id} finding={finding} onRefresh={refetch} />
        ))}
      </div>

      {filteredFindings.length === 0 && (
        <div className="text-center py-8 text-sm text-[#6d6760]">
          No {severityFilter} severity findings found.
        </div>
      )}
    </div>
  );
}

// Finding Card Component
function FindingCard({ finding, onRefresh }: { finding: any; onRefresh: () => void }) {
  const [showDetail, setShowDetail] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);

  const severityConfig = {
    critical: { label: 'Critical', color: 'bg-red-100 text-red-700', icon: '🔴' },
    high: { label: 'High', color: 'bg-orange-100 text-orange-700', icon: '🟠' },
    medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700', icon: '🟡' },
    low: { label: 'Low', color: 'bg-blue-100 text-blue-700', icon: '🔵' },
    info: { label: 'Info', color: 'bg-gray-100 text-gray-700', icon: '⚪' },
  };

  const statusConfig = {
    pending: { label: 'Pending Review', color: 'bg-gray-100 text-gray-700' },
    submitted: { label: 'Submitted', color: 'bg-blue-100 text-blue-700' },
    triaged: { label: 'Triaged', color: 'bg-purple-100 text-purple-700' },
    accepted: { label: 'Accepted', color: 'bg-green-100 text-green-700' },
    in_progress: { label: 'In Progress', color: 'bg-yellow-100 text-yellow-700' },
    fixed: { label: 'Fixed', color: 'bg-green-100 text-green-700' },
    validated: { label: 'Validated', color: 'bg-green-100 text-green-700' },
    rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700' },
    duplicate: { label: 'Duplicate', color: 'bg-yellow-100 text-yellow-700' },
  };

  const severity = severityConfig[finding.severity as keyof typeof severityConfig] || severityConfig.info;
  const status = statusConfig[finding.status as keyof typeof statusConfig] || statusConfig.pending;

  return (
    <>
      <div className="rounded-xl border border-[#e6ddd4] bg-white p-4 hover:border-blue-300 transition-colors">
        <div className="flex items-start justify-between">
          <div className="flex-1 cursor-pointer" onClick={() => setShowDetail(true)}>
            <div className="flex items-center gap-2 mb-2">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${severity.color}`}>
                <span>{severity.icon}</span>
                {severity.label}
              </span>
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${status.color}`}>
                {status.label}
              </span>
              <span className="text-xs text-[#8b8177]">#{finding.id}</span>
            </div>
            
            <h4 className="font-semibold text-[#2d2a26] mb-1">{finding.title}</h4>
            <p className="text-sm text-[#6d6760] line-clamp-2">{finding.description}</p>
            
            <div className="mt-3 flex items-center gap-4 text-xs text-[#8b8177]">
              <div className="flex items-center gap-1">
                <Users className="h-3.5 w-3.5" />
                <span>{finding.researcher_name || 'Unknown'}</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                <span>{new Date(finding.created_at).toLocaleDateString()}</span>
              </div>
              {finding.cvss_score && (
                <div className="flex items-center gap-1">
                  <Flag className="h-3.5 w-3.5" />
                  <span>CVSS {finding.cvss_score}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="flex gap-2 ml-4">
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => setShowAssignModal(true)}
            >
              <UserPlus className="h-4 w-4 mr-1" />
              Assign
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => setShowStatusModal(true)}
            >
              Change Status
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => setShowDetail(true)}
            >
              View Details
            </Button>
          </div>
        </div>
      </div>

      {/* Finding Detail Modal */}
      {showDetail && (
        <Modal
          isOpen={showDetail}
          onClose={() => setShowDetail(false)}
          title={`Finding #${finding.id}`}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${severity.color}`}>
                <span>{severity.icon}</span>
                {severity.label}
              </span>
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${status.color}`}>
                {status.label}
              </span>
            </div>

            <div>
              <h3 className="font-semibold text-[#2d2a26] mb-2">{finding.title}</h3>
              <p className="text-sm text-[#6d6760]">{finding.description}</p>
            </div>

            {finding.impact && (
              <div>
                <label className="text-sm font-medium text-[#8b8177]">Impact</label>
                <p className="mt-1 text-sm text-[#2d2a26]">{finding.impact}</p>
              </div>
            )}

            {finding.remediation && (
              <div>
                <label className="text-sm font-medium text-[#8b8177]">Remediation</label>
                <p className="mt-1 text-sm text-[#2d2a26]">{finding.remediation}</p>
              </div>
            )}

            <div className="flex gap-2 pt-4 border-t border-[#e6ddd4]">
              <Button variant="outline" onClick={() => setShowDetail(false)} className="flex-1">
                Close
              </Button>
              <Button variant="outline" onClick={() => { setShowDetail(false); setShowAssignModal(true); }} className="flex-1">
                Assign
              </Button>
              <Button onClick={() => { setShowDetail(false); setShowStatusModal(true); }} className="flex-1">
                Change Status
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Assign Modal */}
      {showAssignModal && (
        <PTaaSFindingAssignModal
          isOpen={showAssignModal}
          onClose={() => setShowAssignModal(false)}
          findingId={finding.id}
          onSuccess={onRefresh}
        />
      )}

      {/* Status Modal */}
      {showStatusModal && (
        <PTaaSFindingStatusModal
          isOpen={showStatusModal}
          onClose={() => setShowStatusModal(false)}
          findingId={finding.id}
          currentStatus={finding.status}
          onSuccess={onRefresh}
        />
      )}
    </>
  );
}

// Deliverables Tab
function DeliverablesTab({ engagementId }: { engagementId: string }) {
  const { data: deliverables, isLoading, error } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}/deliverables`,
    queryKey: ['ptaas-deliverables', engagementId],
  });

  if (isLoading) {
    return <div className="text-center py-8 text-sm text-[#8b8177]">Loading deliverables...</div>;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Failed to load deliverables. Please try again.</p>
      </div>
    );
  }

  const deliverablesList = deliverables || [];

  if (deliverablesList.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Deliverables</h3>
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-[#8b8177]" />
          <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">No deliverables submitted yet</h3>
          <p className="mt-2 text-sm text-[#6d6760]">
            Researchers will submit reports, evidence, and documentation as they complete testing phases.
          </p>
        </div>
      </div>
    );
  }

  const typeConfig = {
    report: { label: 'Report', color: 'bg-blue-100 text-blue-700', icon: FileText },
    evidence: { label: 'Evidence', color: 'bg-purple-100 text-purple-700', icon: FileText },
    documentation: { label: 'Documentation', color: 'bg-green-100 text-green-700', icon: FileText },
  };

  const statusConfig = {
    pending: { label: 'Pending Review', color: 'bg-gray-100 text-gray-700' },
    approved: { label: 'Approved', color: 'bg-green-100 text-green-700' },
    rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700' },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Deliverables</h3>
        <Button size="sm" variant="outline">Download All</Button>
      </div>

      <div className="space-y-3">
        {deliverablesList.map((deliverable: any) => {
          const type = typeConfig[deliverable.type as keyof typeof typeConfig] || typeConfig.report;
          const status = statusConfig[deliverable.status as keyof typeof statusConfig] || statusConfig.pending;
          const TypeIcon = type.icon;

          return (
            <div
              key={deliverable.id}
              className="rounded-xl border border-[#e6ddd4] bg-white p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className={`rounded-lg p-2 ${type.color}`}>
                    <TypeIcon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-[#2d2a26]">{deliverable.title}</h4>
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${status.color}`}>
                        {status.label}
                      </span>
                    </div>
                    <p className="text-sm text-[#6d6760] mb-2">{deliverable.description}</p>
                    <div className="flex items-center gap-4 text-xs text-[#8b8177]">
                      <div className="flex items-center gap-1">
                        <Users className="h-3.5 w-3.5" />
                        <span>{deliverable.researcher_name || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>{new Date(deliverable.submitted_at).toLocaleDateString()}</span>
                      </div>
                      {deliverable.file_size && (
                        <span>{(deliverable.file_size / 1024 / 1024).toFixed(2)} MB</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline">Download</Button>
                  {deliverable.status === 'pending' && (
                    <>
                      <Button size="sm">Approve</Button>
                      <Button size="sm" variant="outline">Reject</Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Team Tab
function TeamTab({ engagementId }: { engagementId: string }) {
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedResearcher, setSelectedResearcher] = useState<any>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const { showToast } = useToast();
  
  const { data: engagement, refetch } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}`,
    queryKey: ['ptaas-engagement', engagementId],
  });

  // Fetch researcher details for assigned researchers
  const assignedResearcherIds = engagement?.assigned_researchers || [];
  const { data: allResearchers } = useApiQuery({
    endpoint: '/matching/organization/researchers?limit=100',
    queryKey: ['organization-researchers'],
    enabled: assignedResearcherIds.length > 0,
  });

  // Filter to get only assigned researchers
  const researchers = allResearchers?.filter((r: any) => 
    assignedResearcherIds.includes(r.id)
  ) || [];

  const handleViewProfile = (researcher: any) => {
    setSelectedResearcher(researcher);
    setShowProfileModal(true);
  };

  const handleMessage = (researcher: any) => {
    // TODO: Navigate to messages page when implemented
    // window.location.href = `/organization/messages?researcher=${researcher.id}`;
    showToast(`Messaging feature coming soon! You'll be able to chat with ${researcher.user?.username || 'this researcher'}.`, 'info');
  };

  if (researchers.length === 0) {
    return (
      <>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-[#2d2a26]">Assigned Researchers</h3>
            <Button size="sm" onClick={() => setShowAssignModal(true)}>
              Assign Researcher
            </Button>
          </div>
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-[#8b8177]" />
            <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">No researchers assigned yet</h3>
            <p className="mt-2 text-sm text-[#6d6760]">
              Assign expert security researchers to this engagement to begin testing.
            </p>
            <Button className="mt-6" size="sm" onClick={() => setShowAssignModal(true)}>
              Assign Your First Researcher
            </Button>
          </div>
        </div>
        
        {showAssignModal && engagement && (
          <PTaaSResearcherAssignModal
            isOpen={showAssignModal}
            onClose={() => setShowAssignModal(false)}
            engagementId={engagement.id}
            engagementName={engagement.name}
            onSuccess={() => refetch()}
          />
        )}
      </>
    );
  }

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[#2d2a26]">Assigned Researchers ({researchers.length})</h3>
          <Button size="sm" onClick={() => setShowAssignModal(true)}>
            Assign More
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {researchers.map((researcher: any) => (
            <div
              key={researcher.id}
              className="rounded-xl border border-[#e6ddd4] bg-white p-4"
            >
              <div className="flex items-start gap-3">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                  {researcher.user?.username?.charAt(0)?.toUpperCase() || 'R'}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-[#2d2a26]">{researcher.user?.username || 'Unknown'}</h4>
                  <p className="text-xs text-[#8b8177]">{researcher.user?.email || ''}</p>
                  
                  <div className="mt-2 flex items-center gap-4 text-xs text-[#8b8177]">
                    <div className="flex items-center gap-1">
                      <Flag className="h-3.5 w-3.5" />
                      <span>{researcher.verified_reports || 0} reports</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-3.5 w-3.5" />
                      <span>{researcher.reputation_score || 0} rep</span>
                    </div>
                  </div>

                  {researcher.profile?.specializations && researcher.profile.specializations.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {researcher.profile.specializations.slice(0, 3).map((spec: string) => (
                        <span
                          key={spec}
                          className="px-2 py-0.5 rounded bg-blue-50 text-xs text-blue-700"
                        >
                          {spec}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="mt-3 flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleViewProfile(researcher)}
                    >
                      View Profile
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleMessage(researcher)}
                    >
                      Message
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {showAssignModal && engagement && (
        <PTaaSResearcherAssignModal
          isOpen={showAssignModal}
          onClose={() => setShowAssignModal(false)}
          engagementId={engagement.id}
          engagementName={engagement.name}
          onSuccess={() => refetch()}
        />
      )}

      {/* Researcher Profile Modal */}
      {showProfileModal && selectedResearcher && (
        <Modal
          isOpen={showProfileModal}
          onClose={() => {
            setShowProfileModal(false);
            setSelectedResearcher(null);
          }}
          title="Researcher Profile"
        >
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start gap-4">
              <div className="h-20 w-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-3xl font-semibold">
                {selectedResearcher.user?.username?.charAt(0)?.toUpperCase() || 'R'}
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-[#2d2a26]">
                  {selectedResearcher.user?.username || 'Unknown'}
                </h3>
                <p className="text-sm text-[#8b8177]">{selectedResearcher.user?.email || ''}</p>
                <div className="mt-2 flex items-center gap-4">
                  <div className="flex items-center gap-1 text-sm">
                    <Flag className="h-4 w-4 text-blue-600" />
                    <span className="font-semibold text-[#2d2a26]">
                      {selectedResearcher.verified_reports || 0}
                    </span>
                    <span className="text-[#8b8177]">reports</span>
                  </div>
                  <div className="flex items-center gap-1 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="font-semibold text-[#2d2a26]">
                      {selectedResearcher.reputation_score || 0}
                    </span>
                    <span className="text-[#8b8177]">reputation</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bio */}
            {selectedResearcher.bio && (
              <div>
                <h4 className="text-sm font-semibold text-[#2d2a26] mb-2">About</h4>
                <p className="text-sm text-[#6d6760]">{selectedResearcher.bio}</p>
              </div>
            )}

            {/* Specializations */}
            {selectedResearcher.profile?.specializations && selectedResearcher.profile.specializations.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-[#2d2a26] mb-2">Specializations</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedResearcher.profile.specializations.map((spec: string) => (
                    <span
                      key={spec}
                      className="px-3 py-1 rounded-lg bg-blue-50 text-sm text-blue-700 font-medium"
                    >
                      {spec}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Skills */}
            {selectedResearcher.profile?.skills && selectedResearcher.profile.skills.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-[#2d2a26] mb-2">Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedResearcher.profile.skills.map((skill: string) => (
                    <span
                      key={skill}
                      className="px-3 py-1 rounded-lg bg-gray-100 text-sm text-[#2d2a26]"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {selectedResearcher.profile?.experience_years && (
              <div>
                <h4 className="text-sm font-semibold text-[#2d2a26] mb-2">Experience</h4>
                <p className="text-sm text-[#6d6760]">
                  {selectedResearcher.profile.experience_years} years in security research
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
              <Button
                className="flex-1"
                onClick={() => handleMessage(selectedResearcher)}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Send Message
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowProfileModal(false);
                  setSelectedResearcher(null);
                }}
              >
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}

// Activity Tab
function ActivityTab({ engagementId }: { engagementId: string }) {
  const { data: activities, isLoading, error } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}/collaboration`,
    queryKey: ['ptaas-activity', engagementId],
  });

  if (isLoading) {
    return <div className="text-center py-8 text-sm text-[#8b8177]">Loading activity...</div>;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Failed to load activity. Please try again.</p>
      </div>
    );
  }

  const activitiesList = activities || [];

  if (activitiesList.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Activity Feed</h3>
        <div className="text-center py-12">
          <MessageSquare className="mx-auto h-12 w-12 text-[#8b8177]" />
          <h3 className="mt-4 text-lg font-semibold text-[#2d2a26]">No activity yet</h3>
          <p className="mt-2 text-sm text-[#6d6760]">
            Activity will appear here as researchers work on the engagement, submit findings, and communicate with your team.
          </p>
        </div>
      </div>
    );
  }

  const activityIcons = {
    comment: MessageSquare,
    finding: Flag,
    deliverable: FileText,
    phase_change: TrendingUp,
    assignment: Users,
    status_change: CheckCircle,
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#2d2a26]">Activity Feed</h3>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-[#e6ddd4]" />

        {/* Activity Items */}
        <div className="space-y-6">
          {activitiesList.map((activity: any, index: number) => {
            const Icon = activityIcons[activity.type as keyof typeof activityIcons] || MessageSquare;
            
            return (
              <div key={activity.id} className="relative flex gap-4">
                {/* Icon */}
                <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-full bg-white border-2 border-[#e6ddd4]">
                  <Icon className="h-5 w-5 text-blue-600" />
                </div>

                {/* Content */}
                <div className="flex-1 pb-6">
                  <div className="rounded-xl border border-[#e6ddd4] bg-white p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-[#2d2a26]">{activity.title}</h4>
                        <p className="text-sm text-[#6d6760]">{activity.description}</p>
                      </div>
                      <span className="text-xs text-[#8b8177] whitespace-nowrap">
                        {new Date(activity.created_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>

                    {activity.user_name && (
                      <div className="flex items-center gap-2 text-xs text-[#8b8177]">
                        <Users className="h-3.5 w-3.5" />
                        <span>{activity.user_name}</span>
                      </div>
                    )}

                    {activity.content && (
                      <div className="mt-3 p-3 rounded-lg bg-[#faf6f1] text-sm text-[#2d2a26]">
                        {activity.content}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
