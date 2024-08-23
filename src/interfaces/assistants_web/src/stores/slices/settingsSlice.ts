import { StateCreator } from 'zustand';

const INITIAL_STATE = {
  isLeftPanelOpen: true,
  isRightPanelOpen: false,
};

type State = {
  isLeftPanelOpen: boolean;
  isRightPanelOpen: boolean;
};

type Actions = {
  setLeftPanelOpen: (isOpen: boolean) => void;
  setRightPanelOpen: (isOpen: boolean) => void;
};

export type SettingsStore = State & Actions;

export const createSettingsSlice: StateCreator<SettingsStore, [], [], SettingsStore> = (set) => ({
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
