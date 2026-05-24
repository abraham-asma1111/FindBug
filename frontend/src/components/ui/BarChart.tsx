'use client';

import { useMemo } from 'react';

interface BarChartData {
  label: string;
  value: number;
  color: string;
}

interface BarChartProps {
  data: BarChartData[];
  height?: number;
  showValues?: boolean;
  valueFormatter?: (value: number) => string;
}

export default function BarChart({ 
  data, 
  height = 200,
  showValues = true,
  valueFormatter = (value) => value.toString()
}: BarChartProps) {
  const maxValue = useMemo(() => Math.max(...data.map(d => d.value), 0), [data]);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <span className="text-sm text-gray-400">No data available</span>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* Chart area with bars */}
      <div style={{ height: height - 30 }} className="flex items-end justify-center gap-3 px-6 relative">
        {data.map((item, index) => {
          const barHeightPercent = maxValue > 0 ? (item.value / maxValue) * 100 : 0;
          
          return (
            <div key={index} className="flex flex-col items-center justify-end" style={{ flex: 1, maxWidth: '140px', height: '100%' }}>
              {/* Value label on top */}
              {showValues && item.value > 0 && (
                <div className="mb-2 text-sm font-semibold text-gray-200">
                  {valueFormatter(item.value)}
                </div>
              )}
              
              {/* Bar - extends to bottom */}
              <div
                className="w-full rounded-t transition-all duration-300 hover:opacity-80"
                style={{
                  height: `${barHeightPercent}%`,
                  backgroundColor: item.color,
                  minHeight: item.value > 0 ? '40px' : '0px',
                }}
              />
            </div>
          );
        })}
      </div>
      
      {/* X-axis labels below the chart */}
      <div className="flex items-start justify-center gap-3 px-6 pt-2">
        {data.map((item, index) => (
          <div key={index} className="flex items-center justify-center" style={{ flex: 1, maxWidth: '140px' }}>
            <span className="text-xs font-medium text-gray-300 whitespace-nowrap">
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
