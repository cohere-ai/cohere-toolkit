import { useState } from 'react';

import { Switch } from '@/components/Shared';

import './style.css';

export const DarkModeToggle = () => {
  const [isDarkMode, setIsDarkMode] = useState(() =>
    Boolean(document.querySelector('html')?.classList.contains('dark'))
  );
  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        document.querySelector('html')?.classList.toggle('dark');
      });
    } else {
      document.querySelector('html')?.classList.toggle('dark');
    }
  };
  return (
    <Switch
      label="Dark mode"
      checked={isDarkMode}
      theme="evolved-green"
      onChange={toggleDarkMode}
    />
  );
};
