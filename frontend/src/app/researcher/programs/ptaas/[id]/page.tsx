'use client';

import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import ResearcherPTaaSEngagementDetail from '@/components/researcher/ptaas/ResearcherPTaaSEngagementDetail';
import Button from '@/components/ui/Button';

export default function ResearcherPTaaSEngagementDetailPage() {
  const params = useParams();
  const engagementId = params.id as string;
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="PTaaS Engagement"
          subtitle="Testing workspace and collaboration"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            <Button
              variant="outline"
              onClick={() => router.push('/researcher/programs/ptaas')}
            >
              ← Back to PTaaS Engagements
            </Button>
            <ResearcherPTaaSEngagementDetail engagementId={engagementId} />
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
