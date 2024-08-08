module.exports = {
  extends: [
    'eslint-config-next/core-web-vitals',
    'eslint-config-prettier',
    'plugin:storybook/recommended',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-process-env': 'error',
  },
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
};
