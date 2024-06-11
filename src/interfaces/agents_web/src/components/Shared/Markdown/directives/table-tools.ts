import type { Root } from 'mdast';
import { toString as markdownNodeToString } from 'mdast-util-to-string';
import type { Plugin } from 'unified';
import { visit } from 'unist-util-visit';

export type StructuredTable = {
  header: string[];
  rows: string[][];
};

/**
 * Takes a markdown node as input and tries to extract a table structure from it. If the node is
 * not of the 'table' type or if the header and any row has a different amount of cells, the function returns null.
 *
 * @param {any} node - A markdown node containing the table to be parsed.
 */
const extractStructureFromMarkdownTable = (node: any): StructuredTable | null => {
  if (node.type !== 'table') return null;
  if (!Array.isArray(node.children) || node.children.length <= 1) return null;

  let structuredTable: StructuredTable = {
    header: [],
    rows: [],
  };

  /**
   * A 'table' node in markdown has children which are of type `TableRow` and each `TableRow` has children of the type
   * `TableCell`. Each `TableCell` may not just contain text (they can contain other directive such as cite or links) so
   * we extract the textual content from each `TableCell` (similar to the `innerText` function in HTML)
   **/

  const firstChild = node?.children?.[0]?.children ?? [];
  for (const tableCell of firstChild) {
    const cellText = markdownNodeToString(tableCell);
    structuredTable.header.push(cellText);
  }

  if (structuredTable.header.length === 0) {
    return null;
  }

  const headerLength = structuredTable.header.length;
  for (let i = 1; i < node.children.length; i++) {
    const tableRow = node.children[i];
    const row = [];
    for (const tableCell of tableRow.children) {
      const cellText = markdownNodeToString(tableCell);
      row.push(cellText);
    }

    if (row.length !== headerLength) {
      return null;
    }

    structuredTable.rows.push(row);
  }

  return structuredTable;
};

/**
 * A remark plugin that reads a Markdown table from the node and adds a hProperty with the table structure making
 * the table data available to plugins and markdown renderers after.
 **/
export const renderTableTools: Plugin<void[], Root> = () => {
  return (tree, file) => {
    visit(tree, (node: any, index, parent) => {
      if (node.type !== 'table') return;

      const structuredTable = extractStructureFromMarkdownTable(node);
      if (structuredTable === null) return;

      node.data = node.data || {};
      node.data.hProperties = {
        ...node.data.hProperties,
        structuredTable: structuredTable,
      };
    });
  };
};
