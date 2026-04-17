'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ResearcherProgramsPage() {
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to engagements page which shows all programs
    router.push('/researcher/engagements');
  }, [router]);
  
  return null;
}
