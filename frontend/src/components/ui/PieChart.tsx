'use client';

import { Pie, PieChart as RechartsPieChart, ResponsiveContainer, Cell, Legend } from 'recharts';

interface PieChartData {
  label: string;
  value: number;
  color: string;
}

interface PieChartProps {
  data: PieChartData[];
  size?: number;
  strokeWidth?: number;
  showLabels?: boolean;
  showLegend?: boolean;
  className?: string;
}

export default function PieChart({ 
  data, 
  size = 220, 
  showLegend = true,
  className = '' 
}: PieChartProps) {
  // Calculate total
  const total = data.reduce((sum, item) => sum + item.value, 0);

  // Transform data for Recharts
  const chartData = data.map(item => ({
    name: item.label,
    value: item.value,
    color: item.color,
  }));

  // Custom legend renderer matching the reference screenshot
  const renderLegend = (props: any) => {
    const { payload } = props;
    
    return (
      <div className="flex flex-col gap-3 ml-6">
        {payload.map((entry: any, index: number) => {
          const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(1) : '0.0';
          return (
            <div key={`legend-${index}`} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-sm font-medium text-white capitalize">
                  {entry.value}
                </span>
              </div>
              <span className="text-sm font-semibold text-white whitespace-nowrap">
                {entry.value.toLocaleString()} ({percentage}%)
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  if (data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div 
          className="rounded-full bg-slate-700 flex items-center justify-center"
          style={{ width: size, height: size }}
        >
          <span className="text-sm text-slate-400">No data</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center ${className}`}>
      <div className="relative" style={{ width: size, height: size }}>
        <ResponsiveContainer width={size} height={size} minWidth={0}>
          <RechartsPieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={size * 0.35}
              outerRadius={size * 0.45}
              paddingAngle={2}
              dataKey="value"
              startAngle={90}
              endAngle={450}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
              ))}
            </Pie>
          </RechartsPieChart>
        </ResponsiveContainer>
        
        {/* Center text showing total */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center flex flex-col items-center justify-center mt-1">
            <span className="text-[32px] font-bold text-white leading-none tracking-tight">{total.toLocaleString()}</span>
            <span className="text-[13px] text-[#94A3B8] mt-1">Total</span>
          </div>
        </div>
      </div>

      {/* Legend on the right */}
      {showLegend && (
        <div className="flex flex-col gap-3 ml-6">
          {chartData.map((entry, index) => {
            const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(1) : '0.0';
            return (
              <div key={`legend-${index}`} className="flex items-center justify-between gap-4 min-w-[200px]">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-sm font-medium text-white capitalize">
                    {entry.name}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-bold text-white whitespace-nowrap">
                    {entry.value.toLocaleString()}
                  </span>
                  <span className="text-xs font-medium text-[#94A3B8] whitespace-nowrap">
                    ({percentage}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}