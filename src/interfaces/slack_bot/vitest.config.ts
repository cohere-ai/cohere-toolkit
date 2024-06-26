import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

// Configure Vitest; https://vitest.dev/config/
export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: 'node',
    coverage: {
      all: true,
      include: ['src'],
      reporter: ['html', 'json', 'json-summary', 'text', 'text-summary'],
    },
  },
});
