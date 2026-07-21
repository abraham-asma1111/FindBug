'use client';

import PieChart from '@/components/ui/PieChart';

interface SeverityChartProps {
  findings: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
}

export default function PTaaSSeverityChart({ findings }: SeverityChartProps) {
  const chartData = [
    { label: 'Critical', value: findings.critical, color: '#ef4444' },
    { label: 'High', value: findings.high, color: '#f97316' },
    { label: 'Medium', value: findings.medium, color: '#eab308' },
    { label: 'Low', value: findings.low, color: '#3b82f6' },
    { label: 'Info', value: findings.info, color: '#6b7280' },
  ];

  const total = findings.critical + findings.high + findings.medium + findings.low + findings.info;

  return (
    <div className="rounded-xl border border-[#e6ddd4] bg-white p-6">
      <h3 className="text-lg font-semibold text-[#2d2a26] mb-6">Findings by Severity</h3>
      
      {total === 0 ? (
        <div className="text-center py-12">
          <p className="text-sm text-[#6d6760]">No findings reported yet</p>
        </div>
      ) : (
        <PieChart 
          data={chartData} 
          size={280}
          showLegend={true}
          showLabels={true}
        />
      )}
    </div>
  );
}
