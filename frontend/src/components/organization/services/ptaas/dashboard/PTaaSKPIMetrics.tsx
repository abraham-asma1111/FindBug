'use client';

import { Users, AlertCircle, Target, TrendingUp } from 'lucide-react';

interface KPIMetricsProps {
  metrics: {
    active_researchers: number;
    total_findings: number;
    findings_by_severity: {
      critical: number;
      high: number;
      medium: number;
      low: number;
      info: number;
    };
    asset_coverage: {
      tested: number;
      total: number;
      percentage: number;
    };
    overall_progress: number;
  };
}

export default function PTaaSKPIMetrics({ metrics }: KPIMetricsProps) {
  const kpiCards = [
    {
      title: 'Active Researchers',
      value: metrics.active_researchers,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
    },
    {
      title: 'Total Findings',
      value: metrics.total_findings,
      subtitle: `${metrics.findings_by_severity.critical} Critical, ${metrics.findings_by_severity.high} High`,
      icon: AlertCircle,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600',
    },
    {
      title: 'Asset Coverage',
      value: `${metrics.asset_coverage.percentage.toFixed(0)}%`,
      subtitle: `${metrics.asset_coverage.tested} of ${metrics.asset_coverage.total} assets tested`,
      icon: Target,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
    },
    {
      title: 'Overall Progress',
      value: `${metrics.overall_progress.toFixed(0)}%`,
      icon: TrendingUp,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiCards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            className="rounded-xl border border-[#e6ddd4] bg-white p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-[#8b8177] mb-2">{card.title}</p>
                <p className="text-3xl font-bold text-[#2d2a26] mb-1">{card.value}</p>
                {card.subtitle && (
                  <p className="text-xs text-[#6d6760]">{card.subtitle}</p>
                )}
              </div>
              <div className={`rounded-lg ${card.bgColor} p-3`}>
                <Icon className={`h-6 w-6 ${card.textColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
