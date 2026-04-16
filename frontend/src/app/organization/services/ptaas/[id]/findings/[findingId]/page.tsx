'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import PTaaSFindingDetailView from '@/components/organization/services/ptaas/findings/PTaaSFindingDetailView';

export default function PTaaSFindingDetailPage() {
  const params = useParams();
  const engagementId = params.id as string;
  const findingId = params.findingId as string;

  return (
    <div className="min-h-screen bg-[#faf6f1] p-6">
      <div className="mx-auto max-w-7xl">
        <Link
          href={`/organization/services/ptaas/${engagementId}/findings`}
          className="inline-flex items-center gap-2 text-sm text-[#6d6760] hover:text-[#2d2a26] mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Findings
        </Link>
        
        <PTaaSFindingDetailView engagementId={engagementId} findingId={findingId} />
      </div>
    </div>
  );
}
