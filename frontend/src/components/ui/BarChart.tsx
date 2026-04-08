'use client';

import { useMemo, memo } from 'react';

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
  yAxisInterval?: number; // Custom interval for Y-axis (e.g., 5000 for ETB)
  className?: string;
}

const BarChart = memo(function BarChart({ 
  data, 
  height = 300,
  showValues = true,
  valueFormatter = (value) => value.toString(),
  yAxisInterval,
  className = '' 
}: BarChartProps) {
  const { maxValue, bars, yAxisLabels } = useMemo(() => {
    const dataMax = Math.max(...data.map(d => d.value), 0);
    
    let maxValue: number;
    let yAxisLabels: number[];
    
    if (yAxisInterval) {
      // Use custom interval (e.g., 5000 for ETB)
      // Round up to next interval
      maxValue = Math.ceil(dataMax / yAxisInterval) * yAxisInterval;
      
      // If maxValue is 0, set a minimum
      if (maxValue === 0) {
        maxValue = yAxisInterval * 5; // Show 5 intervals minimum
      }
      
      // Create labels at each interval
      yAxisLabels = [];
      for (let i = maxValue; i >= 0; i -= yAxisInterval) {
        yAxisLabels.push(i);
      }
    } else {
      // Original automatic scaling
      maxValue = Math.ceil(dataMax) || 5;
      
      if (maxValue <= 5) {
        yAxisLabels = [maxValue, Math.floor(maxValue * 0.75), Math.floor(maxValue * 0.5), Math.floor(maxValue * 0.25), 0];
      } else {
        yAxisLabels = [
          maxValue,
          Math.ceil(maxValue * 0.75),
          Math.ceil(maxValue * 0.5),
          Math.ceil(maxValue * 0.25),
          0
        ];
      }
    }
    
    const bars = data.map((item) => ({
      ...item,
      heightPercent: maxValue > 0 ? (item.value / maxValue) * 100 : 0,
    }));
    
    return { maxValue, bars, yAxisLabels };
  }, [data, yAxisInterval]);

  if (data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height }}>
        <span className="text-sm text-[#8b8177] dark:text-gray-400">No data available</span>
      </div>
    );
  }

  const barWidth = 100 / data.length;
  const barGap = 10; // percentage of bar width to use as gap

  return (
    <div className={className}>
      <div className="relative" style={{ height }}>
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-[#8b8177] dark:text-gray-400 pr-2">
          {yAxisLabels.map((label, index) => (
            <span key={index} className="text-right">{valueFormatter(label)}</span>
          ))}
        </div>

        {/* Chart area */}
        <div className="absolute left-12 right-0 top-0 bottom-12 border-l-2 border-b-2 border-[#e6ddd4] dark:border-gray-600">
          {/* Horizontal grid lines */}
          <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
            {yAxisLabels.map((_, index) => (
              <div key={index} className="border-t-2 border-[#f3f0eb] dark:border-gray-700" />
            ))}
          </div>
          
          <div className="relative h-full flex items-end justify-around px-4 gap-2">
            {bars.map((bar, index) => (
              <div
                key={`${bar.label}-${index}`}
                className="flex flex-col items-center justify-end h-full"
                style={{ width: `${barWidth - barGap}%`, minWidth: '30px' }}
              >
                {/* Value label on top of bar */}
                {showValues && bar.value > 0 && (
                  <div className="mb-1 text-xs font-semibold text-[#2d2a26] dark:text-gray-200">
                    {valueFormatter(bar.value)}
                  </div>
                )}
                
                {/* Bar */}
                <div
                  className="w-full rounded-t-lg transition-all duration-300 hover:opacity-80"
                  style={{
                    height: `${bar.heightPercent}%`,
                    backgroundColor: bar.color,
                    minHeight: bar.value > 0 ? '8px' : '0px',
                  }}
                  title={`${bar.label}: ${valueFormatter(bar.value)}`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* X-axis labels */}
        <div className="absolute left-12 right-0 bottom-0 h-12 flex items-start justify-around px-1 pt-2">
          {bars.map((bar, index) => (
            <div
              key={`${bar.label}-label-${index}`}
              className="text-[10px] font-medium text-[#2d2a26] dark:text-gray-300 text-center leading-tight"
              style={{ 
                width: `${barWidth - barGap}%`, 
                minWidth: '30px',
                maxWidth: '80px',
                wordBreak: 'break-word',
                hyphens: 'auto'
              }}
              title={bar.label}
            >
              {bar.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

export default BarChart;
