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
        'group flex w-60 gap-x-2 rounded bg-secondary-500/10 p-3',
        'transition-colors ease-in-out',
        {
          'hover:bg-secondary-500/20': hoverAnimation,
        },
        className
      )}
    >
      <div
        className={cn(
          'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded',
          'transition-colors ease-in-out',
          'bg-secondary-500/20 text-secondary-800',
          { 'text-secondary-600': progress !== undefined }
        )}
      >
        <Icon name="file" kind="outline" size="md" />
      </div>
      <div className="flex w-full flex-grow flex-col gap-y-0.5 truncate">
        <Text styleAs="label" className="w-full truncate font-medium">
          {name}
        </Text>
        <div className="flex items-center gap-x-2 uppercase">
          {type && (
            <Text styleAs="caption" className="text-volcanic-600">
              {type} •
            </Text>
          )}

          {progress ? (
            <Text styleAs="caption" className="text-volcanic-800">
              {progress}%
            </Text>
          ) : fileSize ? (
            <Text styleAs="caption" className="text-volcanic-600">
              {fileSize}
            </Text>
          ) : (
            <Skeleton className="h-5 w-10 bg-secondary-500/20" />
          )}
        </div>
      </div>
      {onDelete && (
        <button
          type="button"
          onClick={onDelete}
          className="flex h-4 w-4 flex-shrink-0 text-secondary-800 md:invisible md:group-hover:visible"
        >
          <Icon name="close" />
        </button>
      )}
    </div>
  );
};
