'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import { api } from '@/lib/api';
import Spinner from '@/components/ui/Spinner';
import Modal from '@/components/ui/Modal';

interface Report {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'pending' | 'approved' | 'rejected' | 'resolved';
  program_name: string;
  submitted_at: string;
  bounty_amount?: number;
}

interface ReportDetail {
  id: string;
  title: string;
  description: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  affected_asset?: string;
  suggested_severity: 'critical' | 'high' | 'medium' | 'low';
  vulnerability_type?: string;
  status: string;
}

interface EditReportFormState {
  title: string;
  description: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  suggested_severity: 'critical' | 'high' | 'medium' | 'low';
  affected_asset: string;
  vulnerability_type: string;
}

const statusTone: Record<string, string> = {
  new: 'bg-[#eef5fb] text-[#2d78a8]',
  pending: 'bg-[#faf1e1] text-[#9a6412]',
  approved: 'bg-[#eef7ef] text-[#24613a]',
  rejected: 'bg-[#fff2f1] text-[#b42318]',
  resolved: 'bg-[#f3ede6] text-[#5f5851]',
};

const severityTone: Record<string, string> = {
  critical: 'bg-[#9d1f1f] text-white',
  high: 'bg-[#d6561c] text-white',
  medium: 'bg-[#d89b16] text-[#2d2a26]',
  low: 'bg-[#2d78a8] text-white',
};

export default function ReportList() {
  const router = useRouter();
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
    search: '',
  });
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [editingReportId, setEditingReportId] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [isDeletingReportId, setIsDeletingReportId] = useState<string | null>(null);
  const [deletedReportIds, setDeletedReportIds] = useState<Set<string>>(new Set());
  const [editError, setEditError] = useState('');
  const [editForm, setEditForm] = useState<EditReportFormState>({
    title: '',
    description: '',
    steps_to_reproduce: '',
    impact_assessment: '',
    suggested_severity: 'medium',
    affected_asset: '',
    vulnerability_type: '',
  });

  const { data: reportsData, isLoading, isError, refetch } = useApiQuery<Report[]>({
    endpoint: '/reports/my-reports',
    enabled: true,
  });

  const { data: editingReport, isLoading: isLoadingEditingReport } = useApiQuery<ReportDetail>(
    editingReportId ? `/reports/${editingReportId}` : '',
    { enabled: !!editingReportId && isEditModalOpen }
  );

  const reports = Array.isArray(reportsData)
    ? reportsData.filter((report) => !deletedReportIds.has(report.id))
    : [];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      // Check if click is outside all dropdown menus
      if (!target.closest('.dropdown-menu-container')) {
        setOpenMenuId(null);
      }
    };

    if (openMenuId) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [openMenuId]);

  const filteredReports = reports.filter(report => {
    if (filters.status && report.status !== filters.status) return false;
    if (filters.severity && report.severity !== filters.severity) return false;
    if (filters.search && !report.title.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  const handleViewReport = (reportId: string) => {
    setOpenMenuId(null);
    router.push(`/researcher/reports/${reportId}`);
  };

  const handleRowClick = (reportId: string) => {
    router.push(`/researcher/reports/${reportId}`);
  };

  const handleEditReport = (reportId: string) => {
    setOpenMenuId(null);
    setEditingReportId(reportId);
    setEditError('');
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingReportId(null);
    setEditError('');
  };

  const handleDeleteReport = async (reportId: string) => {
    setOpenMenuId(null);
    
    if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
      return;
    }

    try {
      setIsDeletingReportId(reportId);
      const response = await api.delete(`/reports/${reportId}`);

      if (response.status === 200 || response.status === 204) {
        setDeletedReportIds((current) => new Set(current).add(reportId));
        if (editingReportId === reportId) {
          handleCloseEditModal();
        }
        await refetch();
        alert('Report deleted successfully');
      }
    } catch (error: any) {
      console.error('Delete error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to delete report. Please try again.';
      alert(errorMessage);
    } finally {
      setIsDeletingReportId(null);
    }
  };

  const toggleMenu = (reportId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setOpenMenuId(openMenuId === reportId ? null : reportId);
  };

  useEffect(() => {
    if (!editingReport) {
      return;
    }

    setEditForm({
      title: editingReport.title || '',
      description: editingReport.description || '',
      steps_to_reproduce: editingReport.steps_to_reproduce || '',
      impact_assessment: editingReport.impact_assessment || '',
      suggested_severity: editingReport.suggested_severity || 'medium',
      affected_asset: editingReport.affected_asset || '',
      vulnerability_type: editingReport.vulnerability_type || '',
    });
  }, [editingReport]);

  const handleEditFieldChange = (field: keyof EditReportFormState, value: string) => {
    setEditForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmitEdit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!editingReportId) {
      return;
    }

    try {
      setIsSavingEdit(true);
      setEditError('');

      await api.put(`/reports/${editingReportId}`, {
        title: editForm.title.trim(),
        description: editForm.description.trim(),
        steps_to_reproduce: editForm.steps_to_reproduce.trim(),
        impact_assessment: editForm.impact_assessment.trim(),
        suggested_severity: editForm.suggested_severity,
        affected_asset: editForm.affected_asset.trim() || null,
        vulnerability_type: editForm.vulnerability_type.trim() || null,
      });

      setIsEditModalOpen(false);
      setEditingReportId(null);
      await refetch();
      alert('Report updated successfully');
    } catch (error: any) {
      setEditError(error.response?.data?.detail || 'Failed to update report. Please try again.');
    } finally {
      setIsSavingEdit(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
        Failed to load reports. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Filters */}
      <div className="rounded-2xl bg-[#faf6f1] dark:bg-[#111111] p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Search reports..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="rounded-xl border border-[#d8d0c8] dark:border-gray-700 bg-white dark:bg-neutral-900 px-4 py-2 text-sm text-[#2d2a26] dark:text-white placeholder:text-[#8b8177] dark:placeholder:text-gray-500 focus:border-[#c8bfb6] dark:focus:border-gray-600 focus:outline-none"
          />
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="rounded-xl border border-[#d8d0c8] dark:border-gray-700 bg-white dark:bg-neutral-900 px-4 py-2 text-sm text-[#2d2a26] dark:text-white focus:border-[#c8bfb6] dark:focus:border-gray-600 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="resolved">Resolved</option>
          </select>
          <select
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            className="rounded-xl border border-[#d8d0c8] dark:border-gray-700 bg-white dark:bg-neutral-900 px-4 py-2 text-sm text-[#2d2a26] dark:text-white focus:border-[#c8bfb6] dark:focus:border-gray-600 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Reports Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[#e6ddd4] dark:border-gray-800">
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">DATE</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">REPORT TITLE</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">PROGRAM</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">SEVERITY</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">STATUS</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26] dark:text-white">BOUNTY</th>
              <th className="pb-3 font-semibold text-[#2d2a26] dark:text-white">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filteredReports.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-10 text-center">
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177] dark:text-gray-400">
                    No results found
                  </p>
                  <p className="mt-2 text-[#6d6760] dark:text-gray-300">
                    {reports.length === 0
                      ? "You haven't submitted any reports yet. Start by submitting your first vulnerability report."
                      : 'No reports match your current filters.'}
                  </p>
                </td>
              </tr>
            ) : (
              filteredReports.map((report) => (
                <tr 
                  key={report.id} 
                  className="border-b border-[#e6ddd4] dark:border-gray-800 last:border-0 cursor-pointer hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
                  onClick={() => handleRowClick(report.id)}
                >
                  <td className="py-3 pr-4 text-[#6d6760] dark:text-gray-300">
                    {new Date(report.submitted_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </td>
                  <td className="py-3 pr-4 font-medium text-[#2d2a26] dark:text-white">{report.title}</td>
                  <td className="py-3 pr-4 text-[#6d6760] dark:text-gray-300">{report.program_name}</td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        severityTone[report.severity] || 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300'
                      }`}
                    >
                      {report.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        statusTone[report.status] || 'bg-[#f3ede6] dark:bg-neutral-800 text-[#5f5851] dark:text-gray-300'
                      }`}
                    >
                      {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-[#6d6760] dark:text-gray-300">
                    {report.bounty_amount ? `${report.bounty_amount} ETB` : '-'}
                  </td>
                  <td className="py-3" onClick={(e) => e.stopPropagation()}>
                    <div className="relative dropdown-menu-container">
                      <button
                        onClick={(e) => toggleMenu(report.id, e)}
                        className="inline-flex h-8 w-8 items-center justify-center rounded-full text-[#6d6760] dark:text-gray-300 transition hover:bg-[#f3ede6] dark:hover:bg-neutral-800"
                        aria-label="Actions"
                      >
                        <svg
                          className="h-5 w-5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <circle cx="10" cy="4" r="1.5" />
                          <circle cx="10" cy="10" r="1.5" />
                          <circle cx="10" cy="16" r="1.5" />
                        </svg>
                      </button>

                      {openMenuId === report.id && (
                        <div className="absolute right-0 z-10 mt-1 w-40 rounded-xl border border-[#e6ddd4] dark:border-gray-700 bg-white dark:bg-[#111111] shadow-lg">
                          <div className="py-1">
                            <button
                              onClick={() => handleViewReport(report.id)}
                              className="flex w-full items-center px-4 py-2 text-left text-sm text-[#2d2a26] dark:text-white transition hover:bg-[#faf6f1] dark:hover:bg-neutral-800"
                            >
                              <svg
                                className="mr-3 h-4 w-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                />
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                />
                              </svg>
                              View
                            </button>
                            {(report.status === 'new' || report.status === 'pending') && (
                              <>
                                <button
                                  onClick={() => handleEditReport(report.id)}
                                  className="flex w-full items-center px-4 py-2 text-left text-sm text-[#2d2a26] transition hover:bg-[#faf6f1]"
                                >
                                  <svg
                                    className="mr-3 h-4 w-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                    />
                                  </svg>
                                  Edit
                                </button>
                                <button
                                  onClick={() => handleDeleteReport(report.id)}
                                  disabled={isDeletingReportId === report.id}
                                  className="flex w-full items-center px-4 py-2 text-left text-sm text-[#b42318] transition hover:bg-[#fff2f1]"
                                >
                                  <svg
                                    className="mr-3 h-4 w-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                    />
                                  </svg>
                                  {isDeletingReportId === report.id ? 'Deleting...' : 'Delete'}
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      <Modal isOpen={isEditModalOpen} onClose={handleCloseEditModal} title="Edit Report" size="lg">
        {isLoadingEditingReport ? (
          <div className="flex justify-center py-12">
            <Spinner size="md" />
          </div>
        ) : (
          <form onSubmit={handleSubmitEdit} className="space-y-5">
            {editError ? (
              <div className="rounded-xl border border-[#f2c0bc] bg-[#fff2f1] px-4 py-3 text-sm text-[#b42318]">
                {editError}
              </div>
            ) : null}

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Title</label>
              <input
                type="text"
                value={editForm.title}
                onChange={(event) => handleEditFieldChange('title', event.target.value)}
    className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                required
                minLength={10}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Description</label>
              <textarea
                value={editForm.description}
                onChange={(event) => handleEditFieldChange('description', event.target.value)}
                rows={5}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                required
                minLength={50}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Steps To Reproduce</label>
              <textarea
                value={editForm.steps_to_reproduce}
                onChange={(event) => handleEditFieldChange('steps_to_reproduce', event.target.value)}
                rows={5}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                required
                minLength={20}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Impact Assessment</label>
              <textarea
                value={editForm.impact_assessment}
                onChange={(event) => handleEditFieldChange('impact_assessment', event.target.value)}
                rows={4}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                required
                minLength={20}
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Suggested Severity</label>
                <select
                  value={editForm.suggested_severity}
                  onChange={(event) => handleEditFieldChange('suggested_severity', event.target.value)}
                  className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Vulnerability Type</label>
                <input
                  type="text"
                  value={editForm.vulnerability_type}
                  onChange={(event) => handleEditFieldChange('vulnerability_type', event.target.value)}
                  className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#2d2a26]">Affected Asset</label>
              <input
                type="text"
                value={editForm.affected_asset}
                onChange={(event) => handleEditFieldChange('affected_asset', event.target.value)}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={handleCloseEditModal}
                className="rounded-full border border-[#d8d0c8] bg-[#faf6f1] px-5 py-2.5 text-sm font-semibold text-[#2d2a26] transition hover:bg-[#f3ede6]"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSavingEdit}
                className="rounded-full bg-[#ef2330] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c] disabled:opacity-60"
              >
                {isSavingEdit ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
