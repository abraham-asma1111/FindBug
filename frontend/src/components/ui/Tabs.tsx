'use client';

import {
  Children,
  ReactNode,
  createContext,
  isValidElement,
  useContext,
  useMemo,
  useState,
} from 'react';

interface Tab {
  id: string;
  label: string;
}

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

export interface TabsProps {
  tabs?: Tab[];
  defaultTab?: string;
  defaultValue?: string;
  children: ReactNode;
  className?: string;
}

export interface TabsListProps {
  children: ReactNode;
  className?: string;
}

export interface TabsTriggerProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export interface TabsContentProps {
  value: string;
  children: ReactNode;
  className?: string;
}

function useTabsContext() {
  const context = useContext(TabsContext);

  if (!context) {
    throw new Error('Tabs compound components must be used inside Tabs.');
  }

  return context;
}

export function TabsList({ children, className = '' }: TabsListProps) {
  return (
    <div className={`border-b border-[#e6ddd4] mb-6 ${className}`}>
      <nav className="flex justify-center space-x-16">{children}</nav>
    </div>
  );
}

export function TabsTrigger({ value, children, className = '' }: TabsTriggerProps) {
  const { activeTab, setActiveTab } = useTabsContext();

  return (
    <button
      type="button"
      onClick={() => setActiveTab(value)}
      className={`py-3 px-2 border-b-2 font-bold text-base transition-colors ${
        activeTab === value
          ? 'border-[#ef2330] text-[#ef2330]'
          : 'border-transparent text-[#6d6760] hover:text-[#2d2a26] hover:border-[#d8d0c8]'
      } ${className}`}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className = '' }: TabsContentProps) {
  const { activeTab } = useTabsContext();

  if (activeTab !== value) {
    return null;
  }

  return <div className={className}>{children}</div>;
}

export default function Tabs({
  tabs = [],
  defaultTab,
  defaultValue,
  children,
  className = '',
}: TabsProps) {
  const initialTab = defaultValue || defaultTab || tabs[0]?.id || '';
  const [activeTab, setActiveTab] = useState(initialTab);

  const contextValue = useMemo(
    () => ({
      activeTab,
      setActiveTab,
    }),
    [activeTab]
  );

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={className}>
        {tabs.length ? (
          <>
            <TabsList>
              {tabs.map((tab) => (
                <TabsTrigger key={tab.id} value={tab.id}>
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>

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
          </>
        ) : (
          <div>{children}</div>
        )}
      </div>
    </TabsContext.Provider>
  );
}
