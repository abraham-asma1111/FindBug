'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

interface FinanceHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function FinanceHeader({ title, subtitle, actions }: FinanceHeaderProps) {
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    router.replace('/auth/login');
  };

  return (
    <header className="bg-[#020617] border-b border-[#1E293B] px-8 py-4 sticky top-0 z-10">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-[#64748B]">Finance Portal</p>
          <h1 className="text-2xl font-bold text-[#F8FAFC] mt-1">{title}</h1>
          {subtitle && <p className="text-sm text-[#94A3B8] mt-1">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-3">
          {actions}
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-[#EF2330] hover:bg-[#DC2026] text-white rounded-lg text-sm font-medium transition"
          >
            Log Out
          </button>
        </div>
      </div>
    </header>
  );
}
