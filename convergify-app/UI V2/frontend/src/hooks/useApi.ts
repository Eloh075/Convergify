import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T, P extends any[]> extends UseApiState<T> {
  execute: (...args: P) => Promise<T | null>;
  reset: () => void;
}

/**
 * Custom hook for API calls with loading and error states
 * Similar to MP3's useApi pattern
 */
export function useApi<T, P extends any[]>(
  apiFunction: (...args: P) => Promise<T>
): UseApiReturn<T, P> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: P): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await apiFunction(...args);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (err) {
        const error = err as AxiosError<{ error: string }>;
        const errorMessage =
          error.response?.data?.error ||
          error.message ||
          'An unexpected error occurred';
        
        setState({ data: null, loading: false, error: errorMessage });
        console.error('API Error:', errorMessage, error);
        return null;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Hook for polling analysis status
 */
export function useAnalysisPolling(
  getStatus: (id: string) => Promise<any>,
  interval = 2000
) {
  const [status, setStatus] = useState<'idle' | 'polling' | 'completed' | 'failed'>('idle');
  const [progress, setProgress] = useState<{ step: string; percentage: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startPolling = useCallback(
    async (analysisId: string): Promise<void> => {
      setStatus('polling');
      setError(null);

      return new Promise((resolve, reject) => {
        const poll = async () => {
          try {
            const result = await getStatus(analysisId);

            if (result.status === 'completed') {
              setStatus('completed');
              setProgress(null);
              resolve();
              return;
            }

            if (result.status === 'failed') {
              setStatus('failed');
              setError(result.error_message || 'Analysis failed');
              reject(new Error(result.error_message || 'Analysis failed'));
              return;
            }

            // Still processing
            if (result.progress) {
              setProgress(result.progress);
            }

            // Continue polling
            setTimeout(poll, interval);
          } catch (err) {
            const error = err as AxiosError<{ error: string }>;
            const errorMessage =
              error.response?.data?.error ||
              error.message ||
              'Failed to check analysis status';
            
            setStatus('failed');
            setError(errorMessage);
            reject(new Error(errorMessage));
          }
        };

        poll();
      });
    },
    [getStatus, interval]
  );

  const reset = useCallback(() => {
    setStatus('idle');
    setProgress(null);
    setError(null);
  }, []);

  return {
    status,
    progress,
    error,
    startPolling,
    reset,
  };
}
