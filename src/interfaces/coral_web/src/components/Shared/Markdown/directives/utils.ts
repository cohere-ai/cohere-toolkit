import { Root } from 'hast';
import type { Plugin } from 'unified';

/**
 * A rehype plugin that removes extra blank spaces between tables.
 */
export const removeExtraBlankSpaces: Plugin<void[], Root> = () => {
  return (tree) => {
    for (let i = 0; i < tree.children.length; i++) {
      const node = tree.children[i];
      if (node.type == 'element' && node.tagName == 'table' && i > 0) {
        const prevNode = tree.children[i - 1];
        if (prevNode.type == 'text') {
          prevNode.value = prevNode.value.replace(/\n{2,}/g, '\n');
        }
      }
    }
  };
};
