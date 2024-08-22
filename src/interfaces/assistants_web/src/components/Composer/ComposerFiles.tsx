'use client';

import React from 'react';

import { Icon, Skeleton, Text } from '@/components/UI';
import { useFilesStore, useParamsStore } from '@/stores';
import { cn, formatFileSize, getFileExtension } from '@/utils';

/**
 * @description Displays files that have been prepared to be uploaded along with the next chat request
 */
export const ComposerFiles = () => {
  const {
    files: { composerFiles, uploadingFiles },
    deleteUploadingFile,
    deleteComposerFile,
  } = useFilesStore();

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();

  const handleComposerFileDelete = (fileId: string) => {
    deleteComposerFile(fileId);

    if (fileIds?.some((d) => d === fileId)) {
      setParams({ fileIds: fileIds.filter((d) => d !== fileId) });
    }
  };

  const noErrorUploadingFiles = uploadingFiles.filter((document) => !document.error);

  if (composerFiles.length === 0 && noErrorUploadingFiles.length === 0) return null;

  return (
    <div className="flex max-h-36 flex-wrap gap-2 overflow-scroll p-2">
      {composerFiles.map((file, index) => (
        <File
          key={index}
          name={file.file_name}
          size={file.file_size ?? 0}
          onDelete={() => handleComposerFileDelete(file.id ?? '')}
        />
      ))}
      {noErrorUploadingFiles.map((document, index) => (
        <File
          key={index}
          name={document.file.name}
          progress={document.progress}
          onDelete={() => deleteUploadingFile(document.id ?? '')}
        />
      ))}
    </div>
  );
};

const File: React.FC<{
  name?: string;
  size?: number;
  progress?: number;
  onDelete: VoidFunction;
}> = ({ name = '', size, progress, onDelete }) => {
  const type = getFileExtension(name ?? '')?.replace(/^./, '');
  const fileSize = size !== undefined ? formatFileSize(size) : undefined;

  return (
    <div
      className={cn(
        'group flex w-48 gap-x-2 rounded bg-mushroom-600/10 p-3 md:w-60',
        'transition-colors ease-in-out hover:bg-mushroom-600/20'
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
          className="flex h-4 w-4 flex-shrink-0 text-mushroom-300 dark:text-marble-850 md:invisible md:group-hover:visible"
        >
          <Icon name="close" />
        </button>
      )}
    </div>
  );
};
