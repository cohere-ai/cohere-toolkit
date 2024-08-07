import { StateCreator } from 'zustand';

import { StoreState } from '@/stores';

const INITIAL_STATE = {
  disabledAssistantKnowledge: [],
  isAgentsLeftPanelOpen: true,
  isAgentsRightPanelOpen: false,
};

type State = {
  disabledAssistantKnowledge: string[];
  isAgentsLeftPanelOpen: boolean;
  isAgentsRightPanelOpen: boolean;
};
type Actions = {
  setUseAssistantKnowledge: (useKnowledge: boolean, agentId: string) => void;
  setAgentsLeftSidePanelOpen: (isOpen: boolean) => void;
  setAgentsRightSidePanelOpen: (isOpen: boolean) => void;
};

export type AgentsStore = {
  agents: State;
} & Actions;

export const createAgentsSlice: StateCreator<StoreState, [], [], AgentsStore> = (set) => ({
  setUseAssistantKnowledge(useKnowledge, agentId) {
    set((state) => ({
      agents: {
        ...state.agents,
        disabledAssistantKnowledge: useKnowledge
          ? state.agents.disabledAssistantKnowledge.filter((id) => id !== agentId)
          : [...state.agents.disabledAssistantKnowledge, agentId],
      },
    }));
  },
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
