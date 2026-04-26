'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function FinanceSidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path || pathname.startsWith(`${path}/`);

  return (
    <aside className="w-64 bg-[#020617] border-r border-[#1E293B] min-h-screen sticky top-0">
      {/* Logo */}
      <div className="p-6 border-b border-[#1E293B]">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#EF2330] rounded-lg flex items-center justify-center text-white font-bold text-lg">
            F
          </div>
          <span className="text-[#F8FAFC] font-bold text-lg">FindBug</span>
        </Link>
      </div>

      <nav className="p-4">
        {/* Main Navigation */}
        <div className="mb-6">
          <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
            Main
          </h3>
          <div className="space-y-1">
            <Link
              href="/finance/dashboard"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/dashboard')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Dashboard
            </Link>
          </div>
        </div>

        {/* Payments Section */}
        <div className="mb-6 pt-6 border-t border-[#1E293B]">
          <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
            Payments
          </h3>
          <div className="space-y-1">
            <Link
              href="/finance/payments?status=pending"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/payments')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
              Bounty Payments
            </Link>
            <Link
              href="/finance/payouts?status=requested"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/payouts')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-[#3B82F6]"></span>
              Payouts
            </Link>
            <Link
              href="/finance/kyc?status=pending"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/kyc')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
              KYC Verification
            </Link>
          </div>
        </div>

        {/* Reports Section */}
        <div className="mb-6 pt-6 border-t border-[#1E293B]">
          <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
            Reports
          </h3>
          <div className="space-y-1">
            <Link
              href="/finance/reports"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/reports')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Financial Reports
            </Link>
            <Link
              href="/finance/analytics"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/analytics')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Analytics
            </Link>
          </div>
        </div>

        {/* Management Section */}
        <div className="pt-6 border-t border-[#1E293B]">
          <h3 className="text-xs font-bold uppercase tracking-wide text-[#64748B] mb-3 px-3">
            Management
          </h3>
          <div className="space-y-1">
            <Link
              href="/finance/billing"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/billing')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Billing
            </Link>
            <Link
              href="/finance/settings"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                isActive('/finance/settings')
                  ? 'bg-[#1E40AF] text-[#F8FAFC]'
                  : 'text-[#94A3B8] hover:bg-[#334155] hover:text-[#F8FAFC]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </Link>
          </div>
        </div>
      </nav>
    </aside>
  );
}
