'use client';

interface Tab {
  id: string;
  label: string;
  count?: number;
}

interface SimpleTabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export default function SimpleTabs({ tabs, activeTab, onChange, className = '' }: SimpleTabsProps) {
  return (
    <div className={`border-b border-[#e6ddd4] ${className}`}>
      <nav className="flex justify-center space-x-12">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`py-3 px-2 border-b-2 font-semibold text-base transition-colors ${
              activeTab === tab.id
                ? 'border-[#2d2a26] text-[#2d2a26]'
                : 'border-transparent text-[#6d6760] hover:text-[#2d2a26] hover:border-[#d8d0c8]'
            }`}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className={`ml-2 rounded-full px-2 py-0.5 text-xs ${
                activeTab === tab.id
                  ? 'bg-[#2d2a26] text-white'
                  : 'bg-[#e6ddd4] text-[#6d6760]'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
}
