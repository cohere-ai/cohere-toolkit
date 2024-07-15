import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

import { CodeSnippet } from '@/components/Shared/CodeSnippet';
import { Mermaid } from '@/components/Shared/Markdown/components/Mermaid';
import { Shell } from '@/components/Shared/Markdown/components/Shell';

type Props = {
  title: string;
  type: string | 'application/vnd.ant.code' | 'application/vnd.ant.mermaid';
  identifier: string;
  language?: string;
} & ExtraProps &
  ComponentPropsWithoutRef<'div'>;

export const Antartifact: Component<Props> = ({ children, type, title, identifier }) => {
  let content: React.ReactNode = null;

  switch (type) {
    case 'application/vnd.ant.code':
      content = <CodeSnippet lang="python" codeSnippet={children as string} />;
      break;
    case 'application/vnd.ant.mermaid':
      content = <Mermaid chart={children as string} />;
      break;
    default:
      content = children;
      break;
  }

  return (
    <Shell type={type} title={title} identifier={identifier}>
      {content}
    </Shell>
  );
};
