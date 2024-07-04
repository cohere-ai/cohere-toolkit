import { Root } from 'hast';
import type { Plugin } from 'unified';

/**
 * A rehype plugin that logs the tree to the console.
 */
export const rehypeLog: Plugin<void[], Root> = () => {
  return (tree) => {
    // console.log(tree);
  };
};
