'use client';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface ResearcherPlaceholderPageProps {
  title: string;
  subtitle: string;
  description: string;
  workflow: string[];
  focusAreas: string[];
}

export default function ResearcherPlaceholderPage({
  title,
  subtitle,
  description,
  workflow,
  focusAreas,
}: ResearcherPlaceholderPageProps) {
  const user = useAuthStore((state) => state.user);

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell user={user} title={title} subtitle={subtitle} navItems={getPortalNavItems(user.role)}>
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
            <SectionCard title={`${title} Workflow`} description={description}>
              <div className="space-y-3">
                {workflow.map((step, index) => (
                  <div
                    key={step}
                    className="flex items-start gap-4 rounded-3xl border border-[#e6ddd4] bg-[#fcfaf7] p-4"
                  >
                    <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-[#fde9e7] text-sm font-semibold text-[#9d1f1f]">
                      {index + 1}
                    </span>
                    <p className="pt-1 text-sm leading-6 text-[#4f4943]">{step}</p>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard
              title="Implementation Focus"
              description="This keeps the new sidebar route live while the full workflow pages are being built."
            >
              <div className="space-y-3">
                {focusAreas.map((item) => (
                  <div key={item} className="rounded-2xl bg-[#faf6f1] px-4 py-4 text-sm leading-6 text-[#4f4943]">
                    {item}
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
