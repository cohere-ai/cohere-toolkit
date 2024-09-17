'use client';

import { Search } from '@/components/HotKeys/custom-views/Search';
import { HotKeyGroupOption } from '@/components/HotKeys/domain';

export const useSearchHotKeys = (): HotKeyGroupOption[] => {
  return [
    {
      quickActions: [
        {
          name: 'Search',
          commands: ['$', 'query'],
          closeDialogOnRun: false,
          registerGlobal: false,
          customView: ({ isOpen, close, onBack }) => (
            <Search isOpen={isOpen} close={close} onBack={onBack} />
          ),
        },
      ],
    },
  ];
};
