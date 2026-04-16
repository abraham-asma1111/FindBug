'use client';

import React from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { TrendingUp, Clock, Shield, BarChart3 } from 'lucide-react';
import Card from '@/components/ui/Card';

interface AnalyticsData {
  vulnerability_trends: Array<{
    date: string;
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  }>;
  time_to_fix: {
    critical_avg_days: number;
    high_avg_days: number;
    medium_avg_days: number;
    low_avg_days: number;
  };
  risk_score: number;
  compliance_status: {
    pci_dss: string;
    owasp_top_10: string;
    iso_27001: string;
    critical_findings: number;
    high_findings: number;
  };
}

interface PTaaSAnalyticsDashboardProps {
  engagementId: string;
}

export default function PTaaSAnalyticsDashboard({ engagementId }: PTaaSAnalyticsDashboardProps) {
  const { data: analytics, isLoading } = useApiQuery<AnalyticsData>(
    `/ptaas/engagements/${engagementId}/analytics`
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3b82f6]" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12 text-[#6b6662] dark:text-[#a39e9a]">
        No analytics data available
      </div>
    );
  }

  const getRiskColor = (score: number) => {
    if (score >= 7) return 'text-red-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getComplianceColor = (status: string) => {
    if (status === 'compliant') return 'text-green-600 bg-green-50 dark:bg-green-900/20';
    if (status === 'partial') return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
    return 'text-red-600 bg-red-50 dark:bg-red-900/20';
  };

  return (
    <div className="space-y-6">
      {/* Risk Score */}
      <Card>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-5 w-5 text-[#3b82f6]" />
              <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
                Overall Risk Score
              </h3>
            </div>
            <p className="text-sm text-[#6b6662] dark:text-[#a39e9a]">
              Based on open findings and severity
            </p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${getRiskColor(analytics.risk_score)}`}>
              {analytics.risk_score}
            </div>
            <div className="text-sm text-[#6b6662] dark:text-[#a39e9a]">out of 10</div>
          </div>
        </div>
      </Card>

      {/* Time to Fix Metrics */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Clock className="h-5 w-5 text-[#3b82f6]" />
          <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
            Average Time to Fix
          </h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
            <div className="text-2xl font-bold text-red-600">
              {analytics.time_to_fix.critical_avg_days}
            </div>
            <div className="text-sm text-[#6b6662] dark:text-[#a39e9a]">Critical (days)</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20">
            <div className="text-2xl font-bold text-orange-600">
              {analytics.time_to_fix.high_avg_days}
            </div>
            <div className="text-sm text-[#6b6662] dark:text-[#a39e9a]">High (days)</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
            <div className="text-2xl font-bold text-yellow-600">
              {analytics.time_to_fix.medium_avg_days}
            </div>
            <div className="text-sm text-[#6b6662] dark:text-[#a39e9a]">Medium (days)</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
            <div className="text-2xl font-bold text-blue-600">
              {analytics.time_to_fix.low_avg_days}
            </div>
            <div className="text-sm text-[#6b6662] dark:text-[#a39e9a]">Low (days)</div>
          </div>
        </div>
      </Card>

      {/* Compliance Status */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-5 w-5 text-[#3b82f6]" />
          <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
            Compliance Status
          </h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-[#faf6f1] dark:bg-[#3d3a36]">
            <span className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">PCI DSS</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getComplianceColor(analytics.compliance_status.pci_dss)}`}>
              {analytics.compliance_status.pci_dss.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-[#faf6f1] dark:bg-[#3d3a36]">
            <span className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">OWASP Top 10</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getComplianceColor(analytics.compliance_status.owasp_top_10)}`}>
              {analytics.compliance_status.owasp_top_10.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-[#faf6f1] dark:bg-[#3d3a36]">
            <span className="font-medium text-[#2d2a26] dark:text-[#faf6f1]">ISO 27001</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getComplianceColor(analytics.compliance_status.iso_27001)}`}>
              {analytics.compliance_status.iso_27001.replace('_', ' ').toUpperCase()}
            </span>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-[#e6ddd4] dark:border-[#3d3a36]">
          <div className="flex justify-between text-sm">
            <span className="text-[#6b6662] dark:text-[#a39e9a]">Open Critical Findings:</span>
            <span className="font-medium text-red-600">{analytics.compliance_status.critical_findings}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-[#6b6662] dark:text-[#a39e9a]">Open High Findings:</span>
            <span className="font-medium text-orange-600">{analytics.compliance_status.high_findings}</span>
          </div>
        </div>
      </Card>

      {/* Vulnerability Trends */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-[#3b82f6]" />
          <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1]">
            Vulnerability Discovery Trends
          </h3>
        </div>
        {analytics.vulnerability_trends.length > 0 ? (
          <div className="space-y-2">
            {analytics.vulnerability_trends.slice(-7).map((trend) => (
              <div key={trend.date} className="flex items-center gap-3">
                <div className="text-sm text-[#6b6662] dark:text-[#a39e9a] w-24">
                  {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="flex-1 flex gap-1">
                  {trend.critical > 0 && (
                    <div className="bg-red-500 h-6 rounded" style={{ width: `${trend.critical * 20}px` }} title={`${trend.critical} Critical`} />
                  )}
                  {trend.high > 0 && (
                    <div className="bg-orange-500 h-6 rounded" style={{ width: `${trend.high * 20}px` }} title={`${trend.high} High`} />
                  )}
                  {trend.medium > 0 && (
                    <div className="bg-yellow-500 h-6 rounded" style={{ width: `${trend.medium * 20}px` }} title={`${trend.medium} Medium`} />
                  )}
                  {trend.low > 0 && (
                    <div className="bg-blue-500 h-6 rounded" style={{ width: `${trend.low * 20}px` }} title={`${trend.low} Low`} />
                  )}
                </div>
                <div className="text-sm font-medium text-[#2d2a26] dark:text-[#faf6f1] w-8 text-right">
                  {trend.critical + trend.high + trend.medium + trend.low + trend.info}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-[#6b6662] dark:text-[#a39e9a]">
            No trend data available yet
          </div>
        )}
      </Card>
    </div>
  );
}
