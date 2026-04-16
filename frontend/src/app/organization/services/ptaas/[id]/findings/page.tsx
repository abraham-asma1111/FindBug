'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import PTaaSFindingsView from '@/components/organization/services/ptaas/findings/PTaaSFindingsView';

export default function PTaaSFindingsPage() {
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
        
        <PTaaSFindingsView engagementId={engagementId} />
      </div>
    </div>
  );
}
