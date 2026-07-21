'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Admin /bounties redirects to the Finance Officer portal,
 * which is the authoritative home for all bounty & payout management.
 */
export default function AdminBountiesRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/finance/payments?tab=bounty-payments&status=approved');
  }, [router]);

  return (
    <div className="min-h-screen bg-[#0F172A] flex items-center justify-center">
      <p className="text-[#94A3B8] text-sm">Redirecting to Finance Portal…</p>
    </div>
  );
}
