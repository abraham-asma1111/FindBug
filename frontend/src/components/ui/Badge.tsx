import { HTMLAttributes } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'info' | 'new' | 'pending' | 'approved' | 'rejected' | 'resolved';
  size?: 'sm' | 'md' | 'lg';
}

export default function Badge({ 
  variant = 'info', 
  size = 'md',
  className = '',
  children,
  ...props 
}: BadgeProps) {
  const variants = {
    // Severity badges
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-amber-500 text-white',
    low: 'bg-emerald-500 text-white',
    info: 'bg-blue-500 text-white',
    
    // Status badges
    new: 'bg-blue-500 text-white',
    pending: 'bg-amber-500 text-white',
    approved: 'bg-emerald-500 text-white',
    rejected: 'bg-red-600 text-white',
    resolved: 'bg-slate-500 text-white',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm',
  };
  
  return (
    <span
      className={`
        inline-flex items-center rounded-full font-medium
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
}
