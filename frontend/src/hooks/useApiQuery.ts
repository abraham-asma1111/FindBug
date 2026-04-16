'use client';

import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export interface UseApiQueryOptions<T> {
  endpoint: string;
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

export function useApiQuery<T = any>(
  options: UseApiQueryOptions<T>
): UseApiQueryResult<T> {
  const {
    endpoint,
    queryKey = [],
    enabled = true,
    refetchInterval,
    onSuccess,
    onError,
    retry = 0,
    retryDelay = 1000,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(enabled);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState<number>(0);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    try {
      setIsLoading(true);
      setIsError(false);
      setError(null);

      const response = await api.get<T>(endpoint);
      setData(response.data);
      setRetryCount(0);

      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (err) {
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

      if (onError) {
        onError(error);
      }

      // Retry logic
      if (retryCount < retry) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
        }, retryDelay * (retryCount + 1));
      }
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, enabled, onSuccess, onError, retry, retryDelay, retryCount]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Refetch interval
  useEffect(() => {
    if (!refetchInterval || !enabled) return;

    const interval = setInterval(() => {
      // Only refetch if not currently loading to prevent vibration
      if (!isLoading) {
        fetchData();
      }
    }, refetchInterval);

    return () => clearInterval(interval);
  }, [refetchInterval, enabled, fetchData, isLoading]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchData,
  };
}
