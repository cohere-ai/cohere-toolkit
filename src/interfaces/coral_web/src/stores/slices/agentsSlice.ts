import { StateCreator } from 'zustand';

const INITIAL_STATE = {
  recentAgentsIds: [],
};

type State = {
  recentAgentsIds: string[];
};
type Actions = {
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
  agents: INITIAL_STATE,
});
