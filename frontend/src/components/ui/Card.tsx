import { HTMLAttributes } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export default function Card({ 
  hover = false,
  className = '',
  children,
  ...props 
}: CardProps) {
  return (
    <div
      className={`
        bg-white dark:bg-slate-900
        border border-slate-200 dark:border-slate-800
        rounded-lg shadow-md dark:shadow-xl dark:shadow-black/20
        ${hover ? 'hover:shadow-lg dark:hover:shadow-2xl hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-200 cursor-pointer' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`px-6 py-4 border-b border-slate-200 dark:border-slate-800 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardBody({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`px-6 py-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`px-6 py-4 border-t border-slate-200 dark:border-slate-800 ${className}`} {...props}>
      {children}
    </div>
  );
}
