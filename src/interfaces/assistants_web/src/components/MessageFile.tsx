'use client';

import React from 'react';

import { Icon, Skeleton, Text } from '@/components/Shared';
import { cn, formatFileSize } from '@/utils';
import { getFileExtension } from '@/utils';

type Props = {
  name?: string;
  size?: number;
  progress?: number;
  hoverAnimation?: boolean;
  className?: string;
  onDelete?: VoidFunction;
};

const getFileType = (fileName: string) => {
  return getFileExtension(fileName)?.replace(/^./, ''); // replace first character if it is a period
};

/**
 * @description Renders a file card in a chat message or composer.
 */
export const MessageFile: React.FC<Props> = ({
  name,
  progress,
  size,
  hoverAnimation = false,
  className,
  onDelete,
}) => {
  const type = getFileType(name ?? '');
  const fileSize = size !== undefined ? formatFileSize(size) : undefined;

  return (
    <div
      className={cn(
        'group flex w-60 gap-x-2 rounded bg-mushroom-600/10 p-3',
        'transition-colors ease-in-out',
        {
          'hover:bg-mushroom-600/20': hoverAnimation,
        },
        className
      )}
    >
      <div
        className={cn(
          'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded',
          'transition-colors ease-in-out',
          'bg-mushroom-600/20 text-mushroom-300 dark:text-marble-950',
          { 'text-mushroom-500 dark:text-volcanic-600': progress !== undefined }
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

          {progress ? (
            <Text styleAs="caption" className="text-volcanic-300 dark:text-marble-900">
              {progress}%
            </Text>
          ) : fileSize ? (
            <Text styleAs="caption" className="text-volcanic-500 dark:text-marble-900">
              {fileSize}
            </Text>
          ) : (
            <Skeleton className="h-5 w-10 bg-mushroom-600/20 dark:bg-volcanic-600" />
          )}
        </div>
      </div>
      {onDelete && (
        <button
          type="button"
          onClick={onDelete}
          className="flex h-4 w-4 flex-shrink-0 text-mushroom-300 md:invisible md:group-hover:visible dark:text-marble-850"
        >
          <Icon name="close" />
        </button>
      )}
    </div>
  );
};
