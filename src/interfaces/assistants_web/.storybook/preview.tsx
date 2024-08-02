import type { Preview } from '@storybook/react';
import { ThemeProvider } from 'next-themes';
import React from 'react';

import '../src/styles/main.css';

const preview: Preview = {
  decorators: [
    (Story) => (
      <div className="grid h-screen w-screen grid-cols-2">
        <main className="dark bg-volcanic-100 p-3">
          <Story />
        </main>
        <main className="bg-marble-950 p-3">
          <Story />
        </main>
      </div>
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
