import type { ReactNode } from 'react';

interface SectionCardProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export default function SectionCard({ title, description, children }: SectionCardProps) {
  return (
    <section className="rounded-3xl border border-[#ddd4cb] bg-white p-6 shadow-sm text-left">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-[#2d2a26]">{title}</h2>
        {description ? <p className="mt-1 text-sm text-[#6d6760]">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
