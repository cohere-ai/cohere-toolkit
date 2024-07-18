'use client';

import { ComponentPropsWithoutRef, useMemo } from 'react';
import ReactMarkdown, { Components, UrlTransform } from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkDirective from 'remark-directive';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { PluggableList } from 'unified';

import { removeExtraBlankSpaces } from '@/components/Shared/Markdown/directives/utils';
import { Iframe } from '@/components/Shared/Markdown/tags/Iframe';
import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

import { renderRemarkCites } from './directives/cite';
import { remarkReferences } from './directives/code';
import { renderTableTools } from './directives/table-tools';
import { renderRemarkTags } from './directives/tag';
import { renderRemarkUnknowns } from './directives/unknown';
import { P } from './tags/P';
import { Pre } from './tags/Pre';
import { References } from './tags/References';

type MarkdownTextProps = {
  text: string;
  className?: string;
  customComponents?: Components;
  renderLaTex?: boolean;
  renderRawHtml?: boolean;
  customRemarkPlugins?: PluggableList;
  customRehypePlugins?: PluggableList;
  allowedElements?: Array<string>;
  unwrapDisallowed?: boolean;
  urlTransform?: UrlTransform | null;
} & ComponentPropsWithoutRef<'div'>;

export const getActiveMarkdownPlugins = (options: {
  renderRawHtml?: boolean;
  renderLaTex?: boolean;
}): { remarkPlugins: PluggableList; rehypePlugins: PluggableList } => {
  const remarkPlugins: PluggableList = [
    // remarkGFm is a plugin that adds support for GitHub Flavored Markdown
    remarkGfm,
    // remarkDirective is a plugin that adds support for custom directives
    remarkDirective,
    // renderRemarkCites is a plugin that adds support for :cite[] directives
    renderRemarkCites,
    // renderRemarkTags is a plugin that adds support for :tag[] directives
    renderRemarkTags,
    // renderRemarkUnknowns is a plugin that converts unrecognized directives to regular text nodes
    renderRemarkUnknowns,
    remarkReferences,
  ];

  const rehypePlugins: PluggableList = [
    // renderTableTools is a plugin that detects tables and saves them in a readable structure
    renderTableTools,
    // rehypeHighlight is a plugin that adds syntax highlighting to code blocks
    // Version 7.0.0 seems to have a memory leak bug that's why we are using 6.0.0
    // https://github.com/remarkjs/react-markdown/issues/791#issuecomment-2096106784
    // @ts-ignore
    [rehypeHighlight, { detect: true, ignoreMissing: true }],
  ];

  if (options.renderRawHtml) {
    // rehypeRaw is a plugin that adds support for raw HTML
    rehypePlugins.push(rehypeRaw);
    // removeExtraBlankSpaces is a plugin that removes extra blank spaces from the text elements
    rehypePlugins.push(removeExtraBlankSpaces);
  }

  if (options.renderLaTex) {
    // remarkMath is a plugin that adds support for math
    remarkPlugins.push([remarkMath, { singleDollarTextMath: false }]);
    // options: https://katex.org/docs/options.html
    rehypePlugins.push([rehypeKatex, { output: 'mathml' }]);
  }

  return { remarkPlugins, rehypePlugins };
};

/**
 * Convenience component to help apply the styling to markdown texts.
 */
export const Markdown = ({
  className = '',
  text,
  customComponents,
  customRemarkPlugins = [],
  customRehypePlugins = [],
  renderLaTex = true,
  renderRawHtml = true,
  allowedElements,
  unwrapDisallowed,
  urlTransform,
  ...rest
}: MarkdownTextProps) => {
  const { remarkPlugins, rehypePlugins } = getActiveMarkdownPlugins({ renderLaTex, renderRawHtml });

  // Memoize to avoid re-rendering that occurs with Pre due to lambda function
  // @ts-ignore
  const components: Components = useMemo(
    () => ({
      // @ts-ignore
      pre: (props) => <Pre {...props} />,
      p: P,
      references: References,
      // @ts-ignore
      iframe: Iframe,
      ...customComponents,
    }),
    [customComponents]
  );

  return (
    <Text
      as="div"
      dir="auto"
      className={cn(
        'prose max-w-none',
        'prose-p:my-0',
        'prose-ol:my-0 prose-ol:space-y-2 prose-ol:whitespace-normal',
        'prose-ul:my-0 prose-ul:space-y-2 prose-ul:whitespace-normal',
        'prose-li:my-0',
        'prose-pre prose-pre:mb-0 prose-pre:mt-0',
        'prose-code:!whitespace-pre-wrap prose-code:!bg-transparent prose-code:!p-0',
        'prose-img:my-2',
        'prose-headings:my-0',
        'prose-h1:font-medium prose-h2:font-medium prose-h3:font-medium prose-h4:font-medium prose-h5:font-medium prose-h6:font-medium prose-strong:font-medium',
        'prose-h1:text-xl prose-h2:text-lg prose-h3:text-base prose-h4:text-base prose-h5:text-base prose-h6:text-base',
        'prose-pre:border prose-pre:border-mushroom-800 prose-pre:bg-mushroom-900 prose-pre:text-volcanic-100',
        className
      )}
      {...rest}
    >
      <ReactMarkdown
        remarkPlugins={[...remarkPlugins, ...customRemarkPlugins]}
        rehypePlugins={[...rehypePlugins, ...customRehypePlugins]}
        unwrapDisallowed={unwrapDisallowed}
        allowedElements={allowedElements}
        components={components}
        urlTransform={urlTransform}
        skipHtml={false}
      >
        {text}
      </ReactMarkdown>
    </Text>
  );
};
