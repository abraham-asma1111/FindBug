'use client';

import { useState, useCallback } from 'react';
import api from '@/lib/api';

export interface UseApiMutationOptions<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: Error, variables: TVariables) => void;
  onSettled?: (data: TData | null, error: Error | null, variables: TVariables) => void;
}

export interface UseApiMutationResult<TData, TVariables> {
  mutate: (variables: TVariables) => Promise<TData | null>;
  mutateAsync: (variables: TVariables) => Promise<TData>;
  data: TData | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isSuccess: boolean;
  reset: () => void;
}

export function useApiMutation<TData = any, TVariables = any>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
  options: UseApiMutationOptions<TData, TVariables> = {}
): UseApiMutationResult<TData, TVariables> {
  const { onSuccess, onError, onSettled } = options;

  const [data, setData] = useState<TData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const reset = useCallback(() => {
    setData(null);
    setIsLoading(false);
    setIsError(false);
    setError(null);
    setIsSuccess(false);
  }, []);

  const mutate = useCallback(
    async (variables: TVariables): Promise<TData | null> => {
      try {
        setIsLoading(true);
        setIsError(false);
        setError(null);
        setIsSuccess(false);

        let response: TData;

        switch (method) {
          case 'POST':
            response = (await api.post<TData>(endpoint, variables)).data;
            break;
          case 'PUT':
            response = (await api.put<TData>(endpoint, variables)).data;
            break;
          case 'PATCH':
            response = (await api.patch<TData>(endpoint, variables)).data;
            break;
          case 'DELETE':
            response = (await api.delete<TData>(endpoint)).data;
            break;
          default:
            throw new Error(`Unsupported method: ${method}`);
        }

        setData(response);
        setIsSuccess(true);

        if (onSuccess) {
          onSuccess(response, variables);
        }

        if (onSettled) {
          onSettled(response, null, variables);
        }

        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('An error occurred');
        setIsError(true);
        setError(error);
        setIsSuccess(false);

        if (onError) {
          onError(error, variables);
        }

        if (onSettled) {
          onSettled(null, error, variables);
        }

        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [endpoint, method, onSuccess, onError, onSettled]
  );

  const mutateAsync = useCallback(
    async (variables: TVariables): Promise<TData> => {
      const result = await mutate(variables);
      if (result === null) {
        throw error || new Error('Mutation failed');
      }
      return result;
    },
    [mutate, error]
  );

  return {
    mutate,
    mutateAsync,
    data,
    isLoading,
    isError,
    error,
    isSuccess,
    reset,
  };
}
