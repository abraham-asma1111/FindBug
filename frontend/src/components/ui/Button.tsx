import { ButtonHTMLAttributes, forwardRef } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'danger' | 'success' | 'warning' | 'secondary' | 'outline' | 'ghost';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    isLoading = false,
    className = '',
    children,
    disabled,
    ...props 
  }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    // SecureCrowd Button System
    const variants = {
      primary: 'bg-[#3B82F6] hover:bg-[#2563EB] text-white focus:ring-[#3B82F6]',
      success: 'bg-[#10B981] hover:bg-[#059669] text-white focus:ring-[#10B981]',
      danger: 'bg-[#EF4444] hover:bg-[#DC2626] text-white focus:ring-[#EF4444]',
      warning: 'bg-[#F59E0B] hover:bg-[#D97706] text-white focus:ring-[#F59E0B]',
      secondary: 'bg-[#64748B] hover:bg-[#475569] text-white focus:ring-[#64748B]',
      outline: 'border border-[#334155] text-[#F8FAFC] hover:border-[#475569] hover:bg-[#1E293B] focus:ring-[#3B82F6]',
      ghost: 'text-[#64748B] hover:text-[#94A3B8] hover:bg-[#1E293B] focus:ring-[#64748B]',
    };
    
    const sizes = {
      xs: 'px-2 py-1 text-xs',
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    };
    
    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
          </>
        ) : children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
