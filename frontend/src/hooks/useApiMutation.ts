'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

export interface UseApiMutationOptions<TData, TVariables> {
  endpoint?: string;
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
  arg1?: string | UseApiMutationOptions<TData, TVariables>,
  arg2?: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  arg3?: UseApiMutationOptions<TData, TVariables>
): UseApiMutationResult<TData, TVariables> {
  let configuredEndpoint: string | undefined;
  let method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST';
  let options: UseApiMutationOptions<TData, TVariables> = {};

  if (typeof arg1 === 'string') {
    configuredEndpoint = arg1;
    if (arg2) method = arg2;
    if (arg3) options = arg3;
  } else if (arg1) {
    options = arg1;
    configuredEndpoint = options.endpoint;
    if (options.method) method = options.method;
  }

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

        // Extract endpoint from variables if provided
        let payloadData = variables;
        let mutationEndpoint = configuredEndpoint;

        if (variables && typeof variables === 'object' && 'endpoint' in variables) {
          const { endpoint, ...rest } = variables as any;
          if (endpoint) mutationEndpoint = endpoint;
          payloadData = rest as any;
        }
        
        if (!mutationEndpoint) {
          throw new Error('Endpoint is required');
        }

        let response: TData;

        switch (method) {
          case 'POST':
            response = (await api.post<TData>(mutationEndpoint, payloadData)).data;
            break;
          case 'PUT':
            response = (await api.put<TData>(mutationEndpoint, payloadData)).data;
            break;
          case 'PATCH':
            response = (await api.patch<TData>(mutationEndpoint, payloadData)).data;
            break;
          case 'DELETE':
            response = (await api.delete<TData>(mutationEndpoint)).data;
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
