'use client';

import { Component, ReactNode } from 'react';
import { logError } from '@/lib/errors';
import Button from '@/components/ui/Button';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logError(error, { errorInfo });
  }

  resetErrorBoundary = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.resetErrorBoundary);
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4">
          <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6 border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 dark:bg-red-900/20 rounded-full">
              <svg
                className="w-6 h-6 text-red-600 dark:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            
            <h2 className="text-xl font-bold text-center text-slate-900 dark:text-slate-100 mb-2">
              Something went wrong
            </h2>
            
            <p className="text-center text-slate-600 dark:text-slate-400 mb-4">
              {this.state.error.message || 'An unexpected error occurred'}
            </p>
            
            {process.env.NODE_ENV === 'development' && (
              <details className="mb-4 p-3 bg-slate-100 dark:bg-slate-800 rounded text-xs">
                <summary className="cursor-pointer text-slate-700 dark:text-slate-300 font-medium mb-2">
                  Error Details
                </summary>
                <pre className="text-slate-600 dark:text-slate-400 overflow-auto">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
            
            <div className="flex gap-3">
              <Button
                variant="primary"
                className="flex-1"
                onClick={this.resetErrorBoundary}
              >
                Try Again
              </Button>
              <Button
                variant="secondary"
                className="flex-1"
                onClick={() => window.location.href = '/'}
              >
                Go Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
