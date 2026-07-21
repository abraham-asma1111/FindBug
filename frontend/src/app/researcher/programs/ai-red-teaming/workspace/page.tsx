'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/** Legacy route — workspace lives on the main AI Red Teaming page. */
export default function AIRedTeamingWorkspaceRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/researcher/programs/ai-red-teaming');
  }, [router]);

  return null;
}
