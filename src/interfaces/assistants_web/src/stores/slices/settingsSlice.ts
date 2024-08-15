import { StateCreator } from 'zustand';

const INITIAL_STATE = {
  disabledAssistantKnowledge: [],
  isLeftPanelOpen: true,
  isRightPanelOpen: false,
};

type State = {
  disabledAssistantKnowledge: string[];
  isLeftPanelOpen: boolean;
  isRightPanelOpen: boolean;
};

type Actions = {
  setUseAssistantKnowledge: (useKnowledge: boolean, agentId: string) => void;
  setLeftPanelOpen: (isOpen: boolean) => void;
  setRightPanelOpen: (isOpen: boolean) => void;
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
  setLeftPanelOpen(isOpen) {
    set((state) => ({
      ...state,
      isLeftPanelOpen: isOpen,
    }));
  },
  setRightPanelOpen(isOpen) {
    set((state) => ({
      ...state,
      isRightPanelOpen: isOpen,
    }));
  },
  ...INITIAL_STATE,
});
