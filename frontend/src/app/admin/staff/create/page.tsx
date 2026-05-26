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
  const [createdCredentials, setCreatedCredentials] = useState<{ email: string; temporary_password: string } | null>(null);

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
      const response = await api.post(`/admin/staff/create?${params.toString()}`);
      setCreatedCredentials({
        email: response.data.email,
        temporary_password: response.data.temporary_password,
      });
      setSuccess(true);
      // Removed auto-redirect so the admin has time to copy the password
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
                Provision a new internal staff member. A temporary password will be generated for them.
              </p>
            </div>
          </section>

          <div className="mt-6 mx-auto max-w-lg">
            {success && createdCredentials ? (
              <div className="rounded-lg border border-[#10B981] bg-[#0F172A] p-6 text-center shadow-lg">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#10B981]/20 mb-4">
                  <svg className="h-6 w-6 text-[#10B981]" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-[#F8FAFC] mb-2">Staff Member Provisioned!</h3>
                <p className="text-[#94A3B8] text-sm mb-6">
                  Please securely share these credentials with the new staff member. They will be prompted to change their password upon their first login.
                </p>
                
                <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-4 text-left mb-6 space-y-4">
                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-[#64748B] block mb-1">Email</label>
                    <code className="text-sm text-[#F8FAFC] bg-[#0F172A] px-2 py-1 rounded block">{createdCredentials.email}</code>
                  </div>
                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-[#64748B] block mb-1">Temporary Password</label>
                    <div className="flex items-center justify-between bg-[#0F172A] px-3 py-2 rounded border border-[#334155]">
                      <code className="text-[#38BDF8] font-mono">{createdCredentials.temporary_password}</code>
                      <button 
                        onClick={() => navigator.clipboard.writeText(createdCredentials.temporary_password)}
                        className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] flex items-center gap-1"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        Copy
                      </button>
                    </div>
                  </div>
                </div>

                <Button 
                  onClick={() => router.push('/admin/staff')}
                  className="w-full bg-[#10B981] hover:bg-[#059669] text-white font-bold"
                >
                  Return to Staff List
                </Button>
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
