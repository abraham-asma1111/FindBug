'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Tabs, { TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs';
import Alert from '@/components/ui/Alert';
import AIRedTeamingEnvironmentSetupModal from '@/components/organization/ai-red-teaming/AIRedTeamingEnvironmentSetupModal';
import AIRedTeamingExpertInvitationModal from '@/components/organization/ai-red-teaming/AIRedTeamingExpertInvitationModal';

export default function AIRedTeamingEngagementDetailPage() {
  const params = useParams();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const engagementId = params.id as string;
  const [showEnvironmentModal, setShowEnvironmentModal] = useState(false);
  const [showInvitationModal, setShowInvitationModal] = useState(false);

  // Fetch engagement details
  const { data: engagement, isLoading, error, refetch } = useApiQuery(
    `/ai-red-teaming/engagements/${engagementId}`,
    { enabled: !!user && !!engagementId }
  );

  // Fetch testing environment
  const { data: testingEnv } = useApiQuery(
    `/ai-red-teaming/engagements/${engagementId}/testing-environment`,
    { enabled: !!user && !!engagementId }
  );

  // Fetch vulnerability reports
  const { data: reports, isLoading: isLoadingReports, error: reportsError, refetch: refetchReports } = useApiQuery(
    `/ai-red-teaming/engagements/${engagementId}/reports`,
    { enabled: !!user && !!engagementId }
  );

  // Fetch security reports
  const { data: securityReports } = useApiQuery(
    `/ai-red-teaming/engagements/${engagementId}/security-reports`,
    { enabled: !!user && !!engagementId }
  );

  // Update engagement status mutation
  const { mutate: updateStatus, isLoading: isUpdatingStatus } = useApiMutation(
    `/ai-red-teaming/engagements/${engagementId}/status`,
    'PATCH'
  );

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateStatus({ status: newStatus });
      refetch();
    } catch (err) {
      // Error handled by mutation
    }
  };

  const statusColors: Record<string, string> = {
    draft: 'bg-[#f3ede6] text-[#5f5851]',
    pending: 'bg-[#faf1e1] text-[#9a6412]',
    active: 'bg-[#eef5fb] text-[#2d78a8]',
    completed: 'bg-[#eef7ef] text-[#24613a]',
    archived: 'bg-[#f3ede6] text-[#8b8177]',
  };

  const modelTypeLabels: Record<string, string> = {
    llm: 'Large Language Model',
    ml_model: 'ML Model',
    ai_agent: 'AI Agent',
    chatbot: 'Chatbot',
    recommendation_system: 'Recommendation System',
    computer_vision: 'Computer Vision',
  };

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="AI Red Teaming"
            subtitle="Loading engagement details..."
            navItems={getPortalNavItems(user.role)}
          >
            <Card>
              <div className="flex items-center justify-center py-12">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
              </div>
            </Card>
          </PortalShell>
        )}
      </ProtectedRoute>
    );
  }

  if (error || !engagement) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="AI Red Teaming"
            subtitle="Engagement not found"
            navItems={getPortalNavItems(user.role)}
          >
            <Alert variant="error">
              {error?.message || 'Engagement not found'}
            </Alert>
            <Button onClick={() => router.push('/organization/ai-red-teaming')} className="mt-4">
              Back to Engagements
            </Button>
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
          title={engagement.name}
          subtitle="AI Red Teaming Engagement"
          navItems={getPortalNavItems(user.role)}
        >
          {/* Header Section */}
          <div className="mb-6">
            {engagement.status === 'draft' && (
              <Alert variant="info" className="mb-4">
                <strong>Auto-Broadcast Workflow:</strong> When you publish this engagement, the BountyMatch algorithm automatically filters researchers by AI/ML expertise and reputation, then broadcasts to ALL qualified researchers—just like bug bounty programs. You can also manually invite specific researchers before publishing.
              </Alert>
            )}
            {engagement.status === 'active' && (
              <Alert variant="success" className="mb-4">
                <strong>Engagement Active:</strong> This engagement has been broadcasted to {engagement.assigned_experts?.length || 'algorithm-filtered'} researchers. Reports will appear in the Vulnerability Reports tab.
              </Alert>
            )}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                      statusColors[engagement.status] || statusColors.draft
                    }`}
                  >
                    {engagement.status}
                  </span>
                  <span className="text-sm text-[#6d6760] dark:text-slate-400">
                    {modelTypeLabels[engagement.model_type] || engagement.model_type}
                  </span>
                </div>
                <p className="text-sm text-[#6d6760] dark:text-slate-400">
                  {engagement.target_ai_system}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => router.push('/organization/ai-red-teaming')}
                >
                  Back
                </Button>
                {engagement.status === 'draft' && (
                  <>
                    <Button
                      variant="secondary"
                      onClick={() => setShowEnvironmentModal(true)}
                    >
                      Setup Environment
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => setShowInvitationModal(true)}
                    >
                      Invite Experts (Optional)
                    </Button>
                    <Button
                      onClick={() => handleStatusChange('active')}
                      disabled={isUpdatingStatus}
                      title="Publishes engagement and auto-broadcasts to algorithm-filtered researchers"
                    >
                      Publish & Broadcast
                    </Button>
                  </>
                )}
                {engagement.status === 'active' && (
                  <Button
                    onClick={() => handleStatusChange('completed')}
                    disabled={isUpdatingStatus}
                  >
                    Complete Engagement
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-4 mb-6">
            <Card className="p-4">
              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-1">Total Findings</div>
              <div className="text-2xl font-bold text-[#2d2a26] dark:text-slate-100">
                {engagement.total_findings || 0}
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-1">Critical</div>
              <div className="text-2xl font-bold text-[#9d1f1f]">
                {engagement.critical_findings || 0}
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-1">High</div>
              <div className="text-2xl font-bold text-[#d6561c]">
                {engagement.high_findings || 0}
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-1">Assigned Experts</div>
              <div className="text-2xl font-bold text-[#2d2a26] dark:text-slate-100">
                {engagement.assigned_experts?.length || 0}
              </div>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultTab="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="environment">Testing Environment</TabsTrigger>
              <TabsTrigger value="experts">Assigned Experts ({engagement.assigned_experts?.length || 0})</TabsTrigger>
              <TabsTrigger value="reports">Vulnerability Reports ({reports?.length || 0})</TabsTrigger>
              <TabsTrigger value="security">Security Reports</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview">
              <div className="space-y-6">
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Engagement Details
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        Target AI System
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100">
                        {engagement.target_ai_system}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        Testing Environment
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                        {engagement.testing_environment}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        Ethical Guidelines
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                        {engagement.ethical_guidelines}
                      </div>
                    </div>
                    {engagement.scope_description && (
                      <div>
                        <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                          Scope Description
                        </div>
                        <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                          {engagement.scope_description}
                        </div>
                      </div>
                    )}
                    {engagement.allowed_attack_types && engagement.allowed_attack_types.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                          Allowed Attack Types
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {engagement.allowed_attack_types.map((type: string) => (
                            <span
                              key={type}
                              className="inline-flex items-center rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-medium text-[#2d2a26]"
                            >
                              {type.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </Card>

                {engagement.start_date && (
                  <Card className="p-6">
                    <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                      Timeline
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[#6d6760] dark:text-slate-400">Start Date</span>
                        <span className="text-sm font-medium text-[#2d2a26] dark:text-slate-100">
                          {new Date(engagement.start_date).toLocaleDateString('en-US', {
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </span>
                      </div>
                      {engagement.end_date && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-[#6d6760] dark:text-slate-400">End Date</span>
                          <span className="text-sm font-medium text-[#2d2a26] dark:text-slate-100">
                            {new Date(engagement.end_date).toLocaleDateString('en-US', {
                              month: 'long',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </span>
                        </div>
                      )}
                    </div>
                  </Card>
                )}
              </div>
            </TabsContent>

            {/* Testing Environment Tab */}
            <TabsContent value="environment">
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Testing Environment Configuration
                </h3>
                {testingEnv ? (
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        Sandbox URL
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100 font-mono">
                        {testingEnv.sandbox_url}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        API Endpoint
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100 font-mono">
                        {testingEnv.api_endpoint}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-1">
                        Isolated Environment
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100">
                        {testingEnv.is_isolated ? 'Yes' : 'No'}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-4">
                      No testing environment configured yet
                    </p>
                    <Button onClick={() => setShowEnvironmentModal(true)}>
                      Setup Testing Environment
                    </Button>
                  </div>
                )}
              </Card>
            </TabsContent>

            {/* Assigned Experts Tab */}
            <TabsContent value="experts">
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Assigned AI Security Experts
                </h3>
                {engagement.assigned_experts && engagement.assigned_experts.length > 0 ? (
                  <div className="space-y-3">
                    {engagement.assigned_experts.map((expertId: string) => (
                      <div
                        key={expertId}
                        className="flex items-center justify-between p-3 rounded-lg border border-[#e6ddd4] dark:border-gray-700"
                      >
                        <div className="text-sm text-[#2d2a26] dark:text-slate-100">
                          Expert ID: {expertId}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-4">
                      No experts assigned yet
                    </p>
                    <Button onClick={() => setShowInvitationModal(true)}>
                      Invite Experts
                    </Button>
                  </div>
                )}
              </Card>
            </TabsContent>

            {/* Vulnerability Reports Tab */}
            <TabsContent value="reports">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100">
                    Vulnerability Reports
                  </h3>
                  <Button
                    variant="secondary"
                    onClick={() => refetchReports()}
                    disabled={isLoadingReports}
                  >
                    {isLoadingReports ? 'Loading...' : 'Refresh'}
                  </Button>
                </div>
                
                {isLoadingReports ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="h-6 w-6 animate-spin rounded-full border-3 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                  </div>
                ) : reportsError ? (
                  <Alert variant="error">
                    Failed to load reports: {reportsError.message}
                  </Alert>
                ) : reports && reports.length > 0 ? (
                  <div className="space-y-3">
                    {reports.map((report: any) => (
                      <button
                        key={report.id}
                        onClick={() => router.push(`/organization/ai-red-teaming/reports/${report.id}`)}
                        className="w-full p-4 rounded-lg border border-[#e6ddd4] dark:border-gray-700 hover:border-[#7d39c2] hover:bg-[#fcfaf7] dark:hover:bg-gray-800 transition-all text-left"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-[#2d2a26] dark:text-slate-100">
                            {report.title}
                          </h4>
                          <div className="flex gap-2">
                            <span
                              className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${
                                report.severity === 'critical'
                                  ? 'bg-[#fff2f1] text-[#9d1f1f]'
                                  : report.severity === 'high'
                                    ? 'bg-[#fff5ed] text-[#d6561c]'
                                    : report.severity === 'medium'
                                      ? 'bg-[#faf1e1] text-[#9a6412]'
                                      : 'bg-[#f3ede6] text-[#5f5851]'
                              }`}
                            >
                              {report.severity}
                            </span>
                            <span className="inline-flex items-center rounded-full bg-[#eef5fb] px-2 py-1 text-xs font-semibold text-[#2d78a8]">
                              {report.status}
                            </span>
                          </div>
                        </div>
                        <div className="text-sm text-[#6d6760] dark:text-slate-400 mb-2">
                          Attack Type: {report.attack_type.replace(/_/g, ' ')}
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-[#8b8177] dark:text-slate-500">
                            Submitted: {new Date(report.submitted_at).toLocaleDateString()}
                          </div>
                          <div className="text-xs text-[#7d39c2] font-semibold">
                            View Details →
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-sm text-[#6d6760] dark:text-slate-400">
                      No vulnerability reports submitted yet
                    </p>
                  </div>
                )}
              </Card>
            </TabsContent>

            {/* Security Reports Tab */}
            <TabsContent value="security">
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Security Summary Reports
                </h3>
                {securityReports && securityReports.length > 0 ? (
                  <div className="space-y-3">
                    {securityReports.map((report: any) => (
                      <div
                        key={report.id}
                        className="p-4 rounded-lg border border-[#e6ddd4] dark:border-gray-700"
                      >
                        <h4 className="font-medium text-[#2d2a26] dark:text-slate-100 mb-2">
                          {report.report_title}
                        </h4>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-[#6d6760] dark:text-slate-400">Security</div>
                            <div className="font-medium text-[#2d2a26] dark:text-slate-100">
                              {report.security_findings}
                            </div>
                          </div>
                          <div>
                            <div className="text-[#6d6760] dark:text-slate-400">Safety</div>
                            <div className="font-medium text-[#2d2a26] dark:text-slate-100">
                              {report.safety_findings}
                            </div>
                          </div>
                          <div>
                            <div className="text-[#6d6760] dark:text-slate-400">Privacy</div>
                            <div className="font-medium text-[#2d2a26] dark:text-slate-100">
                              {report.privacy_findings}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-sm text-[#6d6760] dark:text-slate-400 mb-4">
                      No security reports generated yet
                    </p>
                    <Button>Generate Security Report</Button>
                  </div>
                )}
              </Card>
            </TabsContent>
          </Tabs>

          {/* Modals */}
          <AIRedTeamingEnvironmentSetupModal
            isOpen={showEnvironmentModal}
            onClose={() => setShowEnvironmentModal(false)}
            engagementId={engagementId}
            onSuccess={refetch}
          />
          <AIRedTeamingExpertInvitationModal
            isOpen={showInvitationModal}
            onClose={() => setShowInvitationModal(false)}
            engagementId={engagementId}
            onSuccess={refetch}
          />
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
