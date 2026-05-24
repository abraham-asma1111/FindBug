'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

interface FormState {
  email: string;
  full_name: string;
  department: string;
  role: string;
}

export default function StaffCreatePage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  const [form, setForm] = useState<FormState>({
    email: '',
    full_name: '',
    department: '',
    role: 'triage_specialist',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email || !form.full_name || !form.department) {
      setError('Please fill in all required fields.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        email: form.email,
        full_name: form.full_name,
        department: form.department,
        role: form.role,
      });
      await api.post(`/admin/staff/create?${params.toString()}`);
      setSuccess(true);
      setTimeout(() => router.push('/admin/staff'), 1500);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to provision staff member. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const ROLES = [
    { value: 'triage_specialist', label: 'Triage Specialist' },
    { value: 'finance_officer',   label: 'Finance Officer' },
    { value: 'staff',             label: 'Platform Staff' },
    { value: 'admin',             label: 'Administrator' },
  ];

  const DEPARTMENTS = ['Triage', 'Finance', 'Engineering', 'Operations', 'Admin'];

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Provision Staff"
          subtitle="Create a new staff account"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Admin Console"
          eyebrowClassName="text-xl tracking-[0.18em]"
          hideTitle
          hideSubtitle
          hideThemeToggle={true}
        >
          <section className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 shadow-sm sm:p-8">
            <div className="text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#94A3B8]">
                Staff Provisioning
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F8FAFC] sm:text-5xl">
                Create Staff Account
              </h1>
              <p className="mt-4 text-sm leading-7 text-[#94A3B8] sm:text-base">
                Provision a new internal staff member. A temporary password will be generated and a welcome email sent.
              </p>
            </div>
          </section>

          <div className="mt-6 mx-auto max-w-lg">
            {success ? (
              <div className="rounded-lg border border-[#10B981] bg-[#10B981]/10 p-6 text-center">
                <p className="text-[#10B981] font-semibold text-lg">Staff member provisioned!</p>
                <p className="text-[#94A3B8] text-sm mt-2">Redirecting to staff list…</p>
              </div>
            ) : (
              <form
                onSubmit={handleSubmit}
                className="rounded-lg border border-[#334155] bg-[#1E293B] p-6 space-y-5"
              >
                <div>
                  <label className="block text-sm font-medium text-[#F8FAFC] mb-1">
                    Full Name <span className="text-[#EF2330]">*</span>
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Jane Doe"
                    className="w-full rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#EF2330] focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#F8FAFC] mb-1">
                    Email Address <span className="text-[#EF2330]">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="jane@findbug.io"
                    className="w-full rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#EF2330] focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#F8FAFC] mb-1">
                    Role <span className="text-[#EF2330]">*</span>
                  </label>
                  <select
                    name="role"
                    value={form.role}
                    onChange={handleChange}
                    className="w-full rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] focus:border-[#EF2330] focus:outline-none"
                  >
                    {ROLES.map((r) => (
                      <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#F8FAFC] mb-1">
                    Department <span className="text-[#EF2330]">*</span>
                  </label>
                  <select
                    name="department"
                    value={form.department}
                    onChange={handleChange}
                    className="w-full rounded-md border border-[#334155] bg-[#0F172A] px-3 py-2 text-sm text-[#F8FAFC] focus:border-[#EF2330] focus:outline-none"
                    required
                  >
                    <option value="">Select department…</option>
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>

                {error && (
                  <div className="rounded-md bg-[#EF4444]/10 border border-[#EF4444]/30 px-4 py-3 text-sm text-[#EF4444]">
                    {error}
                  </div>
                )}

                <div className="flex gap-3 justify-end pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.push('/admin/staff')}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="bg-[#EF2330] hover:bg-[#DC2026] text-white"
                    disabled={loading}
                  >
                    {loading ? 'Creating…' : 'Provision Staff Member'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
