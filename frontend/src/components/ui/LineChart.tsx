'use client';

import { Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

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
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey={xKey} 
          stroke="#94A3B8"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#94A3B8"
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#F8FAFC',
          }}
          labelStyle={{ color: '#94A3B8' }}
        />
        <Legend 
          wrapperStyle={{ color: '#94A3B8', fontSize: '12px' }}
        />
        {lines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            stroke={line.color}
            strokeWidth={2}
            name={line.name}
            dot={{ fill: line.color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}
