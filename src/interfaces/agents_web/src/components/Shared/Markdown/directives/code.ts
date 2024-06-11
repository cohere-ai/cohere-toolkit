import type { Paragraph, Root } from 'mdast';
import type { Plugin } from 'unified';
import { visit } from 'unist-util-visit';

const CITE_REGEX = /:cite\[([^]*?)\]{generationId="(.*?)" start="(.*?)" end="(.*?)"}/g;

const COMMA_NODE = {
  type: 'text',
  value: ', ',
};

/**
 * A remark plugin to render to find `:cite` directives in code and inlineMath blocks and push them to the references section.
 */
export const remarkReferences: Plugin<void[], Root> = () => {
  return (tree) => {
    visit(tree, ['code', 'inlineMath'], (node: any, index, parent) => {
      if (node.type === 'code' || node.type === 'inlineMath') {
        let currentMatch;
        let textWithoutCites = node.value;

        const REFERENCES_NODE: Paragraph = {
          type: 'paragraph',
          data: {
            hName: 'references',
          },
          children: [],
        };

        while ((currentMatch = CITE_REGEX.exec(node.value)) !== null) {
          if (currentMatch.length !== 5) continue;
          const { 1: text, 2: generationId, 3: start, 4: end } = currentMatch;

          textWithoutCites = textWithoutCites.replace(currentMatch[0], decodeURIComponent(text));
          const cite = {
            type: 'textDirective',
            data: {
              hName: 'cite',
              hProperties: {
                generationId,
                start,
                end,
                isCodeSnippet: true,
              },
            },
            children: [
              {
                type: 'text',
                value: 'Reference: #' + (REFERENCES_NODE.children.length + 1),
              },
            ],
          };

          // @ts-ignore
          REFERENCES_NODE.children.push(...[cite, COMMA_NODE]);
        }

        if (REFERENCES_NODE.children.length && parent && index !== undefined) {
          if (node.type === 'inlineMath') {
            node.data.hChildren[0].value = textWithoutCites;
          }
          node.value = textWithoutCites;

          // remove the last comma
          REFERENCES_NODE.children.pop();

          // add the references node after the current node
          parent.children.splice(index + 1, 0, REFERENCES_NODE);

          // skip the nodes we just added and the original node
          return index + 2;
        }
      }
    });
  };
};
