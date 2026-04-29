'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';

export interface UseApiQueryOptions<T> {
  endpoint?: string;
  queryKey?: string[];
  enabled?: boolean;
  refetchInterval?: number;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retry?: number;
  retryDelay?: number;
}

export interface UseApiQueryResult<T> {
  data: T | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

// Overload signatures
export function useApiQuery<T = any>(
  endpoint: string,
  options?: Omit<UseApiQueryOptions<T>, 'endpoint'>
): UseApiQueryResult<T>;
export function useApiQuery<T = any>(
  options: UseApiQueryOptions<T>
): UseApiQueryResult<T>;

// Implementation
export function useApiQuery<T = any>(
  endpointOrOptions: string | UseApiQueryOptions<T>,
  optionsParam?: Omit<UseApiQueryOptions<T>, 'endpoint'>
): UseApiQueryResult<T> {
  // Normalize parameters
  const options: UseApiQueryOptions<T> = typeof endpointOrOptions === 'string'
    ? { endpoint: endpointOrOptions, ...optionsParam }
    : endpointOrOptions;

  const {
    endpoint = '',
    enabled = true,
    refetchInterval,
    onSuccess,
    onError,
    retry = 0,
    retryDelay = 1000,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  
  // Use ref for retry count to avoid triggering re-renders
  const retryCountRef = useRef<number>(0);
  const isMountedRef = useRef<boolean>(true);

  // Stable callbacks using refs
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  
  useEffect(() => {
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  }, [onSuccess, onError]);

  const fetchData = useCallback(async () => {
    if (!enabled || !endpoint || !isMountedRef.current) return;

    console.log(`[useApiQuery] Fetching: ${endpoint}`);

    try {
      setIsLoading(true);
      setIsError(false);
      setError(null);

      const response = await api.get<T>(endpoint);
      
      if (!isMountedRef.current) return;
      
      console.log(`[useApiQuery] Success:`, response.data);
      setData(response.data);
      retryCountRef.current = 0;

      if (onSuccessRef.current) {
        onSuccessRef.current(response.data);
      }
    } catch (err) {
      if (!isMountedRef.current) return;
      
      let errorMessage = 'An error occurred';
      
      // Extract error message from various error formats
      if (err && typeof err === 'object') {
        const axiosError = err as any;
        
        // Check for Pydantic validation errors (array of error objects)
        if (Array.isArray(axiosError.response?.data?.detail)) {
          const validationErrors = axiosError.response.data.detail;
          errorMessage = validationErrors
            .map((e: any) => `${e.loc?.join('.') || 'Field'}: ${e.msg}`)
            .join(', ');
        }
        // Check for string detail
        else if (typeof axiosError.response?.data?.detail === 'string') {
          errorMessage = axiosError.response.data.detail;
        }
        // Check for message field
        else if (axiosError.response?.data?.message) {
          errorMessage = axiosError.response.data.message;
        }
        // Check for error message
        else if (axiosError.message) {
          errorMessage = axiosError.message;
        }
      }
      
      const error = new Error(errorMessage);
      setIsError(true);
      setError(error);

      if (onErrorRef.current) {
        onErrorRef.current(error);
      }

      // Retry logic - only if retry is enabled
      if (retry > 0 && retryCountRef.current < retry) {
        const currentRetry = retryCountRef.current;
        retryCountRef.current += 1;
        
        setTimeout(() => {
          if (isMountedRef.current) {
            fetchData();
          }
        }, retryDelay * (currentRetry + 1));
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [endpoint, enabled, retry, retryDelay]);

  // Initial fetch - only runs when endpoint or enabled changes
  useEffect(() => {
    if (enabled && endpoint) {
      retryCountRef.current = 0;
      fetchData();
    }
  }, [endpoint, enabled, fetchData]);

  // Refetch interval
  useEffect(() => {
    if (!refetchInterval || !enabled || !endpoint) return;

    const interval = setInterval(() => {
      fetchData();
    }, refetchInterval);

    return () => clearInterval(interval);
  }, [refetchInterval, enabled, endpoint, fetchData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchData,
  };
}
