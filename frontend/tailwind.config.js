/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Blue (Exact from Triage screenshot)
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          DEFAULT: '#3b82f6',  // Primary accent/buttons
          hover: '#2563eb',
        },
        // Danger - Red (Critical badge)
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          DEFAULT: '#ef4444',  // Critical badge
          hover: '#dc2626',
        },
        // Success/Warning - Amber (High badge)
        success: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          DEFAULT: '#f59e0b',  // High badge
          hover: '#d97706',
        },
        // Supporting colors
        warning: {
          DEFAULT: '#f97316',
          hover: '#ea580c',
        },
        info: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
        },
        // Exact Triage Portal colors
        triage: {
          'page-bg': '#0F172A',        // Main background
          'sidebar-bg': '#020617',     // Sidebar background
          'card-bg': '#1E2937',        // Card backgrounds
          'active-menu': '#2563EB',    // Active menu item
          'badge-blue': '#2563EB',     // "12 New" badge
          'button-primary': '#3B82F6', // Primary buttons
          'critical': '#EF4444',       // Critical badge
          'high': '#F59E0B',           // High badge
          'text-main': '#F8FAFC',      // Main text
          'text-secondary': '#94A3B8', // Secondary text
          'hover': '#334155',          // Hover states
          'border': '#334155',         // Borders/dividers
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Courier New', 'monospace'],
      },
      boxShadow: {
        'dark-md': '0 4px 6px -1px rgba(0, 0, 0, 0.2)',
        'dark-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
        'dark-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
      },
    },
  },
  plugins: [],
}
