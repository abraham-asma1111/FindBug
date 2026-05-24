'use client';

import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';

export default function AdminReportDetailPage() {
  const user = useAuthStore((state) => state.user);
  const params = useParams();
  const reportId = params?.id as string;

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: report, isLoading } = useApiQuery<any>({
    endpoint: `/admin/reports/${reportId}`,
  });

  const getStatusBadge = (s: string) => {
    const map: Record<string, { bg: string; label: string }> = {
      new:       { bg: 'bg-[#3B82F6]', label: 'NEW' },
      submitted: { bg: 'bg-[#3B82F6]', label: 'SUBMITTED' },
      triaged:   { bg: 'bg-[#F59E0B]', label: 'TRIAGED' },
      valid:     { bg: 'bg-[#10B981]', label: 'VALID' },
      validated: { bg: 'bg-[#10B981]', label: 'VALID' },
      invalid:   { bg: 'bg-[#EF4444]', label: 'INVALID' },
      rejected:  { bg: 'bg-[#EF4444]', label: 'REJECTED' },
      duplicate: { bg: 'bg-[#94A3B8]', label: 'DUPLICATE' },
      resolved:  { bg: 'bg-[#8B5CF6]', label: 'RESOLVED' },
      closed:    { bg: 'bg-[#64748B]', label: 'CLOSED' },
    };
    const config = map[s] || { bg: 'bg-[#94A3B8]', label: s?.toUpperCase() || '—' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} text-white`}>
        {config.label}
      </span>
    );
  };

  const getSeverityBadge = (sev: string | null) => {
    if (!sev) return <span className="text-[#475569] text-sm">—</span>;
    const map: Record<string, string> = {
      critical: 'bg-[#DC2626]',
      high:     'bg-[#EA580C]',
      medium:   'bg-[#CA8A04]',
      low:      'bg-[#16A34A]',
      info:     'bg-[#0284C7]',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${map[sev] || 'bg-[#94A3B8]'} text-white`}>
        {sev.toUpperCase()}
      </span>
    );
  };

  const Field = ({ label, value }: { label: string; value: React.ReactNode }) => (
    <div className="py-3 border-b border-[#334155] last:border-0 flex flex-col sm:flex-row sm:items-start gap-1">
      <span className="text-xs font-semibold uppercase tracking-wide text-[#64748B] sm:w-44 shrink-0">{label}</span>
      <span className="text-sm text-[#F8FAFC]">{value ?? <span className="text-[#475569]">—</span>}</span>
    </div>
  );

  const TextBlock = ({ label, content, className = '' }: { label: string; content: string | null; className?: string }) => {
    if (!content) return null;
    return (
      <div className={`p-6 sm:p-8 ${className}`}>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-3">{label}</h2>
        <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap leading-relaxed">{content}</p>
      </div>
    );
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Report Detail"
          subtitle="Admin report detail"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          <div className="mb-4">
            <Link href="/admin/reports">
              <Button variant="outline" size="sm">← Back to Reports</Button>
            </Link>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading report…</p>
            </div>
          ) : !report ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#EF4444]">Report not found.</p>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden divide-y divide-[#334155]">
              {/* Header */}
              <div className="p-6 sm:p-8">
                <div className="flex flex-col gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    {report.report_number && (
                      <span className="text-xs text-[#64748B] font-mono">#{report.report_number}</span>
                    )}
                    {getStatusBadge(report.status)}
                    {getSeverityBadge(report.assigned_severity)}
                    {report.is_duplicate && (
                      <span className="px-2 py-1 rounded text-xs font-bold bg-[#78350F] text-[#FDE68A]">DUPLICATE</span>
                    )}
                    {report.bounty_status && (
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                        report.bounty_status === 'paid' || report.bounty_status === 'approved'
                          ? 'bg-[#10B981]/20 text-[#10B981]'
                          : 'bg-[#F59E0B]/20 text-[#F59E0B]'
                      }`}>
                        Bounty: {report.bounty_status}
                      </span>
                    )}
                  </div>
                  <h1 className="text-2xl font-bold text-[#F8FAFC]">{report.title}</h1>
                  <p className="text-sm text-[#94A3B8]">
                    {report.researcher_name || 'Unknown researcher'}
                    {report.program_name ? ` · ${report.program_name}` : ''}
                    {report.organization_name ? ` · ${report.organization_name}` : ''}
                  </p>
                </div>
              </div>

              {/* Metadata */}
              <div className="p-6 sm:p-8 bg-[#0F172A]/30">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-4">Report Metadata</h2>
                <Field label="Report ID" value={<code className="text-xs text-[#94A3B8]">{report.id}</code>} />
                <Field label="Researcher" value={report.researcher_name} />
                <Field label="Program" value={
                  report.program_id
                    ? <Link href={`/admin/programs/${report.program_id}`} className="text-[#3B82F6] hover:underline">{report.program_name || report.program_id}</Link>
                    : null
                } />
                <Field label="Organization" value={report.organization_name} />
                <Field label="Vulnerability Type" value={report.vulnerability_type} />
                <Field label="Affected Asset" value={report.affected_asset} />
                <Field label="VRT Category" value={report.vrt_category} />
                <Field label="Suggested Severity" value={getSeverityBadge(report.suggested_severity)} />
                <Field label="Assigned Severity" value={getSeverityBadge(report.assigned_severity)} />
                <Field label="CVSS Score" value={report.cvss_score != null ? report.cvss_score : null} />
                <Field label="Bounty Amount" value={report.bounty_amount != null ? `${Number(report.bounty_amount).toLocaleString()} ETB` : null} />
                <Field label="Submitted" value={report.submitted_at ? new Date(report.submitted_at).toLocaleString() : null} />
                <Field label="Triaged At" value={report.triaged_at ? new Date(report.triaged_at).toLocaleString() : null} />
                <Field label="Resolved At" value={report.resolved_at ? new Date(report.resolved_at).toLocaleString() : null} />
              </div>

              {/* Report Content */}
              <TextBlock label="Description" content={report.description} />
              <TextBlock label="Steps to Reproduce" content={report.steps_to_reproduce} className="bg-[#0F172A]/30" />
              <TextBlock label="Impact Assessment" content={report.impact_assessment} />

              {/* Triage Notes */}
              {report.triage_notes && (
                <div className="p-6 sm:p-8 bg-[#0F172A]/30">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-[#F59E0B] mb-3">Triage Notes</h2>
                  <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap leading-relaxed">{report.triage_notes}</p>
                </div>
              )}

              {/* Comments */}
              {report.comments?.length > 0 && (
                <div className={`p-6 sm:p-8 ${!report.triage_notes ? 'bg-[#0F172A]/30' : ''}`}>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-4">
                    Comments ({report.comments.length})
                  </h2>
                  <div className="space-y-4">
                    {report.comments.map((c: any) => (
                      <div key={c.id} className={`rounded-lg p-4 border ${
                        c.is_internal
                          ? 'border-[#78350F] bg-[#78350F]/10'
                          : 'border-[#334155] bg-[#0F172A]'
                      }`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-[#94A3B8] uppercase">{c.author_role}</span>
                          <div className="flex items-center gap-2">
                            {c.is_internal && (
                              <span className="text-xs bg-[#78350F] text-[#FDE68A] px-2 py-0.5 rounded font-bold">INTERNAL</span>
                            )}
                            <span className="text-xs text-[#475569]">
                              {c.created_at ? new Date(c.created_at).toLocaleString() : ''}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap">{c.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
