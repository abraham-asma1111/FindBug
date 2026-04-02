import { InputHTMLAttributes, forwardRef } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', required, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-[#2d2a26] mb-2">
            {label}
            {required && <span className="text-[#b42318] ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          className={`
            w-full px-4 py-2.5 rounded-xl
            bg-white
            border ${error ? 'border-[#f2c0bc]' : 'border-[#e6ddd4]'}
            text-[#2d2a26]
            placeholder:text-[#8b8177]
            focus:outline-none focus:ring-2 ${error ? 'focus:ring-[#f2c0bc]' : 'focus:ring-[#2d2a26]'} focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[#faf6f1]
            transition-all
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-sm text-[#b42318]">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-[#6d6760]">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
