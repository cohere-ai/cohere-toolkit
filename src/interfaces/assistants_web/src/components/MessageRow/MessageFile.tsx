'use client';

import React from 'react';

import { Icon, Skeleton, Text } from '@/components/UI';
import { cn, formatFileSize, getFileExtension } from '@/utils';

type Props = {
  name?: string;
  size?: number;
};

const getFileType = (fileName: string) => {
  return getFileExtension(fileName)?.replace(/^./, ''); // replace first character if it is a period
};

/**
 * @description Renders a file card in a chat message or composer.
 */
export const MessageFile: React.FC<Props> = ({ name, size }) => {
  const type = getFileType(name ?? '');
  const fileSize = size !== undefined ? formatFileSize(size) : undefined;

  return (
    <div
      className={cn(
        'group flex w-60 gap-x-2 rounded bg-mushroom-600/10 p-3',
        'transition-colors ease-in-out'
      )}
    >
      <div
        className={cn(
          'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded',
          'transition-colors ease-in-out',
          'bg-mushroom-600/20 text-mushroom-300 dark:text-marble-950'
        )}
      >
        <Icon name="file" kind="outline" />
      </div>
      <div className="flex w-full flex-grow flex-col gap-y-0.5 truncate">
        <Text styleAs="label" className="w-full truncate font-medium">
          {name}
        </Text>
        <div className="flex items-center gap-x-2 uppercase">
          {type && (
            <Text styleAs="caption" className="text-volcanic-500 dark:text-marble-900">
              {type} •
            </Text>
          )}

          {fileSize ? (
            <Text styleAs="caption" className="text-volcanic-500 dark:text-marble-900">
              {fileSize}
            </Text>
          ) : (
            <Skeleton className="h-5 w-10 bg-mushroom-600/20 dark:bg-volcanic-600" />
          )}
        </div>
      </div>
    </div>
  );
};
