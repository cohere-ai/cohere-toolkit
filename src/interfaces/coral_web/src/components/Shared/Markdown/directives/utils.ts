import { Root } from 'hast';
import type { Plugin } from 'unified';
import { visit } from 'unist-util-visit';

/**
 * A remark plugin that removes extra blank spaces from the text.
 */
export const removeExtraBlankSpaces: Plugin<void[], Root> = () => {
  return (tree) => {
    visit(tree, 'text', (node) => {
      node.value = node.value.replace(/\n{2,}/g, '\n');
    });
  };
};
