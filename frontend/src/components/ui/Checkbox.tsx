import { InputHTMLAttributes, forwardRef } from 'react';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  helperText?: string;
}

const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, helperText, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        <label className="inline-flex items-center cursor-pointer">
          <input
            ref={ref}
            type="checkbox"
            className={`
              w-4 h-4 rounded
              border-slate-300 dark:border-gray-700
              text-blue-500
              focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
              ${className}
            `}
            {...props}
          />
          {label && (
            <span className="ml-2 text-sm text-slate-900 dark:text-slate-100">
              {label}
            </span>
          )}
        </label>
        {helperText && (
          <p className="mt-1.5 ml-6 text-sm text-[#6d6760] dark:text-slate-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

export default Checkbox;
