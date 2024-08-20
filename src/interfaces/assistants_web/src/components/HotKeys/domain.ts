import { Options } from 'react-hotkeys-hook';

type OptionsOrDependencyArray = Options | ReadonlyArray<unknown>;

export type QuickAction = {
  name: string;
  commands: string[];
  action: () => void;
};

export interface CustomHotKey extends QuickAction {
  options?: OptionsOrDependencyArray;
  dependencies?: OptionsOrDependencyArray;
}

export type HotKeyGroupOption = {
  group: string;
  quickActions: CustomHotKey[];
};
