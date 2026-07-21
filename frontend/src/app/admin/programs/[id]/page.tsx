'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

const STATUS_OPTIONS = ['draft', 'public', 'private', 'paused', 'archived'];

export default function AdminProgramDetailPage() {
  const user = useAuthStore((state) => state.user);
  const params = useParams();
  const programId = params?.id as string;

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: program, isLoading, refetch } = useApiQuery<any>({
    endpoint: `/admin/programs/${programId}`,
  });

  const [newStatus, setNewStatus] = useState('');
  const [actionPending, setActionPending] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (program?.status) setNewStatus(program.status);
  }, [program]);

  const handleStatusUpdate = async () => {
    if (!newStatus || newStatus === program?.status) return;
    setActionPending(true);
    setMessage(null);
    try {
      await api.post(`/admin/programs/${programId}/status?new_status=${newStatus}`);
      setMessage({ type: 'success', text: `Program status updated to "${newStatus}".` });
      refetch?.();
    } catch {
      setMessage({ type: 'error', text: 'Action failed. Please try again.' });
    } finally {
      setActionPending(false);
    }
  };

  const getStatusBadge = (s: string) => {
    const map: Record<string, string> = {
      draft:    'bg-[#94A3B8]',
      public:   'bg-[#10B981]',
      active:   'bg-[#10B981]',
      private:  'bg-[#3B82F6]',
      paused:   'bg-[#F59E0B]',
      archived: 'bg-[#64748B]',
      closed:   'bg-[#EF4444]',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${map[s] || 'bg-[#94A3B8]'} text-white`}>
        {s?.toUpperCase() || '—'}
      </span>
    );
  };

  const Field = ({ label, value }: { label: string; value: React.ReactNode }) => (
    <div className="py-3 border-b border-[#334155] last:border-0 flex flex-col sm:flex-row sm:items-start gap-1">
      <span className="text-xs font-semibold uppercase tracking-wide text-[#64748B] sm:w-44 shrink-0">{label}</span>
      <span className="text-sm text-[#F8FAFC]">{value ?? <span className="text-[#475569]">—</span>}</span>
    </div>
  );

  const StatusPill = ({ label, count }: { label: string; count: number }) => (
    <div className="bg-[#0F172A] rounded-lg p-3 text-center border border-[#334155]">
      <p className="text-xl font-bold text-[#F8FAFC]">{count}</p>
      <p className="text-xs text-[#64748B] mt-1 capitalize">{label}</p>
    </div>
  );

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Program Detail"
          subtitle="Admin program detail"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          <div className="mb-4">
            <Link href="/admin/programs">
              <Button variant="outline" size="sm">← Back to Programs</Button>
            </Link>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading program…</p>
            </div>
          ) : !program ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#EF4444]">Program not found.</p>
            </div>
          ) : (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden divide-y divide-[#334155]">
              {/* Header */}
              <div className="p-6 sm:p-8">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold text-[#F8FAFC]">{program.name}</h1>
                    <p className="text-sm text-[#94A3B8] mt-1">
                      {program.organization_name || 'Unknown Organization'}
                    </p>
                    <div className="mt-2 flex items-center gap-2 flex-wrap">
                      {getStatusBadge(program.status)}
                      {program.visibility && (
                        <span className="px-2 py-1 rounded text-xs font-bold uppercase bg-[#1E3A5F] text-[#93C5FD]">
                          {program.visibility}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* Status Management */}
                  <div className="flex items-center gap-2 shrink-0">
                    <select
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value)}
                      className="rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] focus:border-[#EF2330] focus:outline-none"
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                      ))}
                    </select>
                    <Button
                      variant="primary"
                      size="sm"
                      disabled={actionPending || newStatus === program.status}
                      onClick={handleStatusUpdate}
                      className="bg-[#EF2330] hover:bg-[#DC2026] disabled:opacity-40"
                    >
                      {actionPending ? '…' : 'Update'}
                    </Button>
                  </div>
                </div>

                {message && (
                  <div className={`mt-4 rounded-md px-4 py-2 text-sm font-medium ${
                    message.type === 'success' ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-[#EF4444]/20 text-[#EF4444]'
                  }`}>
                    {message.text}
                  </div>
                )}
              </div>

              {/* Reports Summary */}
              <div className="p-6 sm:p-8 bg-[#0F172A]/30">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-4">
                  Reports — {program.total_reports} Total
                </h2>
                {program.report_counts_by_status && Object.keys(program.report_counts_by_status).length > 0 ? (
                  <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
                    {Object.entries(program.report_counts_by_status).map(([st, cnt]) => (
                      <StatusPill key={st} label={st} count={cnt as number} />
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-[#64748B]">No reports submitted yet.</p>
                )}
              </div>

              {/* Program Details */}
              <div className="p-6 sm:p-8">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-4">Program Details</h2>
                <Field label="Program ID" value={<code className="text-xs text-[#94A3B8]">{program.id}</code>} />
                <Field label="Organization" value={program.organization_name} />
                <Field label="Budget" value={program.budget != null ? `${Number(program.budget).toLocaleString()} ETB` : null} />
                <Field label="Visibility" value={program.visibility} />
                <Field label="Created" value={program.created_at ? new Date(program.created_at).toLocaleString() : null} />
                <Field label="Updated" value={program.updated_at ? new Date(program.updated_at).toLocaleString() : null} />
              </div>

              {/* Policy */}
              {program.policy && (
                <div className="p-6 sm:p-8 bg-[#0F172A]/30">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-3">Policy</h2>
                  <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap leading-relaxed">{program.policy}</p>
                </div>
              )}

              {/* Scope */}
              {program.scope && (
                <div className="p-6 sm:p-8">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-3">In Scope</h2>
                  <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap leading-relaxed">{program.scope}</p>
                </div>
              )}

              {/* Out of Scope */}
              {program.out_of_scope && (
                <div className="p-6 sm:p-8 bg-[#0F172A]/30">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-3">Out of Scope</h2>
                  <p className="text-sm text-[#CBD5E1] whitespace-pre-wrap leading-relaxed">{program.out_of_scope}</p>
                </div>
              )}

              {/* Quick links */}
              <div className="p-6 sm:p-8">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94A3B8] mb-3">Quick Links</h2>
                <Link href={`/admin/reports?program_id=${program.id}`}>
                  <Button variant="outline" size="sm">View All Reports for this Program</Button>
                </Link>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
