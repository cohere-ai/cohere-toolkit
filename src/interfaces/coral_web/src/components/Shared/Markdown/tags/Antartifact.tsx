import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

import { CodeSnippet } from '@/components/Shared/CodeSnippet';
import { Icon } from '@/components/Shared/Icon';
import { Mermaid } from '@/components/Shared/Markdown/components/Mermaid';
import { Text } from '@/components/Shared/Text';

type Props = {
  title?: string;
  type?: string | 'application/vnd.ant.code' | 'application/vnd.ant.mermaid';
  identifier?: string;
  language?: string;
} & ExtraProps &
  ComponentPropsWithoutRef<'div'>;

export const Antartifact: Component<Props> = ({ children, type, title, identifier }) => {
  let content: React.ReactNode = children;

  if (type === 'application/vnd.ant.code') {
    // TODO: retrieve all the text from the children
    // go trought the children and get the code
    let code = '';
    for (const child of children as any) {
      if (typeof child === 'string') {
        code += child;
      } else if (typeof child === 'object' && 'props' in child) {
        code += child.props.children;
      }
    }
    content = <CodeSnippet lang="python" codeSnippet={code} />;
  }

  if (type === 'application/vnd.ant.mermaid') {
    const chart = children as string;
    content = <Mermaid chart={chart} />;
  }

  return (
    <div className="rounded border border-marble-500">
      <header className="flex border-b border-marble-500">
        <div className="flex items-center gap-1 border-r border-marble-500 p-4">
          <Icon name="file" kind="outline" />
          <Text>{type}</Text>
        </div>
        <Text className="p-4">{title}</Text>
        <div className="ml-auto border-l border-marble-500 p-4">
          <Text>{identifier}</Text>
        </div>
      </header>
      {content}
    </div>
  );
};
