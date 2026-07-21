'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { labsHubUrl } from '@/lib/simulation-lab';

/** Legacy per-challenge lab URL → unified lab hub with focus. */
export default function LegacyLabRedirectPage() {
  const params = useParams();
  const router = useRouter();
  const challengeId = params.id as string;

  useEffect(() => {
    router.replace(labsHubUrl(challengeId));
  }, [challengeId, router]);

  return (
    <div className="flex justify-center py-32 text-gray-500 text-sm">
      Redirecting to lab environment…
    </div>
  );
}
