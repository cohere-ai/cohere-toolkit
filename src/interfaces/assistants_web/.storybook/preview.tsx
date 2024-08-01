import type { Preview } from '@storybook/react';
import { ThemeProvider } from 'next-themes';
import React from 'react';

import '../src/styles/main.css';

const preview: Preview = {
  globalTypes: {
    theme: {
      description: 'Global theme for components',
      toolbar: {
        // The label to show for this toolbar item
        title: 'Theme',
        icon: 'circlehollow',
        // Array of plain string values or MenuItem shape (see below)
        items: ['light', 'dark'],
        // Change title based on selected value
        dynamicTitle: true,
      },
    },
  },
  decorators: [
    (Story, context) => (
      <ThemeProvider forcedTheme={context.globals.theme} attribute="class" defaultTheme="dark">
        <div className="h-screen w-screen bg-marble-950 p-4 dark:bg-volcanic-100">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
  parameters: {
    nextjs: {
      appDirectory: true,
      router: {
        basePath: '/',
      },
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: 'fullscreen',
  },
};

export default preview;
