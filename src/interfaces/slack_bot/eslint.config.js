const eslintPluginPrettierRecommended = require('eslint-plugin-prettier/recommended');

module.exports = [
  {
    ignores: ['coverage'],
  },
  eslintPluginPrettierRecommended,
];
