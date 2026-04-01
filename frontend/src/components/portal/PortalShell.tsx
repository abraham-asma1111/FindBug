'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import type { PortalNavItem, UserProfile } from '@/lib/portal';
import { getRoleLabel } from '@/lib/portal';

interface PortalShellProps {
  user: UserProfile;
  title: string;
  subtitle: string;
  navItems: PortalNavItem[];
  moduleTabs?: PortalNavItem[];
  children: ReactNode;
}

export default function PortalShell({
  user,
  title,
  subtitle,
  navItems,
  moduleTabs,
  children,
}: PortalShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  const isActiveRoute = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  const handleLogout = () => {
    logout();
    router.replace('/auth/login');
  };

  return (
    <div className="min-h-screen bg-[#f5f1ec] text-[#2d2a26]">
      <div className="grid min-h-screen lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="border-b border-[#ddd4cb] bg-[#faf6f1] px-6 py-8 text-[#2d2a26] lg:border-b-0 lg:border-r">
          <div className="space-y-8">
            <div>
              <Link
                href="/"
                className="inline-flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.25em] text-[#9d1f1f]"
              >
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-[#fde9e7] text-lg text-[#c3272f]">
                  F
                </span>
                FindBug
              </Link>
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.25em] text-[#8b8177]">
                Workspace
              </p>
              <nav className="space-y-2">
              {navItems.map((item) => {
                const isActive = isActiveRoute(item.href);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition ${
                      isActive
                        ? 'bg-[#fde9e7] text-[#9d1f1f]'
                        : 'text-[#4f4943] hover:bg-white hover:text-[#2d2a26]'
                    }`}
                  >
                    <span>{item.label}</span>
                    {item.badge !== undefined ? (
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          isActive ? 'bg-[#f9c6c2] text-[#8e1b22]' : 'bg-[#f3ede6] text-[#6d6760]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    ) : null}
                  </Link>
                );
              })}
              </nav>
            </div>
          </div>
        </aside>

        <main className="px-4 py-6 sm:px-6 lg:px-10 lg:py-8">
          <header className="mb-5 rounded-[2rem] border border-[#ddd4cb] bg-gradient-to-r from-white via-[#fcfaf7] to-[#f7efe8] px-6 py-6 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#8b8177]">
                  {getRoleLabel(user.role)} Portal
                </p>
                <h1 className="mt-2 text-3xl font-semibold text-[#2d2a26]">{title}</h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-[#6d6760]">{subtitle}</p>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard/mfa"
                  className="rounded-full border border-[#d5ccc3] bg-white px-4 py-2 text-sm font-medium text-[#4f4943] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
                >
                  Security
                </Link>
                <button
                  onClick={handleLogout}
                  className="rounded-full bg-[#ef2330] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#d81c29]"
                >
                  Log Out
                </button>
              </div>
            </div>
          </header>

          {moduleTabs?.length ? (
            <nav className="mb-8 flex flex-wrap gap-3 rounded-[1.75rem] border border-[#ddd4cb] bg-[#faf6f1] px-4 py-3 shadow-sm">
              {moduleTabs.map((item) => {
                const isActive = isActiveRoute(item.href);

                return (
                  <Link
                    key={`${item.href}-top`}
                    href={item.href}
                    className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                      isActive
                        ? 'bg-[#fde9e7] text-[#9d1f1f]'
                        : 'bg-white text-[#4f4943] hover:bg-[#f7efe8] hover:text-[#2d2a26]'
                    }`}
                  >
                    <span>{item.label}</span>
                    {item.badge !== undefined ? (
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          isActive ? 'bg-[#f9c6c2] text-[#8e1b22]' : 'bg-[#f3ede6] text-[#6d6760]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    ) : null}
                  </Link>
                );
              })}
            </nav>
          ) : null}

          {children}
        </main>
      </div>
    </div>
  );
}
