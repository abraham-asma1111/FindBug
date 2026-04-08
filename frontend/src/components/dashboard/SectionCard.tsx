import type { ReactNode } from 'react';

interface SectionCardProps {
  title: string;
  description?: string;
  headerAlign?: 'left' | 'center';
  titleClassName?: string;
  children: ReactNode;
}

export default function SectionCard({
  title,
  description,
  headerAlign = 'left',
  titleClassName = '',
  children,
}: SectionCardProps) {
  return (
    <section className="rounded-3xl border border-[#ddd4cb] dark:border-gray-800 bg-white dark:bg-[#111111] dark:bg-[#111111] p-6 shadow-sm text-left">
      <div className={`mb-5 ${headerAlign === 'center' ? 'text-center' : 'text-left'}`}>
        <h2 className={`font-semibold text-[#2d2a26] dark:text-white ${titleClassName || 'text-lg'}`}>{title}</h2>
        {description ? <p className="mt-1 text-sm text-[#6d6760] dark:text-gray-400">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
