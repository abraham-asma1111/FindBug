'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

export interface UseApiMutationOptions<TData, TVariables> {
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
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
  options: UseApiMutationOptions<TData, TVariables> = {}
): UseApiMutationResult<TData, TVariables> {
  const { onSuccess, onError, onSettled, method = 'POST' } = options;

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

        // Extract endpoint from variables if provided
        const { endpoint, ...data } = variables as any;
        
        if (!endpoint) {
          throw new Error('Endpoint is required');
        }

        let response: TData;

        switch (method) {
          case 'POST':
            response = (await api.post<TData>(endpoint, data)).data;
            break;
          case 'PUT':
            response = (await api.put<TData>(endpoint, data)).data;
            break;
          case 'PATCH':
            response = (await api.patch<TData>(endpoint, data)).data;
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
    [method, onSuccess, onError, onSettled]
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
