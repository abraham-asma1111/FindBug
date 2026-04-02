'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import type { LoaderKey, ResearcherEngagementsState } from './researcherEngagementTypes';
import { mergePTaaSOpportunities } from './researcherEngagementOperationalTransformers';
import {
  createLoaderResponseStrategies,
  type PTaaSAccumulator,
} from './researcherEngagementLoaderStrategies';

export type {
  CodeReviewAssignment,
  EngagementProgram,
  LiveEventAssignment,
  MatchingInvitation,
  ProgramInvitation,
  ProgramParticipation,
  PTaaSOpportunity,
} from './researcherEngagementTypes';

interface UseResearcherEngagementsDataResult extends ResearcherEngagementsState {
  error: string;
  isLoading: boolean;
  refreshData: () => void;
}

type LoaderEntry = {
  key: LoaderKey;
  request: Promise<any>;
};

function createInitialResearcherEngagementsState(): ResearcherEngagementsState {
  return {
    recommendedPrograms: [],
    publicPrograms: [],
    matchedPrograms: [],
    programInvitations: [],
    participations: [],
    matchingInvitations: [],
    liveEvents: [],
    codeReviewAssignments: [],
    ptaasOpportunities: [],
    warnings: [],
  };
}

function buildCriticalLoaders(signal: AbortSignal): LoaderEntry[] {
  return [
    { key: 'publicPrograms', request: api.get('/programs', { params: { limit: 18 }, signal }) },
    { key: 'programInvitations', request: api.get('/programs/invitations/my-invitations', { signal }) },
    { key: 'participations', request: api.get('/programs/programs/my-participations', { signal }) },
    { key: 'matchingInvitations', request: api.get('/matching/invitations', { signal }) },
  ];
}

function buildSecondaryLoaders(signal: AbortSignal): LoaderEntry[] {
  return [
    { key: 'recommendedPrograms', request: api.get('/recommendations/programs', { params: { limit: 6 }, signal }) },
    { key: 'matchedPrograms', request: api.get('/matching/recommendations/bug-bounty', { params: { limit: 6 }, signal }) },
    { key: 'ptaasMatching', request: api.get('/matching/recommendations/ptaas', { params: { limit: 6 }, signal }) },
    {
      key: 'ptaasResearcher',
      request: api.get('/matching/researcher/ptaas-recommendations', { params: { limit: 6 }, signal }),
    },
    { key: 'liveEvents', request: api.get('/live-events/researcher/my-events', { signal }) },
    { key: 'codeReview', request: api.get('/code-review/engagements', { signal }) },
  ];
}

function createPTaaSAccumulator(): PTaaSAccumulator {
  return {
    matching: [],
    researcher: [],
  };
}

function finalizeLoaderState(nextState: ResearcherEngagementsState, ptaasAccumulator: PTaaSAccumulator) {
  nextState.ptaasOpportunities = mergePTaaSOpportunities([
    ...ptaasAccumulator.matching,
    ...ptaasAccumulator.researcher,
  ]);
}

async function runBoundedLoaders(
  loaders: LoaderEntry[],
  onSuccess: (loaderKey: LoaderKey, responseData: any) => void,
  onFailure: (loaderKey: LoaderKey) => void,
  signal: AbortSignal,
  maxConcurrency = 4
) {
  let index = 0;

  async function runLoaderWorker(): Promise<void> {
    while (index < loaders.length && !signal.aborted) {
      const loader = loaders[index];
      index += 1;

      try {
        const response = await loader.request;
        if (signal.aborted) {
          return;
        }
        onSuccess(loader.key, response.data);
      } catch {
        if (signal.aborted) {
          return;
        }
        onFailure(loader.key);
      }
    }
  }

  const workerCount = Math.max(1, Math.min(maxConcurrency, loaders.length));
  await Promise.all(Array.from({ length: workerCount }, () => runLoaderWorker()));
}

export function useResearcherEngagementsData(): UseResearcherEngagementsDataResult {
  const [state, setState] = useState<ResearcherEngagementsState>(createInitialResearcherEngagementsState());
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const abortController = new AbortController();

    const loadData = async () => {
      try {
        setIsLoading(true);

        const nextState: ResearcherEngagementsState = {
          ...state,
          warnings: [],
        };
        const ptaasAccumulator = createPTaaSAccumulator();
        const loaderHandlers = createLoaderResponseStrategies(nextState, ptaasAccumulator);

        await runBoundedLoaders(
          [...buildCriticalLoaders(abortController.signal), ...buildSecondaryLoaders(abortController.signal)],
          (loaderKey, responseData) => loaderHandlers[loaderKey](responseData),
          (loaderKey) => {
            nextState.warnings.push(loaderKey);
          },
          abortController.signal,
          4
        );
        finalizeLoaderState(nextState, ptaasAccumulator);

        if (cancelled) {
          return;
        }

        setState(nextState);
        setError('');
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load researcher engagements.');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      cancelled = true;
      abortController.abort();
    };
  }, [refreshKey]);

  return {
    ...state,
    error,
    isLoading,
    refreshData: () => setRefreshKey((current) => current + 1),
  };
}
