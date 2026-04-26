'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import { useAuthStore } from '@/store/authStore';
import FinanceSidebar from './FinanceSidebar';
import FinanceHeader from './FinanceHeader';

interface FinanceLayoutProps {
  title: string;
  subtitle?: string;
  headerActions?: React.ReactNode;
  children: React.ReactNode;
}

export default function FinanceLayout({ title, subtitle, headerActions, children }: FinanceLayoutProps) {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <div className="min-h-screen bg-[#0F172A]">
          <div className="flex">
            <FinanceSidebar />
            <div className="flex-1">
              <FinanceHeader title={title} subtitle={subtitle} actions={headerActions} />
              <main className="p-8">{children}</main>
            </div>
          </div>
        </div>
      ) : null}
    </ProtectedRoute>
  );
}
