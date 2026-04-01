interface StatCardProps {
  label: string;
  value: string;
  helper?: string;
  align?: 'left' | 'center';
}

export default function StatCard({
  label,
  value,
  helper,
  align = 'left',
}: StatCardProps) {
  return (
    <div className={`rounded-3xl border border-[#ddd4cb] bg-white p-5 shadow-sm ${align === 'center' ? 'text-center' : 'text-left'}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#8b8177]">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-[#2d2a26]">{value}</p>
      {helper ? <p className="mt-2 text-sm leading-relaxed text-[#6d6760]">{helper}</p> : null}
    </div>
  );
}
