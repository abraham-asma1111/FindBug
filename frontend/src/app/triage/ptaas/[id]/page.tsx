'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getTriageReportDetailPath } from '@/lib/triageRoutes';

/** Legacy route — PTaaS findings use the same detail URL as bounty reports. */
export default function TriagePTaaSLegacyRedirect() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  useEffect(() => {
    if (id) {
      router.replace(getTriageReportDetailPath(id));
    }
  }, [id, router]);

  return null;
}
