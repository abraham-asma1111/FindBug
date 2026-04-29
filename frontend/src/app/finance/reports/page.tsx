'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';

export default function FinanceReportsPage() {
  const user = useAuthStore((state) => state.user);
  const [reportType, setReportType] = useState('payments');
  const [dateRange, setDateRange] = useState('30d');
  const [format, setFormat] = useState('json');
  const [generatedReport, setGeneratedReport] = useState<any>(null);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const generateMutation = useApiMutation({
    method: 'GET',
    onSuccess: (data) => {
      setGeneratedReport(data);
    },
  });

  const handleGenerateReport = async () => {
    const endpoints: Record<string, string> = {
      payments: `/finance/reports/payments?format=${format}`,
      payouts: `/finance/reports/payouts?format=${format}`,
      financial_summary: `/finance/reports/financial-summary`,
      tax: `/finance/reports/tax?year=2024&format=${format}`,
    };

    const endpoint = endpoints[reportType];
    if (endpoint) {
      if (format === 'csv') {
        window.open(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, '_blank');
      } else {
        await generateMutation.mutateAsync({ endpoint, data: {} });
      }
    }
  };

  return (
    <ProtectedRoute allowedRoles={['finance_officer', 'admin', 'super_admin']}>
      {user ? (
        <PortalShell
          user={user}
          title="Financial Reports"
          subtitle="Generate and export financial reports"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155] mb-6">
            <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Generate Report</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Report Type
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="payments">Payments Report</option>
                  <option value="payouts">Payouts Report</option>
                  <option value="financial_summary">Financial Summary</option>
                  <option value="tax">Tax Report</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Date Range
                </label>
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                  <option value="1y">Last Year</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
                  Format
                </label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                >
                  <option value="json">JSON (View Online)</option>
                  <option value="csv">CSV (Download)</option>
                </select>
              </div>

              <Button 
                onClick={handleGenerateReport} 
                className="w-full"
                disabled={generateMutation.isLoading}
              >
                {generateMutation.isLoading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
          </div>

          {generatedReport && (
            <div className="bg-[#1E293B] rounded-lg p-6 border border-[#334155]">
              <h2 className="text-lg font-semibold text-[#F8FAFC] mb-4">Report Results</h2>
              <div className="bg-[#0F172A] rounded p-4 overflow-auto max-h-96">
                <pre className="text-xs text-[#F8FAFC]">
                  {JSON.stringify(generatedReport, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}
