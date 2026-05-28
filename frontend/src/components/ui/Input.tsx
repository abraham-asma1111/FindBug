import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export function Input({ error, className = "", ...props }: InputProps) {
  const baseClasses = "w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors";
  const normalClasses = "border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500";
  const errorClasses = "border-red-500 focus:ring-red-500 focus:border-red-500";
  const bgClasses = "bg-white dark:bg-gray-800 text-gray-900 dark:text-white";
  const placeholderClasses = "placeholder-gray-400 dark:placeholder-gray-500";

  return (
    <div className="w-full">
      <input
        className={`${baseClasses} ${error ? errorClasses : normalClasses} ${bgClasses} ${placeholderClasses} ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}

export default Input;
