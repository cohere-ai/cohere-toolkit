import { StateCreator } from 'zustand';

import { Document } from '@/cohere-client';

import { StoreState } from '..';

const INITIAL_STATE: State = {
  citationReferences: {},
  hasCitations: false,
  searchResults: {},
  outputFiles: {},
};

type CitationReferences = {
  [generationId: string]: {
    /** In the format: {startIndex}-{endIndex} */
    [startEndKey: string]: Document[];
  };
};

interface SearchResults {
  [documentId: string]: Record<string, any>;
}

export type OutputFiles = { [name: string]: { name: string; data: string; documentId?: string } };

type State = {
  citationReferences: CitationReferences;
  hasCitations: boolean;
  searchResults: SearchResults;
  outputFiles: OutputFiles;
};

type Actions = {
  addSearchResults: (results: Record<string, any>) => void;
  addCitation: (generationId: string, startEndKey: string, documents: Document[]) => void;
  resetCitations: VoidFunction;
  saveOutputFiles: (outputFiles: OutputFiles) => void;
};

export type CitationsStore = {
  citations: State;
} & Actions;

export const createCitationsSlice: StateCreator<StoreState, [], [], CitationsStore> = (set) => ({
  addSearchResults(results) {
    set((state) => {
      const newResults = { ...state.citations.searchResults };
      (results || []).forEach((result: any) => {
        (result?.documentIds ?? []).forEach((docId: string) => {
          newResults[docId] = result;
        });
      });
      return {
        citations: {
          ...state.citations,
          ...(results ? { searchResults: newResults } : {}),
        },
      };
    });
  },
  addCitation(generationId, startEndKey, documents) {
    set((state) => ({
      citations: {
        ...state.citations,
        citationReferences: {
          ...state.citations.citationReferences,
          [generationId]: {
            ...state.citations.citationReferences[generationId],
            [startEndKey]: documents,
          },
        },
        hasCitations: true,
      },
    }));
  },
  resetCitations() {
    set(() => ({
      citations: INITIAL_STATE,
    }));
  },
  saveOutputFiles(outputFiles) {
    set((state) => ({
      citations: {
        ...state.citations,
        outputFiles,
      },
    }));
  },
  citations: INITIAL_STATE,
});
