'use client';

import { HotKeyGroupOption } from '@/components/HotKeys/domain';
import { useSettingsStore } from '@/stores';

export const useViewHotKeys = (): HotKeyGroupOption[] => {
  const { isLeftPanelOpen, setLeftPanelOpen } = useSettingsStore();
  return [
    {
      group: 'View',
      quickActions: [
        {
          name: 'Show or hide left sidebar',
          commands: ['ctrl+shift+s', 'meta+shift+s'],
          closeDialogOnRun: true,
          registerGlobal: true,
          action: () => {
            setLeftPanelOpen(!isLeftPanelOpen);
          },
          options: {
            preventDefault: true,
          },
        },
      ],
    },
  ];
};
