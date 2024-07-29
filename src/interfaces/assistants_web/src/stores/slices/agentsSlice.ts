import { StateCreator } from 'zustand';

import { StoreState } from '@/stores';

const INITIAL_STATE = {
  isAgentsLeftPanelOpen: true,
  isAgentsRightPanelOpen: false,
};

type State = {
  isAgentsLeftPanelOpen: boolean;
  isAgentsRightPanelOpen: boolean;
};
type Actions = {
  setAgentsLeftSidePanelOpen: (isOpen: boolean) => void;
  setAgentsRightSidePanelOpen: (isOpen: boolean) => void;
};

export type AgentsStore = {
  agents: State;
} & Actions;

export const createAgentsSlice: StateCreator<StoreState, [], [], AgentsStore> = (set) => ({
  setAgentsLeftSidePanelOpen(isOpen) {
    set((state) => ({
      agents: {
        ...state.agents,
        isAgentsLeftPanelOpen: isOpen,
      },
    }));
  },
  setAgentsRightSidePanelOpen(isOpen) {
    set((state) => ({
      agents: {
        ...state.agents,
        isAgentsRightPanelOpen: isOpen,
      },
    }));
  },
  agents: INITIAL_STATE,
});
