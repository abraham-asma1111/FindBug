import { HTMLAttributes } from 'react';

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export default function Avatar({ 
  src, 
  alt = 'Avatar', 
  fallback,
  size = 'md',
  className = '',
  ...props 
}: AvatarProps) {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };
  
  const getInitials = (name?: string) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
  
  return (
    <div
      className={`
        ${sizes[size]}
        rounded-full overflow-hidden
        bg-blue-500 text-white
        flex items-center justify-center
        font-medium
        ring-2 ring-blue-500/30
        ${className}
      `}
      {...props}
    >
      {src ? (
        <img src={src} alt={alt} className="w-full h-full object-cover" />
      ) : (
        <span>{getInitials(fallback || alt)}</span>
      )}
    </div>
  );
}
