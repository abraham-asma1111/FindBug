'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import SectionCard from '@/components/dashboard/SectionCard';
import StatCard from '@/components/dashboard/StatCard';
import PortalShell from '@/components/portal/PortalShell';
import { api } from '@/lib/api';
import { formatCurrency, getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';

interface ProfileFormState {
  fullName: string;
  bio: string;
  website: string;
  github: string;
  twitter: string;
}

export default function ResearcherSettingsPage() {
  const user = useAuthStore((state) => state.user);
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const [form, setForm] = useState<ProfileFormState>({
    fullName: '',
    bio: '',
    website: '',
    github: '',
    twitter: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadProfile = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/users/me');
        if (!cancelled) {
          setForm({
            fullName: response.data?.full_name || '',
            bio: response.data?.researcher?.bio || '',
            website: response.data?.researcher?.website || '',
            github: response.data?.researcher?.github || '',
            twitter: response.data?.researcher?.twitter || '',
          });
          setError('');
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load settings.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadProfile();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      await api.put('/users/me', {
        full_name: form.fullName,
        profile: {
          bio: form.bio,
          website: form.website,
          github: form.github,
          twitter: form.twitter,
        },
      });

      await checkAuth();
      setSuccess('Settings updated successfully.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update settings.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Settings"
          subtitle="Maintain your researcher profile, public identity, and baseline account configuration."
          navItems={getPortalNavItems(user.role)}
        >
          <div className="grid gap-4 md:grid-cols-3">
            <StatCard label="Email" value={user.email} helper={user.emailVerified ? 'Verified account' : 'Email not verified'} />
            <StatCard
              label="Reputation"
              value={String(user.researcher?.reputation_score ?? 0)}
              helper={user.researcher?.rank ? `Current rank #${user.researcher.rank}` : 'Ranking pending'}
            />
            <StatCard
              label="Lifetime Earnings"
              value={formatCurrency(user.researcher?.total_earnings)}
              helper={user.mfaEnabled ? 'MFA enabled' : 'Enable MFA from Security'}
            />
          </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
          <SectionCard title="Profile Settings" description="This updates `/users/me` and refreshes local auth state.">
            <form onSubmit={handleSubmit} className="space-y-5">
              {error ? (
                <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
                  {error}
                </div>
              ) : null}

              {success ? (
                <div className="rounded-2xl border border-[#c9e6cf] bg-[#eef7ef] p-4 text-sm text-[#24613a]">
                  {success}
                </div>
              ) : null}

              <div className="space-y-2">
                <label htmlFor="fullName" className="block text-sm font-medium text-[#4f4943]">
                  Full Name
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={form.fullName}
                  onChange={handleChange}
                  className="w-full rounded-2xl border border-[#d5ccc3] bg-white dark:bg-[#111111] px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="bio" className="block text-sm font-medium text-[#4f4943]">
                  Bio
                </label>
                <textarea
                  id="bio"
                  name="bio"
                  rows={5}
                  value={form.bio}
                  onChange={handleChange}
                  className="w-full rounded-2xl border border-[#d5ccc3] bg-white dark:bg-[#111111] px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                  placeholder="Share the domains and testing areas you are strongest in."
                />
              </div>

              <div className="grid gap-5 md:grid-cols-2">
                <div className="space-y-2">
                  <label htmlFor="website" className="block text-sm font-medium text-[#4f4943]">
                    Website
                  </label>
                  <input
                    id="website"
                    name="website"
                    type="url"
                    value={form.website}
                    onChange={handleChange}
                    className="w-full rounded-2xl border border-[#d5ccc3] bg-white dark:bg-[#111111] px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="github" className="block text-sm font-medium text-[#4f4943]">
                    GitHub
                  </label>
                  <input
                    id="github"
                    name="github"
                    type="text"
                    value={form.github}
                    onChange={handleChange}
                    className="w-full rounded-2xl border border-[#d5ccc3] bg-white dark:bg-[#111111] px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="twitter" className="block text-sm font-medium text-[#4f4943]">
                  X / Twitter
                </label>
                <input
                  id="twitter"
                  name="twitter"
                  type="text"
                  value={form.twitter}
                  onChange={handleChange}
                  className="w-full rounded-2xl border border-[#d5ccc3] bg-white dark:bg-[#111111] px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
                />
              </div>

              <button
                type="submit"
                disabled={isSaving || isLoading}
                className="rounded-full bg-[#ef2330] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Settings'}
              </button>
            </form>
          </SectionCard>

          <SectionCard
            title="Account Signals"
            description="Quick status checks for visibility and security posture."
          >
            <div className="space-y-4 text-sm text-[#6d6760]">
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Verification</p>
                <p className="mt-2 font-semibold text-[#2d2a26]">
                  {user.emailVerified ? 'Verified and active' : 'Verification pending'}
                </p>
              </div>
              <div className="rounded-2xl bg-[#faf6f1] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8b8177]">Security</p>
                <p className="mt-2 font-semibold text-[#2d2a26]">
                  {user.mfaEnabled ? 'MFA enabled' : 'MFA not enabled yet'}
                </p>
              </div>
            </div>
          </SectionCard>
        </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
