import { StateCreator } from 'zustand';

const INITIAL_STATE = {
  recentAgentsIds: [],
  isEditAgentPanelOpen: false,
  isAgentsSidePanelOpen: true,
};

type State = {
  recentAgentsIds: string[];
  isAgentsSidePanelOpen: boolean;
  isEditAgentPanelOpen: boolean;
};
type Actions = {
  setAgentsSidePanelOpen: (isOpen: boolean) => void;
  setEditAgentPanelOpen: (isOpen: boolean) => void;
  addRecentAgentId: (agentId: string) => void;
  removeRecentAgentId: (agentId: string) => void;
};

export type AgentsStore = {
  agents: State;
} & Actions;

export const createAgentsSlice: StateCreator<AgentsStore, [], [], AgentsStore> = (set) => ({
  addRecentAgentId(agentId) {
    set((state) => ({
      agents: {
        ...state.agents,
        recentAgentsIds: [
          ...state.agents.recentAgentsIds,
          ...(state.agents.recentAgentsIds.includes(agentId) ? [] : [agentId]),
        ],
      },
    }));
  },
  removeRecentAgentId(agentId) {
    set((state) => ({
      agents: {
        ...state.agents,
        recentAgentsIds: state.agents.recentAgentsIds.filter((id) => id !== agentId),
      },
    }));
  },
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
