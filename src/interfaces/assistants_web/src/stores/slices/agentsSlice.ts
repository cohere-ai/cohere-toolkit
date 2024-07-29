import { StateCreator } from 'zustand';

import { StoreState } from '@/stores';

const INITIAL_STATE = {
  isAgentsSidePanelOpen: true,
};

type State = {
  isAgentsSidePanelOpen: boolean;
};
type Actions = {
  setAgentsSidePanelOpen: (isOpen: boolean) => void;
};

export type AgentsStore = {
  agents: State;
} & Actions;

export const createAgentsSlice: StateCreator<StoreState, [], [], AgentsStore> = (set) => ({
  setAgentsSidePanelOpen(isOpen) {
    set((state) => ({
      agents: {
        ...state.agents,
        isAgentsSidePanelOpen: isOpen,
      },
    }));
  },

  agents: INITIAL_STATE,
});
