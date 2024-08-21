'use client';

import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { useOutputFiles } from '@/stores';

export const Anchor: Component<ComponentPropsWithoutRef<'a'> & ExtraProps> = ({ children }) => {
  const { outputFiles } = useOutputFiles();

  if (typeof children === 'string') {
    const snakeCaseUrl = children.replace(/\s/g, '_').toLowerCase();
    const outputFile = Object.entries(outputFiles).find(([key]) =>
      key.startsWith(snakeCaseUrl)
    )?.[1];
    const downloadUrl = outputFile?.downloadUrl;

    if (downloadUrl) {
      return (
        <a href={downloadUrl} download className="flex items-center gap-1">
          {children}
          <Icon name="download" />
        </a>
      );
    }
  }

  return <a dir="auto">{children}</a>;
};
