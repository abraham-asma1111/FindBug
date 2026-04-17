'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { AlertCircle, ChevronLeft, Save, CheckCircle, XCircle, Copy } from 'lucide-react';
import Link from 'next/link';

interface ReportDetail {
  id: string;
  report_number: string;
  title: string;
  description: string;
  status: string;
  assigned_severity: string | null;
  suggested_severity: string;
  cvss_score: number | null;
  vrt_category: string | null;
  bounty_amount: number | null;
  submitted_at: string;
  triaged_at: string | null;
  triaged_by: string | null;
  is_duplicate: boolean;
  duplicate_of: string | null;
  triage_notes: string | null;
  program_id: string;
  researcher_id: string;
}

const severityColors: Record<string, string> = {
  critical: 'bg-[#EF4444] text-white',
  high: 'bg-[#F59E0B] text-white',
  medium: 'bg-[#F59E0B] text-white',
  low: 'bg-[#3B82F6] text-white',
  info: 'bg-[#94A3B8] text-white',
};

const statusColors: Record<string, string> = {
  new: 'bg-[#EF4444] text-white',
  triaged: 'bg-[#F59E0B] text-white',
  valid: 'bg-[#3B82F6] text-white',
  invalid: 'bg-[#EF4444] text-white',
  duplicate: 'bg-[#94A3B8] text-white',
  resolved: 'bg-[#3B82F6] text-white',
};

export default function TriageReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.id as string;
  const user = useAuthStore((state) => state.user);

  // Force dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Form state
  const [status, setStatus] = useState('');
  const [assignedSeverity, setAssignedSeverity] = useState('');
  const [cvssScore, setCvssScore] = useState('');
  const [vrtCategory, setVrtCategory] = useState('');
  const [triageNotes, setTriageNotes] = useState('');
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [duplicateOf, setDuplicateOf] = useState('');

  const { data: report, isLoading, error, refetch } = useApiQuery<ReportDetail>({
    endpoint: `/triage/queue?report_id=${reportId}`,
  });

  // Initialize form when report loads
  useEffect(() => {
    if (report) {
      const reportData = Array.isArray(report) ? report[0] : report;
      setStatus(reportData.status || '');
      setAssignedSeverity(reportData.assigned_severity || reportData.suggested_severity || '');
      setCvssScore(reportData.cvss_score?.toString() || '');
      setVrtCategory(reportData.vrt_category || '');
      setTriageNotes(reportData.triage_notes || '');
      setIsDuplicate(reportData.is_duplicate || false);
      setDuplicateOf(reportData.duplicate_of || '');
    }
  }, [report]);

  const updateMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      alert('Report updated successfully');
    },
    onError: (error) => {
      alert(`Failed to update report: ${error.message}`);
    },
  });

  const acknowledgeMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      alert('Report acknowledged successfully');
    },
  });

  const resolveMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      alert('Report resolved successfully');
    },
  });

  const handleUpdate = () => {
    updateMutation.mutate({
      endpoint: `/triage/reports/${reportId}/update`,
      data: {
        status,
        assigned_severity: assignedSeverity,
        cvss_score: cvssScore ? parseFloat(cvssScore) : null,
        vrt_category: vrtCategory || null,
        triage_notes: triageNotes || null,
        is_duplicate: isDuplicate,
        duplicate_of: duplicateOf || null,
      },
    });
  };

  const handleAcknowledge = () => {
    acknowledgeMutation.mutate({
      endpoint: `/triage/reports/${reportId}/acknowledge`,
      data: {},
    });
  };

  const handleResolve = () => {
    resolveMutation.mutate({
      endpoint: `/triage/reports/${reportId}/resolve`,
      data: {
        resolution_notes: triageNotes,
      },
    });
  };

  const reportData = Array.isArray(report) ? report[0] : report;

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Report Details"
          subtitle="Review and validate report"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2">
            <Link href="/triage/queue" className="text-[#3B82F6] hover:underline text-sm">
              Queue
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">Report Details</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading report...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
                <p className="text-[#EF4444]">Failed to load report</p>
              </div>
            </div>
          ) : reportData ? (
            <div className="space-y-6">
              {/* Report Header */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                      {reportData.title}
                    </h2>
                    <div className="flex items-center gap-3 text-sm text-[#94A3B8]">
                      <span className="flex items-center gap-1">
                        <Copy className="w-4 h-4" />
                        {reportData.report_number}
                      </span>
                      <span>•</span>
                      <span>Submitted {new Date(reportData.submitted_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${statusColors[reportData.status] || 'bg-[#94A3B8] text-white'}`}>
                      {reportData.status}
                    </span>
                    <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${severityColors[reportData.assigned_severity?.toLowerCase() || reportData.suggested_severity?.toLowerCase() || 'info']}`}>
                      {reportData.assigned_severity || reportData.suggested_severity}
                    </span>
                  </div>
                </div>
                <div className="prose prose-invert max-w-none">
                  <p className="text-[#F8FAFC] leading-relaxed whitespace-pre-wrap">
                    {reportData.description}
                  </p>
                </div>
              </div>

              {/* Triage Form */}
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <h3 className="text-lg font-semibold text-[#F8FAFC] mb-4">Triage Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Status
                    </label>
                    <Select
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                      options={[
                        { value: 'new', label: 'New' },
                        { value: 'triaged', label: 'Triaged' },
                        { value: 'valid', label: 'Valid' },
                        { value: 'invalid', label: 'Invalid' },
                        { value: 'duplicate', label: 'Duplicate' },
                        { value: 'resolved', label: 'Resolved' },
                      ]}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      Assigned Severity
                    </label>
                    <Select
                      value={assignedSeverity}
                      onChange={(e) => setAssignedSeverity(e.target.value)}
                      options={[
                        { value: 'critical', label: 'Critical' },
                        { value: 'high', label: 'High' },
                        { value: 'medium', label: 'Medium' },
                        { value: 'low', label: 'Low' },
                        { value: 'info', label: 'Info' },
                      ]}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      CVSS Score (0-10)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={cvssScore}
                      onChange={(e) => setCvssScore(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                      VRT Category
                    </label>
                    <input
                      type="text"
                      value={vrtCategory}
                      onChange={(e) => setVrtCategory(e.target.value)}
                      placeholder="e.g., server_security_misconfiguration"
                      className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="flex items-center gap-2 text-sm font-medium text-[#94A3B8] mb-2">
                    <input
                      type="checkbox"
                      checked={isDuplicate}
                      onChange={(e) => setIsDuplicate(e.target.checked)}
                      className="rounded border-[#334155] bg-[#0F172A] text-[#3B82F6] focus:ring-[#3B82F6]"
                    />
                    Mark as Duplicate
                  </label>
                  {isDuplicate && (
                    <input
                      type="text"
                      value={duplicateOf}
                      onChange={(e) => setDuplicateOf(e.target.value)}
                      placeholder="Original Report ID"
                      className="w-full px-3 py-2 rounded-lg border border-[#334155] bg-[#0F172A] text-[#F8FAFC] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#3B82F6] focus:border-transparent"
                    />
                  )}
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                    Triage Notes
                  </label>
                  <Textarea
                    value={triageNotes}
                    onChange={(e) => setTriageNotes(e.target.value)}
                    rows={4}
                    placeholder="Add notes about your triage decision..."
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={handleUpdate}
                    disabled={updateMutation.isLoading}
                    className="gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  
                  {reportData.status === 'new' && (
                    <Button
                      onClick={handleAcknowledge}
                      disabled={acknowledgeMutation.isLoading}
                      variant="outline"
                      className="gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Acknowledge
                    </Button>
                  )}
                  
                  {reportData.status !== 'resolved' && (
                    <Button
                      onClick={handleResolve}
                      disabled={resolveMutation.isLoading}
                      variant="outline"
                      className="gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Mark Resolved
                    </Button>
                  )}
                </div>
              </div>

              {/* Report Info Grid */}
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Bounty</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.bounty_amount ? `$${reportData.bounty_amount.toLocaleString()}` : 'TBD'}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">CVSS Score</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.cvss_score || '-'}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Triaged At</p>
                  <p className="mt-2 text-sm text-[#F8FAFC]">
                    {reportData.triaged_at ? new Date(reportData.triaged_at).toLocaleDateString() : 'Not yet'}
                  </p>
                </div>
                <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                  <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">Duplicate</p>
                  <p className="mt-2 text-lg font-bold text-[#F8FAFC]">
                    {reportData.is_duplicate ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Link href="/triage/queue">
                  <Button variant="outline" className="gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Queue
                  </Button>
                </Link>
              </div>
            </div>
          ) : null}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
