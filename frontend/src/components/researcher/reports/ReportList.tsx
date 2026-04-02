'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Spinner from '@/components/ui/Spinner';
import ReportDetailModal from './ReportDetailModal';

interface Report {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'pending' | 'approved' | 'rejected' | 'resolved';
  program_name: string;
  submitted_at: string;
  bounty_amount?: number;
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
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
    search: '',
  });
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: reportsData, isLoading, isError } = useApiQuery<Report[]>('/reports/my-reports', {
    enabled: true,
  });

  const reports = Array.isArray(reportsData) ? reportsData : [];

  const filteredReports = reports.filter(report => {
    if (filters.status && report.status !== filters.status) return false;
    if (filters.severity && report.severity !== filters.severity) return false;
    if (filters.search && !report.title.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  const handleViewReport = (reportId: string) => {
    setSelectedReportId(reportId);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedReportId(null);
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
      <div className="rounded-2xl bg-[#faf6f1] p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Search reports..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
          />
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
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
            className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
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
            <tr className="border-b border-[#e6ddd4]">
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">DATE</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">REPORT TITLE</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">PROGRAM</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">SEVERITY</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">STATUS</th>
              <th className="pb-3 pr-4 font-semibold text-[#2d2a26]">BOUNTY</th>
              <th className="pb-3 font-semibold text-[#2d2a26]">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filteredReports.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-10 text-center">
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
                    No results found
                  </p>
                  <p className="mt-2 text-sm text-[#6d6760]">
                    {reports.length === 0
                      ? "You haven't submitted any reports yet. Start by submitting your first vulnerability report."
                      : 'No reports match your current filters.'}
                  </p>
                </td>
              </tr>
            ) : (
              filteredReports.map((report) => (
                <tr key={report.id} className="border-b border-[#e6ddd4] last:border-0">
                  <td className="py-3 pr-4 text-[#6d6760]">
                    {new Date(report.submitted_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </td>
                  <td className="py-3 pr-4 font-medium text-[#2d2a26]">{report.title}</td>
                  <td className="py-3 pr-4 text-[#6d6760]">{report.program_name}</td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        severityTone[report.severity] || 'bg-[#f3ede6] text-[#5f5851]'
                      }`}
                    >
                      {report.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        statusTone[report.status] || 'bg-[#f3ede6] text-[#5f5851]'
                      }`}
                    >
                      {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-[#6d6760]">
                    {report.bounty_amount ? `$${report.bounty_amount.toLocaleString()}` : '-'}
                  </td>
                  <td className="py-3">
                    <button
                      onClick={() => handleViewReport(report.id)}
                      className="inline-flex rounded-full border border-[#d8d0c8] px-4 py-2 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Report Detail Modal */}
      <ReportDetailModal
        reportId={selectedReportId}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}
