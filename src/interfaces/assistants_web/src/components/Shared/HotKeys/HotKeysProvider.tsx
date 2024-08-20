'use client';

import { useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

import { HotKeysDialog } from '@/components/Shared/HotKeys/HotKeysDialog';
import { CustomHotKey, type HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';

type HotKeysProviderProps = {
  hotKeys: HotKeyGroupOption[];
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

  return (
    <>
      <HotKeysDialog isOpen={isDialogOpen} close={close} options={hotKeys} />
      {hotKeys
        .map((hk) => hk.quickActions)
        .flat()
        .map((hk) => (
          <HotKeyRegisterAction
            key={hk.name}
            hotKey={hk}
            isDialogOpen={isDialogOpen}
            close={close}
          />
        ))}
    </>
  );
};

type Props = {
  hotKey: CustomHotKey;
  isDialogOpen: boolean;
  close: VoidFunction;
};

const HotKeyRegisterAction: React.FC<Props> = ({ hotKey, isDialogOpen, close }) => {
  useHotkeys(
    hotKey.commands,
    () => {
      if (isDialogOpen) {
        close();
      }
      hotKey.action();
    },
    { enableOnFormTags: true, ...hotKey.options },
    hotKey.dependencies
  );

  return null;
};
