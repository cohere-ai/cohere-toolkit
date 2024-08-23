'use client';

import { useTheme } from 'next-themes';

import { HotKeyGroupOption } from '@/components/HotKeys/domain';

export const useSettingsHotKeys = (): HotKeyGroupOption[] => {
  const { theme, setTheme } = useTheme();

  return [
    {
      group: 'Settings',
      quickActions: [
        {
          name: 'Set theme to Light',
          label: (
            <span className="flex gap-x-2">
              Set theme to Light
              {theme === 'light' && (
                <span className="ml-2 rounded bg-mushroom-800 px-2 py-1 font-mono text-p-xs uppercase text-volcanic-300 dark:bg-volcanic-400 dark:text-marble-900">
                  Current
                </span>
              )}
            </span>
          ),
          closeDialogOnRun: false,
          commands: [],
          registerGlobal: false,
          action: () => {
            if (theme === 'light') return;
            if (document.startViewTransition) {
              document.startViewTransition(() => setTheme('light'));
            } else {
              setTheme('light');
            }
          },
        },
        {
          name: 'Set theme to Dark',
          label: (
            <span className="flex gap-x-2">
              Set theme to Dark
              {theme === 'dark' && (
                <span className="ml-2 rounded bg-mushroom-800 px-2 py-1 font-mono text-p-xs uppercase text-volcanic-300 dark:bg-volcanic-400 dark:text-marble-900">
                  Current
                </span>
              )}
            </span>
          ),
          closeDialogOnRun: false,
          commands: [],
          registerGlobal: false,
          action: () => {
            if (theme === 'dark') return;
            if (document.startViewTransition) {
              document.startViewTransition(() => setTheme('dark'));
            } else {
              setTheme('dark');
            }
          },
        },
        {
          name: 'Set theme to System',
          label: (
            <span className="flex gap-x-2">
              Set theme to System
              {theme === 'system' && (
                <span className="ml-2 rounded bg-mushroom-800 px-2 py-1 font-mono text-p-xs uppercase text-volcanic-300 dark:bg-volcanic-400 dark:text-marble-900">
                  Current
                </span>
              )}
            </span>
          ),
          commands: [],
          closeDialogOnRun: false,
          registerGlobal: false,
          action: () => {
            if (theme === 'system') return;
            if (document.startViewTransition) {
              document.startViewTransition(() => setTheme('system'));
            } else {
              setTheme('system');
            }
          },
        },
      ],
    },
  ];
};
