'use client';

import { Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';

type NavigationKey = {
  keys: string[];
  description: string;
};

const navigationKeys: NavigationKey[] = [
  {
    keys: ['&crarr;'],
    description: STRINGS.toSelect,
  },
  {
    keys: ['&uarr;', '&darr;'],
    description: STRINGS.toMoveUpDown,
  },
  {
    keys: ['esc'],
    description: STRINGS.toClose,
  },
  {
    keys: ['?'],
    description: STRINGS.toViewAllOptions,
  },
];

const DialogNavigationKeys = () => {
  return (
    <Text
      className="flex flex-col items-start gap-5 bg-marble-950 px-3 py-2 md:flex-row md:items-center"
      as="div"
      styleAs="caption"
    >
      {navigationKeys.map((navKey, i) => (
        <span key={i} className="flex items-center">
          {navKey.keys.map((key) => (
            <kbd
              key={key}
              className="mr-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded border bg-white px-1 font-semibold"
              dangerouslySetInnerHTML={{ __html: key }}
            />
          ))}
          <span>{navKey.description}</span>
        </span>
      ))}
    </Text>
  );
};

export default DialogNavigationKeys;
