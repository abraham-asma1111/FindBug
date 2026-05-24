'use client';

import { useState, useRef, useCallback, useMemo } from 'react';

interface DataPoint {
  date: string;
  amount: number;
  commission?: number;
}

interface TooltipState {
  x: number;
  y: number;
  date: string;
  amount: number;
  visible: boolean;
}

// Smooth Catmull-Rom → cubic bezier spline
function smoothPath(pts: { x: number; y: number }[], tension = 0.3): string {
  if (pts.length === 0) return '';
  if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`;

  let d = `M ${pts[0].x.toFixed(2)} ${pts[0].y.toFixed(2)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const curr = pts[i];
    const next = pts[i + 1];
    const prev = i > 0 ? pts[i - 1] : curr;
    const after = i < pts.length - 2 ? pts[i + 2] : next;

    const cp1x = curr.x + (next.x - prev.x) * tension;
    const cp1y = curr.y + (next.y - prev.y) * tension;
    const cp2x = next.x - (after.x - curr.x) * tension;
    const cp2y = next.y - (after.y - curr.y) * tension;

    d += ` C ${cp1x.toFixed(2)} ${cp1y.toFixed(2)}, ${cp2x.toFixed(2)} ${cp2y.toFixed(2)}, ${next.x.toFixed(2)} ${next.y.toFixed(2)}`;
  }
  return d;
}

function fmtY(v: number): string {
  if (v >= 1_000_000) return `ETB ${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `ETB ${(v / 1_000).toFixed(0)}k`;
  return `ETB ${v}`;
}

const GRAD_STOPS = [
  { offset: '0%',   color: '#06B6D4' },
  { offset: '30%',  color: '#10B981' },
  { offset: '60%',  color: '#F59E0B' },
  { offset: '80%',  color: '#F97316' },
  { offset: '100%', color: '#EF4444' },
];

const VW = 700;
const PAD = { top: 20, right: 24, bottom: 36, left: 72 };

export default function BountyTrendChart({ data, height = 290 }: { data: DataPoint[]; height?: number }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState>({ x: 0, y: 0, date: '', amount: 0, visible: false });
  const [activeIdx, setActiveIdx] = useState<number | null>(null);

  const chartW = VW - PAD.left - PAD.right;
  const chartH = height - PAD.top - PAD.bottom;

  const { points, yTicks, xStep } = useMemo(() => {
    if (!data || data.length === 0) return { points: [], yTicks: [], xStep: 0 };

    const maxVal = Math.max(...data.map(d => d.amount));
    const niceMax = Math.ceil(maxVal / 50_000) * 50_000 || 250_000;
    const xStep = chartW / Math.max(data.length - 1, 1);

    const points = data.map((d, i) => ({
      x: PAD.left + i * xStep,
      y: PAD.top + chartH - (d.amount / niceMax) * chartH,
      date: d.date,
      amount: d.amount,
    }));

    const TICKS = 6;
    const yTicks = Array.from({ length: TICKS }, (_, i) => ({
      value: (niceMax / (TICKS - 1)) * i,
      y: PAD.top + chartH - (i / (TICKS - 1)) * chartH,
    }));

    return { points, yTicks, xStep };
  }, [data, chartW, chartH]);

  const linePath = useMemo(() => smoothPath(points, 0.3), [points]);
  const areaPath = useMemo(() => {
    if (points.length === 0) return '';
    const bot = PAD.top + chartH;
    return `${linePath} L ${points[points.length - 1].x.toFixed(2)} ${bot} L ${points[0].x.toFixed(2)} ${bot} Z`;
  }, [linePath, points, chartH]);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current || points.length === 0) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * VW;
    let best = 0, bestDist = Infinity;
    points.forEach((pt, i) => {
      const d = Math.abs(pt.x - mouseX);
      if (d < bestDist) { bestDist = d; best = i; }
    });
    if (bestDist < xStep) {
      setActiveIdx(best);
      setTooltip({ x: points[best].x, y: points[best].y, date: points[best].date, amount: points[best].amount, visible: true });
    }
  }, [points, xStep]);

  const handleMouseLeave = useCallback(() => {
    setActiveIdx(null);
    setTooltip(t => ({ ...t, visible: false }));
  }, []);

  // Empty state — no DB data yet
  if (!data || data.length === 0) {
    return (
      <div style={{
        height,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
        color: '#475569',
      }}>
        <svg width="44" height="44" fill="none" stroke="#334155" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M7 12l3-3 3 3 4-4M3 20h18" />
        </svg>
        <p style={{ fontSize: 13, color: '#64748B', margin: 0 }}>No payout data yet</p>
        <p style={{ fontSize: 11, color: '#475569', margin: 0 }}>Trend will appear once payments are recorded</p>
      </div>
    );
  }

  // Tooltip box placement — keep inside chart
  const tipX = tooltip.x > VW * 0.7 ? tooltip.x - 158 : tooltip.x + 12;
  const tipY = tooltip.y < 60 ? tooltip.y + 12 : tooltip.y - 68;

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${VW} ${height}`}
      style={{ width: '100%', height, overflow: 'visible', cursor: 'crosshair', display: 'block' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <defs>
        <linearGradient id="btLineGrad" x1="0" y1="0" x2="1" y2="0">
          {GRAD_STOPS.map(s => <stop key={s.offset} offset={s.offset} stopColor={s.color} />)}
        </linearGradient>

        <linearGradient id="btAreaGrad" x1="0" y1="0" x2="1" y2="0">
          {GRAD_STOPS.map(s => <stop key={s.offset} offset={s.offset} stopColor={s.color} stopOpacity={0.55} />)}
        </linearGradient>

        <linearGradient id="btFadeGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="white" stopOpacity={1} />
          <stop offset="100%" stopColor="white" stopOpacity={0} />
        </linearGradient>
        <mask id="btFadeMask">
          <rect x={PAD.left} y={PAD.top} width={chartW} height={chartH} fill="url(#btFadeGrad)" />
        </mask>

        <clipPath id="btClip">
          <rect x={PAD.left} y={PAD.top} width={chartW} height={chartH} />
        </clipPath>
      </defs>

      {/* Grid lines + Y labels */}
      {yTicks.map((tick, i) => (
        <g key={i}>
          <line
            x1={PAD.left} y1={tick.y}
            x2={PAD.left + chartW} y2={tick.y}
            stroke="#1E3A5F" strokeDasharray="4 4" strokeWidth={1}
          />
          <text x={PAD.left - 8} y={tick.y + 4} textAnchor="end" fontSize={11} fill="#64748B">
            {fmtY(tick.value)}
          </text>
        </g>
      ))}

      {/* X-axis labels */}
      {points.map((pt, i) => (
        <text key={i} x={pt.x} y={PAD.top + chartH + 22} textAnchor="middle" fontSize={11} fill="#64748B">
          {pt.date}
        </text>
      ))}

      {/* Clipped gradient area + line */}
      <g clipPath="url(#btClip)">
        <path d={areaPath} fill="url(#btAreaGrad)" mask="url(#btFadeMask)" />
        <path d={linePath} fill="none" stroke="url(#btLineGrad)" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
      </g>

      {/* Active dot with glow */}
      {activeIdx !== null && points[activeIdx] && (() => {
        const pt = points[activeIdx];
        const pct = (pt.x - PAD.left) / chartW;
        const dotColor = pct < 0.3 ? '#10B981' : pct < 0.6 ? '#F59E0B' : '#EF4444';
        return (
          <g>
            <line x1={pt.x} y1={PAD.top} x2={pt.x} y2={PAD.top + chartH}
              stroke="#334155" strokeDasharray="4 3" strokeWidth={1} />
            <circle cx={pt.x} cy={pt.y} r={18} fill={dotColor} fillOpacity={0.07} />
            <circle cx={pt.x} cy={pt.y} r={11} fill={dotColor} fillOpacity={0.18} />
            <circle cx={pt.x} cy={pt.y} r={5}  fill="#0F172A" stroke={dotColor} strokeWidth={2.5} />
          </g>
        );
      })()}

      {/* Tooltip */}
      {tooltip.visible && (
        <g>
          <rect x={tipX} y={tipY} width={148} height={58} rx={8} ry={8}
            fill="rgba(10,18,35,0.96)" stroke="#1E3A5F" strokeWidth={1}
            filter="drop-shadow(0 0 10px rgba(6,182,212,0.25))"
          />
          <text x={tipX + 12} y={tipY + 18} fontSize={11} fill="#94A3B8" fontWeight={600}>
            {tooltip.date}
          </text>
          <circle cx={tipX + 14} cy={tipY + 36} r={4} fill="#10B981" />
          <text x={tipX + 22} y={tipY + 40} fontSize={13} fill="#10B981" fontWeight={700}>
            ETB {tooltip.amount.toLocaleString()}
          </text>
        </g>
      )}

      {/* Legend */}
      <g>
        <defs>
          <linearGradient id="legendGrad" x1="0" y1="0" x2="1" y2="0">
            {GRAD_STOPS.map(s => <stop key={s.offset} offset={s.offset} stopColor={s.color} />)}
          </linearGradient>
        </defs>
        <rect x={PAD.left} y={PAD.top - 16} width={24} height={3} rx={2} fill="url(#legendGrad)" />
        <text x={PAD.left + 28} y={PAD.top - 12} fontSize={11} fill="#64748B">Bounty Payment</text>
      </g>
    </svg>
  );
}
