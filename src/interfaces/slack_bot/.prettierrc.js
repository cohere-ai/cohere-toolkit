// https://prettier.io/docs/en/options.html

module.exports = {
  printWidth: 100,
  singleQuote: true,
  importOrder: ['<THIRD_PARTY_MODULES>', '^@/*/(.*)$', '^[./]', '(.*)\\.css$'],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
  plugins: [require.resolve('@trivago/prettier-plugin-sort-imports')],
};
