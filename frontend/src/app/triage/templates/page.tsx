'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import Button from '@/components/ui/Button';
import { FileText, Plus, Edit, Trash2, AlertCircle } from 'lucide-react';

interface Template {
  id: string;
  name: string;
  title: string;
  content: string;
  category: string;
  is_active: boolean;
  created_at: string;
}

interface TemplatesResponse {
  templates: Template[];
  total: number;
  limit: number;
  offset: number;
}

const categoryColors: Record<string, string> = {
  validation: 'bg-[#3B82F6] text-white',
  rejection: 'bg-[#EF4444] text-white',
  duplicate: 'bg-[#F59E0B] text-white',
  need_info: 'bg-[#3B82F6] text-white',
  resolved: 'bg-[#3B82F6] text-white',
};

export default function TriageTemplatesPage() {
  const user = useAuthStore((state) => state.user);
  const [page, setPage] = useState(0);
  const limit = 20;

  // Force dark mode for triage portal
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const queryParams = new URLSearchParams();
  queryParams.append('limit', limit.toString());
  queryParams.append('offset', (page * limit).toString());

  const { data, isLoading, error } = useApiQuery<TemplatesResponse>({
    endpoint: `/triage/templates?${queryParams.toString()}`,
  });

  const templates = data?.templates || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Response Templates"
          subtitle="Manage triage response templates"
          navItems={getPortalNavItems(user.role)}
          headerAlign="left"
          hideThemeToggle={true}
        >
          {/* Header Actions */}
          <div className="mb-6 flex justify-between items-center">
            <div className="flex gap-4">
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Total Templates
                </p>
                <p className="mt-2 text-2xl font-bold text-[#F8FAFC]">
                  {total}
                </p>
              </div>
              <div className="bg-[#1E293B] rounded-lg p-4 border border-[#334155]">
                <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide">
                  Active
                </p>
                <p className="mt-2 text-2xl font-bold text-[#3B82F6]">
                  {templates.filter((t) => t.is_active).length}
                </p>
              </div>
            </div>
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              New Template
            </Button>
          </div>

          {/* Templates Grid */}
          {isLoading ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-600 border-t-slate-100"></div>
              <p className="mt-4 text-[#94A3B8]">Loading templates...</p>
            </div>
          ) : error ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <AlertCircle className="mx-auto h-8 w-8 text-[#EF4444]" />
              <p className="mt-4 text-[#EF4444]">Failed to load templates</p>
            </div>
          ) : templates.length === 0 ? (
            <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-8 text-center">
              <FileText className="mx-auto h-12 w-12 text-[#94A3B8]" />
              <p className="mt-4 text-[#94A3B8]">No templates found</p>
              <Button className="mt-4 gap-2">
                <Plus className="w-4 h-4" />
                Create First Template
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="bg-[#1E293B] rounded-lg border border-[#334155] p-6 hover:bg-[#334155] transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-[#0F172A]">
                        <FileText className="w-5 h-5 text-[#94A3B8]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#F8FAFC]">
                          {template.title}
                        </h3>
                        <p className="text-xs text-[#94A3B8] mt-1">
                          {template.name}
                        </p>
                      </div>
                    </div>
                    {template.is_active && (
                      <span className="px-2 py-1 rounded-full text-xs font-semibold bg-[#3B82F6] text-white">
                        Active
                      </span>
                    )}
                  </div>

                  <div className="mb-4">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        categoryColors[template.category] || 'bg-[#94A3B8] text-white'
                      }`}
                    >
                      {template.category.replace('_', ' ')}
                    </span>
                  </div>

                  <p className="text-sm text-[#94A3B8] line-clamp-3 mb-4">
                    {template.content}
                  </p>

                  <div className="flex gap-2 pt-4 border-t border-[#334155]">
                    <Button variant="outline" size="sm" className="flex-1 gap-2">
                      <Edit className="w-4 h-4" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2 text-[#EF4444]">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-[#94A3B8]">
                Page {page + 1} of {totalPages} ({total} total templates)
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  variant="outline"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page === totalPages - 1}
                  variant="outline"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
