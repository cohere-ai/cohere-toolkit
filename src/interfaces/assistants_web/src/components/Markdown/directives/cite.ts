import type { Root } from 'mdast';
import type { Plugin } from 'unified';
import { visit } from 'unist-util-visit';

/**
 * A remark plugin to render `:cite` directives as `<cite>` elements.
 * it will add a `docs` attribute to the cite element with the value of the `docs` attribute of the directive.
 * to use in mdx:
 * ```md
 * :cite[text]{docs="https://example.com"}
 * ```
 * this will result in:
 * ```html
 * <cite docs="https://example.com">text</cite>
 * ```
 **/

export const renderRemarkCites: Plugin<void[], Root> = () => {
  return (tree, file) => {
    visit(tree, (node: any) => {
      if (
        node.type === 'textDirective' ||
        node.type === 'leafDirective' ||
        node.type === 'containerDirective'
      ) {
        if (node.name !== 'cite') return;

        const data = node.data || (node.data = {});
        const attributes = node.attributes || {};
        const { generationId, start, end, isCodeSnippet } = attributes;

        if (!generationId) file.fail('Missing generationId', node);
        if (!start) file.fail('Missing start', node);
        if (!end) file.fail('Missing end', node);

        // Decode the citationText child in case there are any weird characters or unclosed brackets that will
        // interfere with parsing the markdown. We should only have one child since we manually feed in this citation text.
        // Note: down the line this may interfere with some markdown styling but this is a safer alternative.
        node.children = (node.children ?? []).map((c: any) => ({
          ...c,
          value: decodeURIComponent(c.value),
        }));

        data.hName = 'cite';
        data.hProperties = {
          generationId,
          start,
          end,
          isCodeSnippet,
        };
      }
    });
  };
};
