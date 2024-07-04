import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { Text } from '@/components/Shared/Text';

type Props = {
  title?: string;
  type?: string;
  identifier?: string;
} & ExtraProps &
  ComponentPropsWithoutRef<'div'>;

export const Antartifact: Component<Props> = ({ children, title }) => {
  return (
    <div className="rounded border border-marble-500">
      <header className="flex border-b border-marble-500">
        <div className="border-r border-marble-500 p-4">
          <Icon name="file" kind="outline" />
        </div>
        <Text className="p-4">{title}</Text>
      </header>
      {children}
    </div>
  );
};
