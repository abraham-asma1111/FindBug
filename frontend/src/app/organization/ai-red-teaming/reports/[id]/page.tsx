'use client';

import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';

export default function AIRedTeamingReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const reportId = params.id as string;

  // Fetch report details
  const { data: report, isLoading, error, refetch } = useApiQuery(
    `/ai-red-teaming/reports/${reportId}`,
    { enabled: !!user && !!reportId }
  );

  const severityColors: Record<string, string> = {
    critical: 'bg-[#fff2f1] text-[#9d1f1f]',
    high: 'bg-[#fff5ed] text-[#d6561c]',
    medium: 'bg-[#faf1e1] text-[#9a6412]',
    low: 'bg-[#f3ede6] text-[#5f5851]',
  };

  const statusColors: Record<string, string> = {
    new: 'bg-[#eef5fb] text-[#2d78a8]',
    under_review: 'bg-[#faf1e1] text-[#9a6412]',
    validated: 'bg-[#eef7ef] text-[#24613a]',
    rejected: 'bg-[#fff2f1] text-[#9d1f1f]',
    resolved: 'bg-[#f3ede6] text-[#5f5851]',
  };

  if (isLoading) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="AI Vulnerability Report"
            subtitle="Loading report details..."
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

  if (error || !report) {
    return (
      <ProtectedRoute allowedRoles={['organization']}>
        {user && (
          <PortalShell
            user={user}
            title="AI Vulnerability Report"
            subtitle="Report not found"
            navItems={getPortalNavItems(user.role)}
          >
            <Alert variant="error">
              {error?.message || 'Report not found'}
            </Alert>
            <Button onClick={() => router.back()} className="mt-4">
              Go Back
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
          title={report.title}
          subtitle="AI Vulnerability Report"
          navItems={getPortalNavItems(user.role)}
        >
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                    severityColors[report.severity] || severityColors.low
                  }`}
                >
                  {report.severity}
                </span>
                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                    statusColors[report.status] || statusColors.new
                  }`}
                >
                  {report.status.replace(/_/g, ' ')}
                </span>
                <span className="inline-flex items-center rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#2d2a26]">
                  {report.attack_type.replace(/_/g, ' ')}
                </span>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => router.back()}>
                  Back
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => router.push(`/organization/ai-red-teaming/${report.engagement_id}`)}
                >
                  View Engagement
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => window.print()}
                >
                  Print Report
                </Button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
            {/* Left Column - Report Details */}
            <div className="space-y-6">
              {/* Attack Details */}
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Attack Details
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                      Input Prompt
                    </div>
                    <div className="p-4 rounded-lg bg-[#fcfaf7] dark:bg-gray-800 border border-[#e6ddd4] dark:border-gray-700">
                      <pre className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap font-mono">
                        {report.input_prompt}
                      </pre>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                      Model Response
                    </div>
                    <div className="p-4 rounded-lg bg-[#fcfaf7] dark:bg-gray-800 border border-[#e6ddd4] dark:border-gray-700">
                      <pre className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap font-mono">
                        {report.model_response}
                      </pre>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Impact & Reproduction */}
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Impact Analysis
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                      Impact
                    </div>
                    <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                      {report.impact}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                      Reproduction Steps
                    </div>
                    <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                      {report.reproduction_steps}
                    </div>
                  </div>
                  {report.mitigation_recommendation && (
                    <div>
                      <div className="text-sm font-medium text-[#6d6760] dark:text-slate-400 mb-2">
                        Mitigation Recommendation
                      </div>
                      <div className="text-sm text-[#2d2a26] dark:text-slate-100 whitespace-pre-wrap">
                        {report.mitigation_recommendation}
                      </div>
                    </div>
                  )}
                </div>
              </Card>

              {/* Report Status Info - For organizations to view only */}
              {report.status === 'new' && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Triage Status
                  </h3>
                  <Alert variant="info">
                    This report is awaiting triage review. A triage specialist will classify and validate this finding.
                  </Alert>
                </Card>
              )}

              {/* Under Review Status */}
              {report.status === 'under_review' && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Triage Status
                  </h3>
                  <Alert variant="info">
                    This report is currently under review by the triage team.
                  </Alert>
                </Card>
              )}
            </div>

            {/* Right Column - Metadata */}
            <div className="space-y-6">
              {/* Report Info */}
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Report Information
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-[#6d6760] dark:text-slate-400">Submitted</span>
                    <span className="font-medium text-[#2d2a26] dark:text-slate-100">
                      {new Date(report.submitted_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[#6d6760] dark:text-slate-400">Attack Type</span>
                    <span className="font-medium text-[#2d2a26] dark:text-slate-100">
                      {report.attack_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[#6d6760] dark:text-slate-400">Severity</span>
                    <span className="font-medium text-[#2d2a26] dark:text-slate-100">
                      {report.severity}
                    </span>
                  </div>
                  {report.model_version && (
                    <div className="flex items-center justify-between">
                      <span className="text-[#6d6760] dark:text-slate-400">Model Version</span>
                      <span className="font-medium text-[#2d2a26] dark:text-slate-100">
                        {report.model_version}
                      </span>
                    </div>
                  )}
                  {report.classification && (
                    <div className="flex items-center justify-between">
                      <span className="text-[#6d6760] dark:text-slate-400">Classification</span>
                      <span className="font-medium text-[#2d2a26] dark:text-slate-100">
                        {report.classification}
                      </span>
                    </div>
                  )}
                </div>
              </Card>

              {/* Validation Status - Only show if status is VALIDATED or INVALID */}
              {(report.status === 'validated' || report.status === 'invalid') && report.validated_at && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Validation Status
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                          report.status === 'validated'
                            ? 'bg-[#eef7ef] text-[#24613a]'
                            : 'bg-[#fff2f1] text-[#9d1f1f]'
                        }`}
                      >
                        {report.status === 'validated' ? 'Validated - Valid' : 'Validated - Invalid'}
                      </span>
                    </div>
                    <div className="text-xs text-[#8b8177] dark:text-slate-500">
                      Validated on {new Date(report.validated_at).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </Card>
              )}

              {/* Classification Status - Only show if classified */}
              {report.classification && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                    Classification
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center rounded-full bg-[#eef5fb] px-3 py-1 text-xs font-semibold text-[#2d78a8]">
                        {report.classification}
                      </span>
                    </div>
                  </div>
                </Card>
              )}

              {/* Workflow Status */}
              <Card className="p-6">
                <h3 className="text-lg font-bold text-[#2d2a26] dark:text-slate-100 mb-4">
                  Workflow Status
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[#6d6760] dark:text-slate-400">Status</span>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${
                        statusColors[report.status] || statusColors.new
                      }`}
                    >
                      {report.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[#6d6760] dark:text-slate-400">Classified</span>
                    <span className="text-sm font-medium text-[#2d2a26] dark:text-slate-100">
                      {report.classification ? 'Yes' : 'No'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[#6d6760] dark:text-slate-400">Validated</span>
                    <span className="text-sm font-medium text-[#2d2a26] dark:text-slate-100">
                      {(report.status === 'validated' || report.status === 'invalid') ? 'Yes' : 'Pending'}
                    </span>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Classify Modal - Removed, only triage can classify */}
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
