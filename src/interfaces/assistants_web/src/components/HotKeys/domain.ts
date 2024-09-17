import { Options } from 'react-hotkeys-hook';

type OptionsOrDependencyArray = Options | ReadonlyArray<unknown>;

export type QuickAction = {
  name: string;
  label?: React.ReactNode;
  commands: string[];
  registerGlobal: boolean;
  closeDialogOnRun: boolean;
  displayInDialog?: boolean;
  action?: () => void;
  customView?: React.FC<{
    isOpen: boolean;
    close: VoidFunction;
    onBack: VoidFunction;
  }>;
};

export interface CustomHotKey extends QuickAction {
  options?: OptionsOrDependencyArray;
  dependencies?: OptionsOrDependencyArray;
}

export type HotKeyGroupOption = {
  group?: string;
  quickActions: CustomHotKey[];
};
