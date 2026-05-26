'use client';

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';

interface LineChartProps {
  data: any[];
  xKey: string;
  lines: {
    key: string;
    color: string;
    name: string;
  }[];
  height?: number;
}

export default function LineChart({ data, xKey, lines, height = 300 }: LineChartProps) {
  if (!data?.length) {
    return (
      <div
        className="flex w-full items-center justify-center text-sm text-slate-400"
        style={{ height, minHeight: height, minWidth: 0 }}
      >
        No chart data
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height, minHeight: height, minWidth: 0 }}>
    <ResponsiveContainer width="100%" height={height} minWidth={0}>
      <AreaChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
        <defs>
          {lines.map((line) => (
            <linearGradient key={`gradient-${line.key}`} id={`gradient-${line.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={line.color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={line.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} vertical={false} />
        <XAxis 
          dataKey={xKey} 
          stroke="#64748B"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#64748B' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis 
          stroke="#64748B"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#64748B' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          content={({ active, payload, label }) => {
            if (active && payload && payload.length) {
              return (
                <div className="bg-[#0F172A] border border-[#334155] rounded-lg p-3 shadow-xl">
                  <p className="text-[#94A3B8] font-semibold text-xs mb-1">{label}</p>
                  {payload.map((entry: any, index: number) => (
                    <p key={index} className="text-[#F8FAFC] font-bold text-sm">
                      {entry.value} {entry.name}
                    </p>
                  ))}
                </div>
              );
            }
            return null;
          }}
        />
        {lines.map((line) => (
          <Area
            key={`area-${line.key}`}
            type="monotone"
            dataKey={line.key}
            stroke={line.color}
            strokeWidth={3}
            fill={`url(#gradient-${line.key})`}
            dot={{ r: 3, fill: line.color, strokeWidth: 0 }}
            activeDot={{ fill: '#FFFFFF', stroke: line.color, strokeWidth: 4, r: 6 }}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
    </div>
  );
}
