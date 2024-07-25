'use client';

import { useState } from 'react';
import { Options, useHotkeys } from 'react-hotkeys-hook';

import { HotKeysDialog } from '@/components/Shared/HotKeys/HotKeysDialog';
import { QuickAction } from '@/components/Shared/HotKeys/QuickActions';

/**
 * taken from the type OptionsOrDependencyArray in react-hotkeys-hook
 */
type OptionsOrDependencyArray = Options | ReadonlyArray<unknown>;

export interface CustomHotKey extends QuickAction {
  options?: OptionsOrDependencyArray;
  dependencies?: OptionsOrDependencyArray;
}

type HotKeysProviderProps = {
  customHotKeys?: CustomHotKey[];
};

export const HotKeysProvider: React.FC<HotKeysProviderProps> = ({ customHotKeys = [] }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const open = () => {
    setIsDialogOpen(true);
  };

  const close = () => {
    setIsDialogOpen(false);
  };

  useHotkeys(
    ['ctrl+k', 'meta+k'],
    () => {
      if (isDialogOpen) {
        close();
        return;
      }
      open();
    },
    {
      enableOnFormTags: true,
    },
    [isDialogOpen, close, open]
  );

  customHotKeys.forEach(({ commands, action, options, dependencies }) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    useHotkeys(
      commands,
      () => {
        if (isDialogOpen) {
          close();
        }
        action();
      },
      { enableOnFormTags: true, ...options },
      dependencies
    );
  });

  const dialogCustomActions: QuickAction[] = customHotKeys.map(({ name, commands, action }) => ({
    name,
    commands,
    action,
  }));

  return <HotKeysDialog isOpen={isDialogOpen} close={close} customActions={dialogCustomActions} />;
};
