'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import SimpleTabs from '@/components/ui/SimpleTabs';
import EmptyState from '@/components/ui/EmptyState';
import { formatDateTime } from '@/lib/portal';

export default function OrganizationReportsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('pending');
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [selectedReport, setSelectedReport] = useState<any>(null);

  // Fetch reports based on active tab
  const { data: reports, isLoading, error, refetch } = useApiQuery(
    `/reports?status=${activeTab}&search=${search}&severity=${severityFilter !== 'all' ? severityFilter : ''}`,
    { enabled: !!user }
  );

  const tabs = [
    { id: 'pending', label: 'Pending Review' },
    { id: 'in_progress', label: 'In Progress' },
    { id: 'resolved', label: 'Resolved' },
    { id: 'all', label: 'All Reports' },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-[#fde9e7] text-[#9d1f1f]';
      case 'high':
        return 'bg-[#fff4e6] text-[#b54708]';
      case 'medium':
        return 'bg-[#faf1e1] text-[#9a6412]';
      case 'low':
        return 'bg-[#edf5fb] text-[#2d78a8]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'new':
      case 'pending':
        return 'bg-[#faf1e1] text-[#9a6412]';
      case 'triaged':
      case 'in_progress':
        return 'bg-[#edf5fb] text-[#2d78a8]';
      case 'resolved':
      case 'fixed':
        return 'bg-[#e6f7ed] text-[#0d7a3d]';
      case 'duplicate':
        return 'bg-[#f3ede6] text-[#5f5851]';
      case 'invalid':
      case 'rejected':
        return 'bg-[#fde9e7] text-[#9d1f1f]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user && (
        <PortalShell
          user={user}
          title="Reports Management"
          subtitle="Review and manage vulnerability reports"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Filters */}
            <Card>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search reports..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <div className="w-full sm:w-48">
                  <Select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                  </Select>
                </div>
              </div>
            </Card>

            {/* Tabs */}
            <SimpleTabs
              tabs={tabs}
              activeTab={activeTab}
              onChange={setActiveTab}
            />

            {/* Error State */}
            {error && (
              <Card className="border-[#f2c0bc] bg-[#fff2f1]">
                <p className="text-sm text-[#b42318]">{error.message || 'An error occurred'}</p>
              </Card>
            )}

            {/* Reports List */}
            {isLoading ? (
              <Card>
                <div className="flex items-center justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#e6ddd4] border-t-[#2d2a26]"></div>
                </div>
              </Card>
            ) : reports && reports.length > 0 ? (
              <div className="space-y-4">
                {reports.map((report: any) => (
                  <Card 
                    key={report.id} 
                    className="hover:border-[#d4c5b3] transition-colors cursor-pointer"
                    onClick={() => setSelectedReport(report)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        {/* Badges */}
                        <div className="flex flex-wrap items-center gap-2 mb-3">
                          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getSeverityColor(report.severity)}`}>
                            {report.severity?.toUpperCase() || 'UNKNOWN'}
                          </span>
                          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(report.status)}`}>
                            {report.status}
                          </span>
                          {report.program_name && (
                            <span className="rounded-full bg-[#f3ede6] px-3 py-1 text-xs font-semibold text-[#5f5851]">
                              {report.program_name}
                            </span>
                          )}
                        </div>

                        {/* Report Title */}
                        <h3 className="text-lg font-semibold text-[#2d2a26] mb-2">
                          {report.title}
                        </h3>

                        {/* Metadata */}
                        <div className="flex flex-wrap items-center gap-4 text-sm text-[#6d6760]">
                          <span>ID: {report.id.slice(0, 8)}</span>
                          {report.researcher_name && (
                            <span>By: {report.researcher_name}</span>
                          )}
                          <span>Submitted: {formatDateTime(report.created_at)}</span>
                          {report.bounty_amount && (
                            <span className="font-semibold text-[#2d2a26]">
                              Bounty: ${report.bounty_amount}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex-shrink-0">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedReport(report);
                          }}
                        >
                          View Details
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No reports found"
                description={
                  activeTab === 'pending'
                    ? 'No pending reports to review'
                    : `No ${activeTab} reports found`
                }
              />
            )}
          </div>

          {/* Report Detail Modal - TODO: Create separate component */}
          {selectedReport && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="space-y-6">
                  <div className="flex items-start justify-between">
                    <h2 className="text-2xl font-bold text-[#2d2a26]">
                      {selectedReport.title}
                    </h2>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedReport(null)}
                    >
                      Close
                    </Button>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getSeverityColor(selectedReport.severity)}`}>
                      {selectedReport.severity?.toUpperCase()}
                    </span>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(selectedReport.status)}`}>
                      {selectedReport.status}
                    </span>
                  </div>

                  {/* Description */}
                  <div>
                    <h3 className="text-sm font-semibold text-[#2d2a26] mb-2">Description</h3>
                    <p className="text-sm text-[#6d6760] leading-relaxed whitespace-pre-wrap">
                      {selectedReport.description || 'No description provided'}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3 pt-4 border-t border-[#e6ddd4]">
                    <Button onClick={() => alert('Acknowledge functionality coming soon')}>
                      Acknowledge
                    </Button>
                    <Button variant="secondary" onClick={() => alert('Request info functionality coming soon')}>
                      Request More Info
                    </Button>
                    <Button variant="secondary" onClick={() => setSelectedReport(null)}>
                      Close
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </PortalShell>
      )}
    </ProtectedRoute>
  );
}
