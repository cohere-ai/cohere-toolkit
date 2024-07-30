import { useState } from 'react';

import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

import './style.css';

export const DarkModeToggle = () => {
  const [isDarkMode, _setIsDarkMode] = useState(() =>
    Boolean(document.querySelector('html')?.classList.contains('dark'))
  );

  const setIsDarkMode = (darkMode: boolean) => {
    _setIsDarkMode(darkMode);
    if (document.startViewTransition) {
      document.startViewTransition(() => handleToggle(darkMode));
    } else {
      handleToggle(darkMode);
    }
  };

  const handleToggle = (darkMode: boolean) => {
    const html = document.querySelector('html');
    if (darkMode) {
      html?.classList.add('dark');
    } else {
      html?.classList.remove('dark');
    }
  };

  return (
    <section className="flex gap-6">
      <div className="flex flex-col gap-2">
        <button
          className={cn('grid h-24 w-28 place-items-center rounded-lg bg-volcanic-200', {
            'border border-evolved-green-700': isDarkMode,
          })}
          onClick={() => setIsDarkMode(true)}
        >
          <Icon name="moon" className="fill-mushroom-950" kind="outline" size="lg" />
        </button>
        <Text className="text-center">Dark</Text>
      </div>
      <div className="flex flex-col gap-2">
        <button
          className={cn('grid h-24 w-28 place-items-center rounded-lg bg-mushroom-950', {
            'border border-evolved-green-700': !isDarkMode,
          })}
          onClick={() => setIsDarkMode(false)}
        >
          <Icon name="sun" className="fill-volcanic-150" kind="outline" size="lg" />
        </button>
        <Text className="text-center">Light</Text>
      </div>
    </section>
  );
};
