'use client';

import { ReactNode, useState, Children, isValidElement } from 'react';

interface Tab {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab: string;
  children: ReactNode;
  className?: string;
}

export default function Tabs({ tabs, defaultTab, children, className = '' }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <div className={className}>
      {/* Tab Navigation */}
      <div className="border-b border-[#e6ddd4] mb-6">
        <nav className="flex justify-center space-x-16">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-2 border-b-2 font-bold text-base transition-colors ${
                activeTab === tab.id
                  ? 'border-[#ef2330] text-[#ef2330]'
                  : 'border-transparent text-[#6d6760] hover:text-[#2d2a26] hover:border-[#d8d0c8]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {Children.map(children, (child) => {
          if (isValidElement(child) && child.props['data-tab']) {
            const tabId = child.props['data-tab'];
            if (tabId === activeTab) {
              return child;
            }
          }
          return null;
        })}
      </div>
    </div>
  );
}
