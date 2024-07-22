import type { Root } from 'mdast';
import type { Plugin } from 'unified';
import { visit } from 'unist-util-visit';

/**
 * A remark plugin to render `:mark` directives in the context of connector tags.
 * to use in mdx:
 * ```md
 * :mark[text]{connectorId="connector-id"}
 * ```
 **/

export const renderRemarkTags: Plugin<void[], Root> = () => {
  return (tree) => {
    visit(tree, (node: any) => {
      if (node.name !== 'mark') return;

      const data = node.data || (node.data = {});
      const attributes = node.attributes || {};
      const { connectorId } = attributes;
      if (!connectorId) return;
      data.hName = 'mark';
      data.hProperties = {
        connectorId,
      };
    });
  };
};
