'use client';

import { useState } from 'react';
import api from '@/lib/api';

const roleOptions = [
  { value: 'triage_specialist', label: 'Triage Specialist' },
  { value: 'finance_officer', label: 'Finance Officer' },
  { value: 'admin', label: 'Administrator' },
];

export default function StaffProvisionForm() {
  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    department: '',
    role: 'triage_specialist',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/admin/staff/create', null, {
        params: {
          email: formData.email,
          full_name: formData.fullName,
          department: formData.department,
          role: formData.role,
        },
      });

      setSuccess(response.data?.message || `Staff account created for ${formData.email}.`);
      setFormData({
        email: '',
        fullName: '',
        department: '',
        role: 'triage_specialist',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create staff account.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
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

      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="fullName" className="block text-sm font-medium text-[#4f4943]">
            Full Name
          </label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            required
            value={formData.fullName}
            onChange={handleChange}
            className="w-full rounded-2xl border border-[#d5ccc3] bg-white px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
            placeholder="Security Operations Lead"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-[#4f4943]">
            Work Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={formData.email}
            onChange={handleChange}
            className="w-full rounded-2xl border border-[#d5ccc3] bg-white px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
            placeholder="person@company.com"
          />
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="department" className="block text-sm font-medium text-[#4f4943]">
            Department
          </label>
          <input
            id="department"
            name="department"
            type="text"
            required
            value={formData.department}
            onChange={handleChange}
            className="w-full rounded-2xl border border-[#d5ccc3] bg-white px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
            placeholder="Security Operations"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="role" className="block text-sm font-medium text-[#4f4943]">
            Platform Role
          </label>
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="w-full rounded-2xl border border-[#d5ccc3] bg-white px-4 py-3 text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-[#f9c6c2]"
          >
            {roleOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-3xl bg-[#faf6f1] p-5">
        <p className="text-sm leading-6 text-[#6d6760]">
          The backend provisions a temporary password automatically and marks the account verified. This form is aligned to the current
          `/admin/staff/create` contract rather than the older JSON-based prototype route.
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="rounded-full bg-[#ef2330] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#d81c29] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading ? 'Provisioning account...' : 'Create staff account'}
      </button>
    </form>
  );
}
