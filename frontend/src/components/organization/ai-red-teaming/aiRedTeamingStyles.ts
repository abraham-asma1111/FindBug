/** Shared compact layout + dark-mode-safe text for AI Red Teaming UI */
export const aiRt = {
  page: 'space-y-3',
  grid: 'grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  card: 'rounded-xl border border-[#e6ddd4] bg-white p-3 transition-colors dark:border-slate-700 dark:bg-slate-800/90',
  cardHover: 'hover:border-violet-500/60 dark:hover:border-violet-400/50',
  title: 'text-sm font-semibold text-[#2d2a26] dark:text-slate-100 line-clamp-2',
  subtitle: 'text-xs text-[#6d6760] dark:text-slate-400 line-clamp-1',
  body: 'text-xs text-[#6d6760] dark:text-slate-300',
  label: 'text-[10px] font-medium uppercase tracking-wide text-[#8b8177] dark:text-slate-500',
  stat: 'text-sm font-semibold text-[#2d2a26] dark:text-slate-100',
  accentBox: 'rounded-lg bg-violet-50 px-2 py-1.5 dark:bg-violet-950/40',
  accentText: 'text-xs font-medium text-violet-800 dark:text-violet-200',
  divider: 'border-t border-[#e6ddd4] dark:border-slate-700 pt-2 mt-2',
} as const;

export const aiRtStatusColors: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200',
  pending: 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-200',
  active: 'bg-violet-100 text-violet-800 dark:bg-violet-950/50 dark:text-violet-200',
  testing: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/50 dark:text-yellow-200',
  completed: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-200',
  archived: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
};

export const aiRtModelLabels: Record<string, string> = {
  llm: 'LLM',
  ml_model: 'ML Model',
  ai_agent: 'AI Agent',
  chatbot: 'Chatbot',
  recommendation_system: 'Recommendation',
  computer_vision: 'Computer Vision',
};
