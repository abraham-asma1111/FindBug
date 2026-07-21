import { ReactNode, SelectHTMLAttributes, forwardRef } from 'react';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options?: { value: string; label: string }[];
  children?: ReactNode;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options = [], children, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`
            w-full px-4 py-2 rounded-lg
            bg-white dark:bg-[#111111]
            border ${error ? 'border-red-500' : 'border-slate-300 dark:border-gray-700'}
            text-slate-900 dark:text-slate-100
            focus:outline-none focus:ring-2 ${error ? 'focus:ring-red-500' : 'focus:ring-blue-500'}
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
            ${className}
          `}
          {...props}
        >
          {children ||
            options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
        </select>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
