import { StateCreator } from 'zustand';

const INITIAL_STATE: Required<State> = {
  isAgentsSidePanelOpen: true,
  isConfigDrawerOpen: false,
  activeConfigDrawerTab: '',
  isConvListPanelOpen: true,
  isMobileConvListPanelOpen: false,
  isEditAgentPanelOpen: false,
};

type State = {
  isAgentsSidePanelOpen: boolean;
  isConfigDrawerOpen: boolean;
  activeConfigDrawerTab: string;
  isConvListPanelOpen: boolean;
  isMobileConvListPanelOpen: boolean;
  isEditAgentPanelOpen: boolean;
};

type Actions = {
  setSettings: (settings: Partial<State>) => void;
  setIsConvListPanelOpen: (isOpen: boolean) => void;
  setIsAgentsSidePanelOpen: (isOpen: boolean) => void;
};

export type SettingsStore = {
  settings: State;
} & Actions;

export const createSettingsSlice: StateCreator<SettingsStore, [], [], SettingsStore> = (set) => ({
  setSettings(settings) {
    set((state) => ({
      settings: {
        ...state.settings,
        ...settings,
      },
    }));
  },
  setIsAgentsSidePanelOpen(isOpen) {
    set((state) => ({
      settings: {
        ...state.settings,
        isAgentsSidePanelOpen: isOpen,
      },
    }));
  },
  setIsConvListPanelOpen(isOpen) {
    set((state) => ({
      settings: {
        ...state.settings,
        isConvListPanelOpen: isOpen,
        isMobileConvListPanelOpen: isOpen,
      },
    }));
  },
  settings: INITIAL_STATE,
});
