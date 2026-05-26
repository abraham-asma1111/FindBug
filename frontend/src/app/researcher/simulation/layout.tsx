'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/common/ProtectedRoute';

const academyNav = [
  {
    label: 'LEARN',
    items: [
      { href: '/researcher/simulation', label: 'Challenge Catalog' },
      { href: '/researcher/simulation/labs', label: 'Lab Environment' },
    ]
  },
  {
    label: 'PROGRESS',
    items: [
      { href: '/researcher/simulation/my-progress', label: 'My Progress & XP' },
      { href: '/researcher/simulation/leaderboard', label: 'Global Leaderboard' },
    ]
  },
  {
    label: 'TIERS',
    items: [
      { href: '/researcher/simulation?difficulty=beginner', label: 'Beginner' },
      { href: '/researcher/simulation?difficulty=intermediate', label: 'Intermediate' },
      { href: '/researcher/simulation?difficulty=advanced', label: 'Advanced' },
    ]
  },
];

export default function SimulationAcademyLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLabsHub = pathname?.startsWith('/researcher/simulation/labs');
  const user = useAuthStore((state) => state.user);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isActive = (href: string) => {
    const base = href.split('?')[0];
    if (base === '/researcher/simulation') return pathname === '/researcher/simulation';
    return pathname === base || pathname.startsWith(`${base}/`);
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      <div className="min-h-screen bg-[#0d0d0d] text-white flex flex-col">
        
        {/* Top Bar */}
        <header className="h-14 bg-[#111111] border-b border-gray-800 flex items-center px-6 z-30 fixed top-0 left-0 right-0 shadow-md">
          <div className="flex items-center gap-6 flex-1">
            {/* Mobile menu toggle */}
            <button
              type="button"
              className={`text-gray-400 hover:text-white ${isLabsHub ? '' : 'lg:hidden'}`}
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="Open academy menu"
            >
              ☰
            </button>
            
            {/* Academy Brand */}
            <Link href="/researcher/simulation" className="flex items-center gap-2 group">
              <div className="w-7 h-7 rounded bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-black font-black text-xs">
                BB
              </div>
              <span className="font-semibold text-white text-sm tracking-tight hidden sm:inline">
                Bug Bounty Academy
              </span>
            </Link>

            {/* Back to Portal */}
            <Link 
              href="/researcher/dashboard"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors hidden sm:inline-flex items-center gap-1"
            >
              ← Researcher Portal
            </Link>
          </div>

          {/* User Info */}
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-400 text-xs hidden md:inline">{user?.email}</span>
          </div>
        </header>

        <div className="flex flex-1 pt-14">
          {/* Sidebar — on labs hub, drawer only (page has its own lab menu) */}
          <aside
            className={`fixed top-14 left-0 bottom-0 w-56 bg-[#111111] border-r border-gray-800 overflow-y-auto z-20 transition-transform ${
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            } ${isLabsHub ? '' : 'lg:translate-x-0'}`}
          >
            <nav className="p-4 space-y-6">
              {academyNav.map((section) => (
                <div key={section.label}>
                  <p className="text-[10px] font-semibold text-gray-600 uppercase tracking-widest mb-2 px-2">
                    {section.label}
                  </p>
                  <ul className="space-y-0.5">
                    {section.items.map((item) => (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          onClick={() => setSidebarOpen(false)}
                          className={`block px-3 py-2 rounded-lg text-sm transition-all ${
                            isActive(item.href)
                              ? 'bg-emerald-500/15 text-emerald-400 font-medium border border-emerald-500/20'
                              : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
                          }`}
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}

              {/* Separator */}
              <div className="border-t border-gray-800 pt-4">
                <p className="text-[10px] font-semibold text-gray-600 uppercase tracking-widest mb-2 px-2">
                  CATEGORIES
                </p>
                <ul className="space-y-0.5">
                  {[
                    { label: 'Web Security', slug: 'web' },
                    { label: 'API Security', slug: 'api' },
                    { label: 'Authentication', slug: 'auth' },
                    { label: 'Access Control', slug: 'access_control' },
                  ].map((cat) => (
                    <li key={cat.slug}>
                      <Link
                        href={`/researcher/simulation?category=${cat.slug}`}
                        className="block px-3 py-2 rounded-lg text-sm text-gray-500 hover:text-gray-300 hover:bg-gray-800/40 transition-colors"
                      >
                        {cat.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </nav>
          </aside>

          {/* Mobile overlay */}
          {sidebarOpen && (
            <div
              className={`fixed inset-0 bg-black/60 z-10 ${isLabsHub ? 'top-14' : 'lg:hidden'}`}
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Main Content */}
          <main
            className={`flex-1 min-w-0 min-h-[calc(100vh-3.5rem)] flex flex-col ${
              isLabsHub ? 'overflow-hidden' : 'lg:ml-56 overflow-y-auto'
            }`}
          >
            <div
              className={
                isLabsHub
                  ? 'flex flex-1 flex-col min-h-0 min-w-0 w-full'
                  : 'max-w-5xl mx-auto px-6 py-8 w-full'
              }
            >
              {children}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
