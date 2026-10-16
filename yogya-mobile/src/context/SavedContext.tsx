/**
 * SavedContext — Yogya
 *
 * Provides reactive bookmark / saved opportunities state across the app.
 * Automatically synchronizes with storageService so bookmarked items persist across
 * Home, Explore, Saved, and Opportunity Details screens.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { getOpportunityById } from '@/data/mock';
import { opportunityService } from '@/services/opportunities';
import { storageService } from '@/services/storage';
import type { Opportunity } from '@/types';

interface SavedContextType {
  savedIds: string[];
  savedOpportunities: Opportunity[];
  isSaved: (id: string) => boolean;
  toggleSave: (id: string) => Promise<boolean>;
  clearSaved: () => Promise<void>;
  isLoading: boolean;
}

const SavedContext = createContext<SavedContextType | undefined>(undefined);

export function SavedProvider({ children }: { children: React.ReactNode }) {
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadSaved() {
      try {
        const ids = await storageService.getSavedOpportunityIds();
        if (isMounted) {
          setSavedIds(ids || []);
        }
      } catch {
        console.warn('SavedContext: Failed to load saved opportunity IDs from storage.');
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadSaved();

    return () => {
      isMounted = false;
    };
  }, []);

  const isSaved = useCallback(
    (id: string): boolean => {
      if (!id) return false;
      const normalized = id.toLowerCase();
      return savedIds.some((savedId) => {
        const s = savedId.toLowerCase();
        return (
          s === normalized ||
          s === `demo-${normalized}` ||
          `demo-${s}` === normalized
        );
      });
    },
    [savedIds],
  );

  const toggleSave = useCallback(
    async (id: string): Promise<boolean> => {
      if (!id) return false;
      const normalized = id.toLowerCase();
      let willBeSaved = false;
      let nextList: string[] = [];

      setSavedIds((prev) => {
        const exists = prev.some((savedId) => {
          const s = savedId.toLowerCase();
          return (
            s === normalized ||
            s === `demo-${normalized}` ||
            `demo-${s}` === normalized
          );
        });

        willBeSaved = !exists;
        if (exists) {
          nextList = prev.filter((savedId) => {
            const s = savedId.toLowerCase();
            return !(
              s === normalized ||
              s === `demo-${normalized}` ||
              `demo-${s}` === normalized
            );
          });
        } else {
          nextList = [...prev, id];
        }
        return nextList;
      });

      try {
        await storageService.saveSavedOpportunityIds(nextList);
      } catch {
        console.warn('SavedContext: Failed to persist bookmark updates to storage.');
      }

      return willBeSaved;
    },
    [],
  );

  const clearSaved = useCallback(async () => {
    setSavedIds([]);
    try {
      await storageService.clearSavedOpportunityIds();
    } catch {
      console.warn('SavedContext: Failed to clear saved bookmarks from storage.');
    }
  }, []);

  const savedOpportunities = useMemo(() => {
    return savedIds
      .map((id) => opportunityService.getCachedOpportunity(id) || getOpportunityById(id))
      .filter((opp): opp is Opportunity => opp !== undefined);
  }, [savedIds]);

  const value: SavedContextType = {
    savedIds,
    savedOpportunities,
    isSaved,
    toggleSave,
    clearSaved,
    isLoading,
  };

  return (
    <SavedContext.Provider value={value}>{children}</SavedContext.Provider>
  );
}

export function useSavedOpportunities(): SavedContextType {
  const context = useContext(SavedContext);
  if (!context) {
    throw new Error(
      'useSavedOpportunities must be used within a SavedProvider',
    );
  }
  return context;
}
