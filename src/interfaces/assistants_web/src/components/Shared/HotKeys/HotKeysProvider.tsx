'use client';

import { useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

import { HotKeysDialog } from '@/components/Shared/HotKeys/HotKeysDialog';
import { type HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';

type HotKeysProviderProps = {
  hotKeys?: HotKeyGroupOption[];
};

export const HotKeysProvider: React.FC<HotKeysProviderProps> = ({ hotKeys = [] }) => {
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

  hotKeys
    .map((hk) => hk.quickActions)
    .flat()
    .forEach(({ commands, action, options, dependencies }) => {
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

  return <HotKeysDialog isOpen={isDialogOpen} close={close} options={hotKeys} />;
};
