import { StateCreator } from 'zustand';

const INITIAL_STATE = {
  disabledAssistantKnowledge: [],
  isLeftPanelOpen: true,
  isRightPanelOpen: false,
  showSteps: true,
};

type State = {
  disabledAssistantKnowledge: string[];
  isLeftPanelOpen: boolean;
  isRightPanelOpen: boolean;
  showSteps: boolean;
};

type Actions = {
  setUseAssistantKnowledge: (useKnowledge: boolean, agentId: string) => void;
  setLeftPanelOpen: (isOpen: boolean) => void;
  setRightPanelOpen: (isOpen: boolean) => void;
  setShowSteps: (showSteps: boolean) => void;
};

export type SettingsStore = State & Actions;

export const createSettingsSlice: StateCreator<SettingsStore, [], [], SettingsStore> = (set) => ({
  setUseAssistantKnowledge(useKnowledge: boolean, agentId: string) {
    set((state) => ({
      ...state,
      disabledAssistantKnowledge: useKnowledge
        ? state.disabledAssistantKnowledge.filter((id) => id !== agentId)
        : [...state.disabledAssistantKnowledge, agentId],
    }));
  },
  setLeftPanelOpen(isOpen: boolean) {
    set((state) => ({
      ...state,
      isLeftPanelOpen: isOpen,
    }));
  },
  setRightPanelOpen(isOpen: boolean) {
    set((state) => ({
      ...state,
      isRightPanelOpen: isOpen,
    }));
  },
  setShowSteps(showSteps: boolean) {
    set((state) => ({
      ...state,
      showSteps: showSteps,
    }));
  },
  ...INITIAL_STATE,
});
