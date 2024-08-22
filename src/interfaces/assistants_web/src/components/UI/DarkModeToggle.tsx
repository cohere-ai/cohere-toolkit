import { useTheme } from 'next-themes';

import { Icon, Text } from '@/components/UI';
import { cn } from '@/utils';

export const DarkModeToggle = () => {
  const { setTheme, theme } = useTheme();

  const handleSetTheme = (theme: string) => {
    if (document.startViewTransition) {
      document.startViewTransition(() => setTheme(theme));
    } else {
      setTheme(theme);
    }
  };

  return (
    <section className="flex gap-6">
      <div className="flex flex-col gap-2">
        <button
          className={cn('grid h-24 w-[144px] place-items-center rounded-lg bg-volcanic-200', {
            'border border-evolved-green-700': theme === 'dark',
          })}
          onClick={() => handleSetTheme('dark')}
        >
          <Icon name="moon" className="fill-mushroom-950" kind="outline" size="lg" />
        </button>
        <Text className="text-center">Dark</Text>
      </div>
      <div className="flex flex-col gap-2">
        <button
          className={cn('grid h-24 w-[144px] place-items-center rounded-lg bg-mushroom-950', {
            'border border-coral-700': theme === 'light',
          })}
          onClick={() => handleSetTheme('light')}
        >
          <Icon
            name="sun"
            className="fill-volcanic-150 dark:fill-volcanic-150"
            kind="outline"
            size="lg"
          />
        </button>
        <Text className="text-center">Light</Text>
      </div>
      <div className="flex flex-col gap-2">
        <button
          className={cn('flex h-24 w-[144px] rounded-lg', {
            'border border-coral-700 dark:border-evolved-green-700': theme === 'system',
          })}
          onClick={() => handleSetTheme('system')}
        >
          <div className="grid h-full w-1/2 place-items-center rounded-l-lg bg-volcanic-200">
            <Icon name="moon" className="fill-mushroom-950" kind="outline" size="lg" />
          </div>
          <div className="grid h-full w-1/2 place-items-center rounded-r-lg bg-mushroom-950">
            <Icon
              name="sun"
              className="fill-volcanic-150 dark:fill-volcanic-150"
              kind="outline"
              size="lg"
            />
          </div>
        </button>
        <Text className="text-center">System</Text>
      </div>
    </section>
  );
};
