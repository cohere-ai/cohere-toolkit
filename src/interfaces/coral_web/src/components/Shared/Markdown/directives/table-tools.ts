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
  if (!Array.isArray(node.children) || node.children.length <= 1) return null;

  const structuredTable: StructuredTable = {
    header: [],
    rows: [],
  };

  const header = node.children[0];
  if (header.tagName !== 'thead') return null;

  const headerRow = header.children[0];
  if (headerRow.tagName !== 'tr') return null;

  for (const cell of headerRow.children) {
    if (cell.tagName !== 'th') return null;
    structuredTable.header.push(markdownNodeToString(cell));
  }

  const body = node.children[1];
  if (body.tagName !== 'tbody') return null;

  for (const row of body.children) {
    if (row.tagName !== 'tr') return null;

    const rowCells = [];
    for (const cell of row.children) {
      if (cell.tagName !== 'td') return null;
      rowCells.push(markdownNodeToString(cell));
    }

    if (rowCells.length !== structuredTable.header.length) return null;
    structuredTable.rows.push(rowCells);
  }

  return structuredTable;
};

type Options = {};

/**
 * A remark plugin that reads a Markdown table from the node and adds a hProperty with the table structure making
 * the table data available to plugins and markdown renderers after.
 **/
export const renderTableTools: Plugin<[Options?], Root> = () => {
  const visitor = (node: any) => {
    if (node.tagName !== 'table') return;
    const structuredTable = extractStructureFromMarkdownTable(node);
    if (structuredTable === null) return;

    node.data = node.data || {};
    node.data.hProperties = {
      ...node.data.hProperties,
      structuredTable: structuredTable,
    };
  };
  return (tree: Root) => {
    visit(tree, 'element', visitor);
  };
};
