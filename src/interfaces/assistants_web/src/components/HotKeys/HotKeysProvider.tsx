'use client';

import { useHotkeys } from 'react-hotkeys-hook';

import { CustomHotKey, type HotKeyGroupOption, HotKeysDialog } from '@/components/HotKeys';
import { useSettingsStore } from '@/stores';

type HotKeysProviderProps = {
  hotKeys: HotKeyGroupOption[];
};

export const HotKeysProvider: React.FC<HotKeysProviderProps> = ({ hotKeys = [] }) => {
  const { isHotKeysDialogOpen, setIsHotKeysDialogOpen } = useSettingsStore();

  const open = () => {
    setIsHotKeysDialogOpen(true);
  };

  const close = () => {
    setIsHotKeysDialogOpen(false);
  };

  useHotkeys(
    ['ctrl+k', 'meta+k'],
    () => {
      if (isHotKeysDialogOpen) {
        close();
        return;
      }
      open();
    },
    {
      enableOnFormTags: true,
    },
    [isHotKeysDialogOpen, close, open]
  );

  return (
    <>
      <HotKeysDialog isOpen={isHotKeysDialogOpen} close={close} options={hotKeys} />
      {hotKeys
        .map((hk) => hk.quickActions)
        .flat()
        .filter((hk) => hk.registerGlobal)
        .map((hk) => (
          <HotKeyRegisterAction
            key={hk.name}
            hotKey={hk}
            isDialogOpen={isHotKeysDialogOpen}
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
      hotKey.action?.();
    },
    { enableOnFormTags: true, ...hotKey.options },
    hotKey.dependencies
  );

  return null;
};
