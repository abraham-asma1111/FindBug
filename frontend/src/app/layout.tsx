import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Providers from '@/components/providers'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'FindBug - Bug Bounty Platform',
  description: 'Ethiopian Bug Bounty and Penetration Testing Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  // Check if we're on a finance or triage portal page
                  const path = window.location.pathname;
                  const isFinanceOrTriage = path.startsWith('/finance') || path.startsWith('/triage');
                  
                  if (isFinanceOrTriage) {
                    // Force dark mode for finance and triage portals
                    document.documentElement.classList.add('dark');
                  } else {
                    // For other pages, check localStorage
                    const theme = localStorage.getItem('theme');
                    if (theme === 'dark') {
                      document.documentElement.classList.add('dark');
                    }
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
