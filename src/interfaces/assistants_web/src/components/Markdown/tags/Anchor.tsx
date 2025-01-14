'use client';

import { ComponentPropsWithoutRef, FC } from 'react';
import { ExtraProps } from 'react-markdown';

import { Icon } from '@/components/UI';
import { useOutputFiles } from '@/stores';

export const Anchor: FC<ComponentPropsWithoutRef<'a'> & ExtraProps> = ({ children, node }) => {
  const { outputFiles } = useOutputFiles();
  const nodeHref = node?.properties.href;

  if (typeof children === 'string' && typeof nodeHref === 'string') {
    const outputFile = Object.entries(outputFiles).find(([key]) => nodeHref.includes(key))?.[1];

    const downloadUrl = outputFile?.downloadUrl;

    if (downloadUrl) {
      return (
        <a href={downloadUrl} download={outputFile.name} className="flex items-center gap-1">
          {children}
          <Icon name="download" />
        </a>
      );
    }
  }

  return <a dir="auto">{children}</a>;
};
