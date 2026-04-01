'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import { getDashboardRouteForRole } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

function DashboardRedirect() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (user) {
      router.replace(getDashboardRouteForRole(user.role));
    }
  }, [router, user]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-100">
      <div className="rounded-3xl border border-stone-200 bg-white px-6 py-5 text-sm text-stone-600 shadow-sm">
        Redirecting to your portal...
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardRedirect />
    </ProtectedRoute>
  );
}
