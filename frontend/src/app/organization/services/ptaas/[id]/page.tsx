'use client';

import { useParams } from 'next/navigation';
import { useApiQuery } from '@/hooks/useApiQuery';
import PTaaSEngagementDetail from '@/components/organization/services/ptaas/PTaaSEngagementDetail';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function PTaaSEngagementDetailPage() {
  const params = useParams();
  const engagementId = params.id as string;

  const { data: engagement, isLoading, error } = useApiQuery({
    endpoint: `/ptaas/engagements/${engagementId}`,
    queryKey: ['ptaas-engagement', engagementId],
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#faf6f1] p-6">
        <div className="mx-auto max-w-7xl">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-48 bg-[#e6ddd4] rounded" />
            <div className="h-64 bg-white rounded-2xl" />
            <div className="h-96 bg-white rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !engagement) {
    return (
      <div className="min-h-screen bg-[#faf6f1] p-6">
        <div className="mx-auto max-w-7xl">
          <Link
            href="/organization/services/ptaas"
            className="inline-flex items-center gap-2 text-sm text-[#6d6760] hover:text-[#2d2a26] mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to PTaaS Engagements
          </Link>
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
            <h2 className="text-lg font-semibold text-red-900 mb-2">Engagement Not Found</h2>
            <p className="text-sm text-red-700">
              The engagement you're looking for doesn't exist or you don't have permission to view it.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#faf6f1] p-6">
      <div className="mx-auto max-w-7xl">
        <Link
          href="/organization/services/ptaas"
          className="inline-flex items-center gap-2 text-sm text-[#6d6760] hover:text-[#2d2a26] mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to PTaaS Engagements
        </Link>
        
        <PTaaSEngagementDetail engagement={engagement} />
      </div>
    </div>
  );
}
