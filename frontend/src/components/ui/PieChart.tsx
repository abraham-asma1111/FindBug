'use client';

import { useMemo, memo } from 'react';

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

const PieChart = memo(function PieChart({ 
  data, 
  size = 200, 
  strokeWidth = 2, 
  showLabels = true,
  showLegend = true,
  className = '' 
}: PieChartProps) {
  const { segments, total, hasData } = useMemo(() => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    const hasData = total > 0;
    
    // If all values are zero, create equal segments for visualization
    if (total === 0) {
      const equalValue = 1; // Use 1 for each segment to create equal portions
      const equalSegments = data.map((item, index) => {
        const percentage = 100 / data.length; // Equal percentage for each
        const startAngle = (index * percentage) * 3.6;
        const endAngle = ((index + 1) * percentage) * 3.6;
        
        return {
          ...item,
          originalValue: item.value, // Keep original value for display
          value: equalValue,
          percentage,
          startAngle,
          endAngle,
        };
      });
      
      return { segments: equalSegments, total: 0, hasData: false };
    }
    
    // Normal calculation when there's actual data
    let cumulativePercentage = 0;
    
    const segments = data.map((item) => {
      const percentage = total > 0 ? (item.value / total) * 100 : 0;
      const startAngle = cumulativePercentage * 3.6; // Convert to degrees
      const endAngle = (cumulativePercentage + percentage) * 3.6;
      
      cumulativePercentage += percentage;
      
      return {
        ...item,
        originalValue: item.value, // Keep original value for display
        percentage,
        startAngle,
        endAngle,
      };
    });
    
    return { segments, total, hasData: true };
  }, [data]);

  const radius = (size - strokeWidth) / 2;
  const center = size / 2;

  const createArcPath = (startAngle: number, endAngle: number) => {
    // Handle full circle case
    if (endAngle - startAngle >= 360) {
      return `M ${center - radius} ${center} A ${radius} ${radius} 0 1 1 ${center + radius} ${center} A ${radius} ${radius} 0 1 1 ${center - radius} ${center}`;
    }
    
    const start = polarToCartesian(center, center, radius, endAngle);
    const end = polarToCartesian(center, center, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    
    return [
      "M", center, center,
      "L", start.x, start.y,
      "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
      "Z"
    ].join(" ");
  };

  const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    };
  };

  if (data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div 
          className="rounded-full bg-[#f3f0eb] flex items-center justify-center"
          style={{ width: size, height: size }}
        >
          <span className="text-sm text-[#8b8177]">No data</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative">
        <svg width={size} height={size} className="transform -rotate-90">
          {segments.map((segment, index) => (
            <path
              key={segment.label}
              d={createArcPath(segment.startAngle, segment.endAngle)}
              fill={segment.color}
              stroke="white"
              strokeWidth={strokeWidth}
              className="transition-opacity hover:opacity-80"
            />
          ))}
        </svg>
        
        {/* Center label showing total */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-[#2d2a26]">{total}</span>
          <span className="text-xs text-[#8b8177] uppercase tracking-wider">Total</span>
        </div>
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="mt-4 grid grid-cols-2 gap-3 w-full max-w-xs">
          {segments.map((segment) => (
            <div key={segment.label} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: segment.color }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[#2d2a26] capitalize truncate">
                    {segment.label}
                  </span>
                  <span className="text-sm font-bold text-[#2d2a26] ml-2">
                    {segment.originalValue ?? segment.value}
                  </span>
                </div>
                <div className="text-xs text-[#8b8177]">
                  {segment.percentage.toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

export default PieChart;