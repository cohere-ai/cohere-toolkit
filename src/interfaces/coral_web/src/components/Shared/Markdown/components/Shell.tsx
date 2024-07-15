import { PropsWithChildren } from 'react';

import { Icon, Text } from '@/components/Shared';

type Props = PropsWithChildren<{
  type: string;
  title: string;
  identifier: string;
}>;

export const Shell: React.FC<Props> = ({ type, title, identifier, children }) => {
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
      {children}
    </div>
  );
};
