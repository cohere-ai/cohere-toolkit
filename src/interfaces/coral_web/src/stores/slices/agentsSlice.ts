import { StateCreator } from 'zustand';

import { StoreState } from '@/stores';

const INITIAL_STATE = {
  isEditAgentPanelOpen: false,
  isAgentsSidePanelOpen: true,
};

type State = {
  isAgentsSidePanelOpen: boolean;
  isEditAgentPanelOpen: boolean;
};
type Actions = {
  setAgentsSidePanelOpen: (isOpen: boolean) => void;
  setEditAgentPanelOpen: (isOpen: boolean) => void;
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
  setEditAgentPanelOpen(isOpen) {
    set((state) => ({
      agents: {
        ...state.agents,
        isEditAgentPanelOpen: isOpen,
      },
    }));
  },
  agents: INITIAL_STATE,
});
