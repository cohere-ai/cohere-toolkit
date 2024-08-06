import { StateCreator } from 'zustand';

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

export type SettingsStore = State & Actions;

export const createSettingsSlice: StateCreator<SettingsStore, [], [], SettingsStore> = (set) => ({
  setUseAssistantKnowledge(useKnowledge, agentId) {
    set((state) => ({
      ...state,
      disabledAssistantKnowledge: useKnowledge
        ? state.disabledAssistantKnowledge.filter((id) => id !== agentId)
        : [...state.disabledAssistantKnowledge, agentId],
    }));
  },
  setAgentsLeftSidePanelOpen(isOpen) {
    set((state) => ({
      ...state,
      isAgentsLeftPanelOpen: isOpen,
    }));
  },
  setAgentsRightSidePanelOpen(isOpen) {
    set((state) => ({
      ...state,
      isAgentsRightPanelOpen: isOpen,
    }));
  },
  ...INITIAL_STATE,
});
