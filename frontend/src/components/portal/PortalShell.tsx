'use client';

import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import type { PortalNavItem, UserProfile } from '@/lib/portal';
import { getPortalName } from '@/lib/portal';

interface PortalShellProps {
  user: UserProfile;
  title: string;
  subtitle: string;
  navItems: PortalNavItem[];
  moduleTabs?: PortalNavItem[];
  headerAlign?: 'left' | 'center';
  eyebrowText?: string;
  eyebrowClassName?: string;
  hideTitle?: boolean;
  hideSubtitle?: boolean;
  hideThemeToggle?: boolean;
  children: ReactNode;
}

export default function PortalShell({
  user,
  title,
  subtitle,
  navItems,
  moduleTabs,
  headerAlign = 'left',
  eyebrowText,
  eyebrowClassName = '',
  hideTitle = false,
  hideSubtitle = false,
  hideThemeToggle = false,
  children,
}: PortalShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);
  const { isDarkMode, toggleDarkMode } = useThemeStore();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const newExpanded = new Set<string>();
    navItems.forEach((item) => {
      if (item.children) {
        const hasActiveChild = item.children.some(
          (child) => pathname === child.href || pathname.startsWith(`${child.href}/`)
        );
        if (hasActiveChild) {
          newExpanded.add(item.href);
        }
      }
    });
    setExpandedItems(newExpanded);
  }, [pathname, navItems]);

  const isActiveRoute = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  const toggleExpanded = (href: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(href)) {
        next.delete(href);
      } else {
        next.add(href);
      }
      return next;
    });
  };

  const handleLogout = () => {
    logout();
    router.replace('/auth/login');
  };

  // Group items by category
  const groupedItems = (() => {
    const categories = new Map<string, PortalNavItem[]>();
    navItems.forEach((item) => {
      const cat = item.category || 'MAIN';
      if (!categories.has(cat)) {
        categories.set(cat, []);
      }
      categories.get(cat)!.push(item);
    });
    return Array.from(categories.entries());
  })();

  return (
    <div className="min-h-screen bg-[#f5f1ec] dark:bg-[#0a0e1a] text-[#2d2a26] dark:text-white">
      <div className="grid min-h-screen lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="border-b border-[#ddd4cb] dark:border-[#1e293b] bg-[#faf6f1] dark:bg-[#020617] px-6 py-8 text-[#2d2a26] dark:text-[#F8FAFC] lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto lg:border-b-0 lg:border-r">
          <div className="space-y-8">
            <div>
              <Link
                href="/"
                className="inline-flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.25em] text-[#9d1f1f] dark:text-red-400"
              >
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-[#fde9e7] dark:bg-red-900/30 text-lg text-[#c3272f] dark:text-red-400">
                  F
                </span>
                FindBug
              </Link>
            </div>

            <div>
              <p className="mb-4 text-xs font-bold uppercase tracking-[0.25em] text-[#8b8177] dark:text-[#94A3B8]">
                {getPortalName(user.role)}
              </p>
              <nav className="space-y-2">
                {groupedItems.map(([category, items]) => (
                  <div key={category}>
                    {category !== 'MAIN' && (
                      <p className="mt-6 mb-3 text-xs font-bold uppercase tracking-[0.18em] text-[#8b8177] dark:text-[#64748B]">
                        {category}
                      </p>
                    )}
                    <div className="space-y-2">
                      {items.map((item) => {
                        const isActive = isActiveRoute(item.href);
                        const isExpanded = expandedItems.has(item.href);
                        const hasChildren = item.children && item.children.length > 0;

                        return (
                          <div key={item.href}>
                            {hasChildren ? (
                              <>
                                <div className={`flex items-center rounded-lg transition ${
                                  isActive
                                    ? 'bg-[#fde9e7] dark:bg-[#2563EB] text-[#9d1f1f] dark:text-[#F8FAFC]'
                                    : 'text-[#4f4943] dark:text-[#94A3B8] hover:bg-white dark:hover:bg-[#334155] hover:text-[#2d2a26] dark:hover:text-[#F8FAFC]'
                                }`}>
                                  <Link
                                    href={item.href}
                                    className="flex-1 px-5 py-3.5 text-base font-bold"
                                  >
                                    {item.label}
                                  </Link>
                                  <button
                                    onClick={() => toggleExpanded(item.href)}
                                    className="px-4 py-3.5"
                                  >
                                    <svg
                                      className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                  </button>
                                </div>
                                {isExpanded && item.children && (
                                  <div className="mt-1 ml-4 space-y-1">
                                    {item.children.map((child) => {
                                      const isChildActive = isActiveRoute(child.href);
                                      return (
                                        <Link
                                          key={child.href}
                                          href={child.href}
                                          className={`block px-4 py-2.5 rounded-lg text-sm font-medium transition ${
                                            isChildActive
                                              ? 'bg-[#fde9e7] dark:bg-[#1e40af] text-[#9d1f1f] dark:text-[#F8FAFC]'
                                              : 'text-[#4f4943] dark:text-[#94A3B8] hover:bg-white dark:hover:bg-[#334155] hover:text-[#2d2a26] dark:hover:text-[#F8FAFC]'
                                          }`}
                                        >
                                          {child.label}
                                        </Link>
                                      );
                                    })}
                                  </div>
                                )}
                              </>
                            ) : (
                              <Link
                                href={item.href}
                                className={`block px-5 py-3.5 rounded-lg text-base font-bold transition ${
                                  isActive
                                    ? 'bg-[#fde9e7] dark:bg-[#2563EB] text-[#9d1f1f] dark:text-[#F8FAFC]'
                                    : 'text-[#4f4943] dark:text-[#94A3B8] hover:bg-white dark:hover:bg-[#334155] hover:text-[#2d2a26] dark:hover:text-[#F8FAFC]'
                                }`}
                              >
                                {item.label}
                              </Link>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </nav>
            </div>
          </div>
        </aside>

        <div className="flex min-h-screen min-w-0 flex-col">
          <header className="sticky top-0 z-20 border-b border-[#ddd4cb] dark:border-[#1e293b] bg-[#fcfaf7]/95 dark:bg-[#020617]/95 backdrop-blur">
            <div className="px-4 py-5 sm:px-6 lg:px-6">
              {headerAlign === 'center' ? (
                <div className="grid gap-4 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
                  <div className="hidden lg:block" />
                  <div className="max-w-3xl text-center">
                    <p className={`font-bold uppercase text-[#8b8177] dark:text-[#94A3B8] ${eyebrowClassName || 'text-xs tracking-[0.25em]'}`}>
                      {eyebrowText || getPortalName(user.role)}
                    </p>
                    {!hideTitle ? <h1 className="mt-2 text-3xl font-bold text-[#2d2a26] dark:text-[#F8FAFC]">{title}</h1> : null}
                    {!hideSubtitle ? <p className="mt-2 max-w-3xl text-sm leading-6 text-[#6d6760] dark:text-[#94A3B8]">{subtitle}</p> : null}
                  </div>

                  <div className="flex items-center justify-center gap-3 lg:justify-end">
                    {!hideThemeToggle && (
                      <button
                        onClick={toggleDarkMode}
                        className="rounded-full border border-[#d5ccc3] dark:border-[#2a2a2a] bg-white dark:bg-[#1a1a1a] p-2 text-[#4f4943] dark:text-gray-300 transition hover:border-[#c8bfb6] dark:hover:border-[#3a3a3a] hover:bg-[#fcfaf7] dark:hover:bg-[#2a2a2a]"
                        title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                      >
                        {isDarkMode ? (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                          </svg>
                        ) : (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                          </svg>
                        )}
                      </button>
                    )}
                    <Link
                      href="/dashboard/mfa"
                      className="rounded-full border border-[#d5ccc3] dark:border-[#2a2a2a] bg-white dark:bg-[#1a1a1a] px-4 py-2 text-sm font-medium text-[#4f4943] dark:text-gray-300 transition hover:border-[#c8bfb6] dark:hover:border-[#3a3a3a] hover:bg-[#fcfaf7] dark:hover:bg-[#2a2a2a]"
                    >
                      Security
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="rounded-full bg-[#ef2330] dark:bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-[#d81c29] dark:hover:bg-red-700"
                    >
                      Log Out
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <p className={`font-bold uppercase text-[#8b8177] dark:text-[#94A3B8] ${eyebrowClassName || 'text-xs tracking-[0.25em]'}`}>
                      {eyebrowText || getPortalName(user.role)}
                    </p>
                    {!hideTitle ? <h1 className="mt-2 text-3xl font-bold text-[#2d2a26] dark:text-[#F8FAFC]">{title}</h1> : null}
                    {!hideSubtitle ? <p className="mt-2 max-w-3xl text-sm leading-6 text-[#6d6760] dark:text-[#94A3B8]">{subtitle}</p> : null}
                  </div>

                  <div className="flex items-center gap-3">
                    {!hideThemeToggle && (
                      <button
                        onClick={toggleDarkMode}
                        className="rounded-full border border-[#d5ccc3] dark:border-[#2a2a2a] bg-white dark:bg-[#1a1a1a] p-2 text-[#4f4943] dark:text-gray-300 transition hover:border-[#c8bfb6] dark:hover:border-[#3a3a3a] hover:bg-[#fcfaf7] dark:hover:bg-[#2a2a2a]"
                        title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                      >
                        {isDarkMode ? (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                          </svg>
                        ) : (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                          </svg>
                        )}
                      </button>
                    )}
                    <Link
                      href="/dashboard/mfa"
                      className="rounded-full border border-[#d5ccc3] dark:border-[#2a2a2a] bg-white dark:bg-[#1a1a1a] px-4 py-2 text-sm font-medium text-[#4f4943] dark:text-gray-300 transition hover:border-[#c8bfb6] dark:hover:border-[#3a3a3a] hover:bg-[#fcfaf7] dark:hover:bg-[#2a2a2a]"
                    >
                      Security
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="rounded-full bg-[#ef2330] dark:bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-[#d81c29] dark:hover:bg-red-700"
                    >
                      Log Out
                    </button>
                  </div>
                </div>
              )}
            </div>

            {moduleTabs?.length ? (
              <nav className="border-t border-[#ddd4cb] dark:border-[#1e293b] bg-[#faf6f1] dark:bg-[#020617] px-4 py-3 sm:px-6 lg:px-6">
                <div className="flex flex-wrap gap-3">
                  {moduleTabs.map((item) => {
                    const isActive = isActiveRoute(item.href);

                    return (
                      <Link
                        key={`${item.href}-top`}
                        href={item.href}
                        className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-bold transition ${
                          isActive
                            ? 'bg-[#fde9e7] dark:bg-[#2563EB] text-[#9d1f1f] dark:text-[#F8FAFC]'
                            : 'bg-white dark:bg-[#1E293B] text-[#4f4943] dark:text-[#94A3B8] hover:bg-[#f7efe8] dark:hover:bg-[#334155] hover:text-[#2d2a26] dark:hover:text-[#F8FAFC]'
                        }`}
                      >
                        <span>{item.label}</span>
                        {item.badge !== undefined ? (
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                              isActive ? 'bg-[#f9c6c2] dark:bg-[#1E293B] text-[#8e1b22] dark:text-[#94A3B8]' : 'bg-[#f3ede6] dark:bg-[#020617] text-[#6d6760] dark:text-[#94A3B8]'
                            }`}
                          >
                            {item.badge}
                          </span>
                        ) : null}
                      </Link>
                    );
                  })}
                </div>
              </nav>
            ) : null}
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-6 lg:py-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
