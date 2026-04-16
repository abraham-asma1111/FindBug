'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import PTaaSTeamView from '@/components/organization/services/ptaas/team/PTaaSTeamView';

export default function PTaaSTeamPage() {
  const params = useParams();
  const engagementId = params.id as string;

  return (
    <div className="min-h-screen bg-[#faf6f1] p-6">
      <div className="mx-auto max-w-7xl">
        <Link
          href={`/organization/services/ptaas/${engagementId}`}
          className="inline-flex items-center gap-2 text-sm text-[#6d6760] hover:text-[#2d2a26] mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Engagement
        </Link>
        
        <PTaaSTeamView engagementId={engagementId} />
      </div>
    </div>
  );
}
