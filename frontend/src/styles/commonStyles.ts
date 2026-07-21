/**
 * Common Style Constants
 * 
 * Reusable style classes for consistent design across pages
 * Used in: PTaaS, Code Review, Live Hacking Events, AI Red Teaming, etc.
 */

export const commonStyles = {
  // Hero Section
  hero: {
    container: 'relative w-full overflow-hidden rounded-2xl h-[600px]',
    image: 'absolute inset-0 w-full h-full object-cover',
    overlay: 'absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent',
    content: 'relative z-10 h-full flex items-end justify-center pb-6',
    title: 'text-7xl font-black text-white drop-shadow-2xl mb-6',
    subtitle: 'text-4xl font-bold text-white drop-shadow-2xl',
  },

  // Section Containers
  section: {
    main: 'rounded-2xl bg-white dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6',
    title: 'text-2xl font-bold text-slate-900 dark:text-white mb-4',
    titleCenter: 'text-2xl font-bold text-slate-900 dark:text-white mb-4 text-center',
    description: 'text-base text-slate-600 dark:text-gray-300 mb-6 text-center',
  },

  // Feature Cards
  featureCard: {
    container: 'rounded-2xl bg-white dark:bg-[#111111] border border-slate-200 dark:border-gray-800 p-6 text-center',
    icon: 'text-3xl mb-3',
    title: 'font-semibold text-slate-900 dark:text-white mb-2',
    description: 'text-sm text-slate-600 dark:text-gray-300',
  },

  // Nested Cards (inside sections)
  nestedCard: {
    container: 'rounded-xl bg-slate-50 dark:bg-gray-900 p-4 border border-slate-200 dark:border-gray-700',
    title: 'font-semibold text-slate-900 dark:text-white mb-2',
    description: 'text-sm text-slate-600 dark:text-gray-300',
  },

  // Expandable/Interactive Cards
  interactiveCard: {
    base: 'w-full rounded-lg bg-white dark:bg-[#111111] p-6 border transition-all duration-300 text-left min-h-[180px]',
    default: 'border-slate-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-lg',
    expanded: 'border-blue-500 dark:border-blue-500 shadow-xl',
  },

  // Step/Process Lists
  stepList: {
    container: 'space-y-4',
    step: 'flex gap-4',
    number: 'flex-shrink-0 w-8 h-8 rounded-full bg-[#ef2330] text-white flex items-center justify-center font-bold text-sm',
    content: '',
    title: 'font-semibold text-slate-900 dark:text-white',
    description: 'text-sm text-slate-600 dark:text-gray-300 mt-1',
  },

  // Grid Layouts
  grid: {
    twoCol: 'grid grid-cols-1 md:grid-cols-2 gap-4',
    threeCol: 'grid grid-cols-1 md:grid-cols-3 gap-6',
    fourCol: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4',
  },

  // Text Styles
  text: {
    heading1: 'text-2xl font-bold text-slate-900 dark:text-white',
    heading2: 'text-xl font-bold text-slate-900 dark:text-white',
    heading3: 'text-lg font-semibold text-slate-900 dark:text-white',
    body: 'text-base text-slate-600 dark:text-gray-300',
    bodySmall: 'text-sm text-slate-600 dark:text-gray-300',
    label: 'text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-gray-400',
  },

  // Spacing
  spacing: {
    pageContainer: 'space-y-6',
    sectionGap: 'space-y-4',
  },

  // Badges/Tags
  badge: {
    default: 'inline-block text-xs px-2 py-0.5 rounded-full',
    primary: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    success: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
    warning: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
    danger: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
  },
};

/**
 * Helper function to combine style classes
 */
export const cx = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ');
};

/**
 * Brand Colors
 */
export const brandColors = {
  primary: '#ef2330',
  primaryHover: '#d81c29',
  blue: '#3b82f6',
  blueHover: '#2563eb',
};
