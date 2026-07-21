'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

export default function OrganizationSettingsPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const settingsOptions = [
    {
      id: 'branding',
      title: 'Branding',
      description: 'Customize your organization\'s appearance with logos, colors, and cover images',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
      ),
      color: 'from-[#3B82F6] to-[#1D4ED8]',
      path: '/organization/settings/branding',
    },
    {
      id: 'profile',
      title: 'Organization Profile',
      description: 'Update company information, contact details, and verification status',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      color: 'from-[#8B5CF6] to-[#7C3AED]',
      path: '/organization/profile',
      comingSoon: true,
    },
    {
      id: 'team',
      title: 'Team Management',
      description: 'Manage team members, roles, and permissions',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      color: 'from-[#10B981] to-[#059669]',
      path: '/organization/team',
      comingSoon: true,
    },
    {
      id: 'security',
      title: 'Security Settings',
      description: 'Configure SSO, two-factor authentication, and security policies',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      color: 'from-[#EF4444] to-[#DC2626]',
      path: '/organization/security',
      comingSoon: true,
    },
    {
      id: 'domain-verification',
      title: 'Domain Verification',
      description: 'Verify ownership of organization domains before publishing high-trust scopes',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.866-3.134 7-7 7m7-7c0-3.866 3.134-7 7-7m-7 7v10m0-10V3m-7 15h14" />
        </svg>
      ),
      color: 'from-[#7C3AED] to-[#5B21B6]',
      path: '/organization/settings/domain-verification',
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Manage email notifications and alert preferences',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      ),
      color: 'from-[#F59E0B] to-[#D97706]',
      path: '/organization/notifications',
      comingSoon: true,
    },
    {
      id: 'integrations',
      title: 'Integrations',
      description: 'Connect with third-party tools and services',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
        </svg>
      ),
      color: 'from-[#06B6D4] to-[#0891B2]',
      path: '/organization/integrations',
      comingSoon: true,
    },
  ];

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {!user ? (
        <div className="min-h-[50vh] rounded-xl border border-[#334155] bg-[#1E293B] p-6 text-[#F8FAFC]">
          <h2 className="text-lg font-semibold">
            {isLoading ? 'Loading settings...' : 'Preparing your organization settings...'}
          </h2>
          <p className="mt-2 text-sm text-[#94A3B8]">
            If this takes too long, refresh once or sign in again.
          </p>
        </div>
      ) : (
      <PortalShell
        user={user}
        title="Settings"
        subtitle="Manage your organization settings and preferences"
        navItems={getPortalNavItems(user.role)}
        hideThemeToggle={true}
      >
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/organization/dashboard')}
            className="flex items-center gap-2 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {settingsOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => !option.comingSoon && router.push(option.path)}
              disabled={option.comingSoon}
              className={`
                relative bg-[#1E293B] rounded-xl border border-[#334155] p-6 text-left
                transition-all duration-200
                ${option.comingSoon 
                  ? 'opacity-60 cursor-not-allowed' 
                  : 'hover:border-[#3B82F6] hover:shadow-xl hover:shadow-[#3B82F6]/10 cursor-pointer'
                }
              `}
            >
              {/* Coming Soon Badge */}
              {option.comingSoon && (
                <div className="absolute top-4 right-4">
                  <span className="px-3 py-1 bg-[#F59E0B]/20 text-[#F59E0B] text-xs font-bold uppercase rounded-full border border-[#F59E0B]/30">
                    Coming Soon
                  </span>
                </div>
              )}

              {/* Icon */}
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${option.color} flex items-center justify-center mb-4 text-white`}>
                {option.icon}
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-[#F8FAFC] mb-2">
                {option.title}
              </h3>

              {/* Description */}
              <p className="text-[#94A3B8] text-sm leading-relaxed">
                {option.description}
              </p>

              {/* Arrow Icon (only for available options) */}
              {!option.comingSoon && (
                <div className="mt-4 flex items-center gap-2 text-[#3B82F6] font-medium text-sm">
                  <span>Configure</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-[#1E293B] rounded-xl border border-[#334155] p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Need Help?</h3>
              <p className="text-[#94A3B8] text-sm mb-4">
                If you need assistance with any settings, please contact our support team or check the documentation.
              </p>
              <div className="flex gap-3">
                <button className="px-4 py-2 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-medium text-sm">
                  Contact Support
                </button>
                <button className="px-4 py-2 bg-[#334155] text-[#F8FAFC] rounded-lg hover:bg-[#475569] transition-colors font-medium text-sm">
                  View Documentation
                </button>
              </div>
            </div>
          </div>
        </div>
      </PortalShell>
      )}
    </ProtectedRoute>
  );
}
