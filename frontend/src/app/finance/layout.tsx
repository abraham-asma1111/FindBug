'use client';

import { useEffect } from 'react';

export default function FinanceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Force dark mode immediately on mount and keep it forced
  useEffect(() => {
    // Add dark class
    document.documentElement.classList.add('dark');
    
    // Create a MutationObserver to prevent dark class from being removed
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          if (!document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.add('dark');
          }
        }
      });
    });

    // Start observing
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    // Cleanup
    return () => {
      observer.disconnect();
    };
  }, []);

  return <>{children}</>;
}
