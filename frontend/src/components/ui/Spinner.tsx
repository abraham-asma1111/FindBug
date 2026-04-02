import { HTMLAttributes } from 'react';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'slate';
}

export default function Spinner({ 
  size = 'md',
  color = 'primary',
  className = '',
  ...props 
}: SpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
    xl: 'w-16 h-16 border-4',
  };
  
  const colors = {
    primary: 'border-blue-500 border-t-transparent',
    white: 'border-white border-t-transparent',
    slate: 'border-slate-500 border-t-transparent',
  };
  
  return (
    <div
      className={`
        animate-spin rounded-full
        ${sizes[size]}
        ${colors[color]}
        ${className}
      `}
      {...props}
    />
  );
}
