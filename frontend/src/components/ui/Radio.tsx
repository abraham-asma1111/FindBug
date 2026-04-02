import { InputHTMLAttributes, forwardRef } from 'react';

export interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

const Radio = forwardRef<HTMLInputElement, RadioProps>(
  ({ label, className = '', ...props }, ref) => {
    return (
      <label className="inline-flex items-center cursor-pointer">
        <input
          ref={ref}
          type="radio"
          className={`
            w-4 h-4 rounded-full
            border-slate-300 dark:border-slate-700
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
    );
  }
);

Radio.displayName = 'Radio';

export default Radio;
