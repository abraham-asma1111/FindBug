'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { invalidateAllTriageData } from '@/lib/cacheManager';
import { useQueryClient } from '@tanstack/react-query';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { AlertCircle, ChevronLeft } from 'lucide-react';

interface PTaaSFinding {
  id: string;
  engagement_id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  cvss_score?: number | null;
  vulnerability_type?: string | null;
  remediation?: string | null;
  discovered_at?: string;
}

export default function TriagePTaaSFindingPage() {
  const params = useParams();
  const findingId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const [validated, setValidated] = useState<'true' | 'false'>('true');
  const [retestRequired, setRetestRequired] = useState(false);
  const [retestNotes, setRetestNotes] = useState('');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const { data: finding, isLoading, error, refetch } = useApiQuery<PTaaSFinding>({
    endpoint: `/ptaas/findings/${findingId}`,
    enabled: !!findingId,
  });

  const validateMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      refetch();
      invalidateAllTriageData(queryClient);
      alert('PTaaS finding updated successfully');
    },
    onError: (err: { response?: { data?: { detail?: string } }; message?: string }) => {
      alert(err?.response?.data?.detail || err.message || 'Failed to update finding');
    },
  });

  const handleValidate = () => {
    validateMutation.mutate({
      endpoint: `/ptaas/findings/${findingId}/validate`,
      validated: validated === 'true',
      retest_required: retestRequired,
      retest_notes: retestNotes || undefined,
    });
  };

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Finding"
          subtitle="Review penetration test finding"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle
        >
          <div className="mb-6 flex items-center gap-2">
            <Link href="/triage/queue" className="text-[#3B82F6] hover:underline text-sm">
              Queue
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#94A3B8] text-sm">PTaaS Finding</span>
          </div>

          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <p className="text-[#94A3B8]">Loading finding...</p>
            </div>
          ) : error || !finding ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-[#EF4444]" />
                <p className="text-[#EF4444]">Failed to load PTaaS finding</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6">
                <p className="text-xs font-mono text-[#3B82F6] mb-2">PTAAS-{finding.id.slice(0, 8).toUpperCase()}</p>
                <h1 className="text-2xl font-bold text-[#F8FAFC] mb-2">{finding.title}</h1>
                <p className="text-sm text-[#94A3B8] mb-4">
                  Status: <span className="text-[#F8FAFC]">{finding.status}</span>
                  {' · '}
                  Severity: <span className="text-[#F8FAFC]">{finding.severity}</span>
                </p>
                <p className="text-[#CBD5E1] whitespace-pre-wrap">{finding.description}</p>
                {finding.remediation && (
                  <div className="mt-4">
                    <h3 className="text-sm font-semibold text-[#94A3B8] mb-1">Remediation</h3>
                    <p className="text-[#CBD5E1] whitespace-pre-wrap">{finding.remediation}</p>
                  </div>
                )}
              </div>

              <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 space-y-4">
                <h2 className="text-lg font-semibold text-[#F8FAFC]">Triage decision</h2>
                <Select
                  label="Validation"
                  value={validated}
                  onChange={(e) => setValidated(e.target.value as 'true' | 'false')}
                  options={[
                    { value: 'true', label: 'Valid finding' },
                    { value: 'false', label: 'Invalid / reject' },
                  ]}
                />
                <label className="flex items-center gap-2 text-sm text-[#F8FAFC]">
                  <input
                    type="checkbox"
                    checked={retestRequired}
                    onChange={(e) => setRetestRequired(e.target.checked)}
                    className="rounded border-[#334155]"
                  />
                  Request retest
                </label>
                <Textarea
                  label="Notes"
                  value={retestNotes}
                  onChange={(e) => setRetestNotes(e.target.value)}
                  rows={4}
                />
                <div className="flex gap-3">
                  <Button onClick={handleValidate} disabled={validateMutation.isPending}>
                    Save triage
                  </Button>
                  <Link href="/triage/queue">
                    <Button variant="outline" className="gap-2">
                      <ChevronLeft className="w-4 h-4" />
                      Back to queue
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
