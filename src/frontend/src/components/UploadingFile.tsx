import React from 'react';

import { BasicButton, Icon, Text } from '@/components/Shared';
import { UploadingFile as UploadingFileType } from '@/stores/slices/filesSlice';

export const UploadingFile: React.FC<{
  file: UploadingFileType;
  onDelete: (fileId: string) => void;
}> = ({ file: { id, file, error }, onDelete }) => {
  const isError = !!error;
  return (
    <div className="relative flex w-full items-center gap-2 rounded border px-2 py-2 md:w-56">
      <BasicButton
        kind="minimal"
        size="sm"
        className="absolute right-2 top-2 px-0 py-0.5 text-volcanic-900"
        startIcon={<Icon name="close" />}
        onClick={() => onDelete(id)}
      />
      <Icon name="file" kind="outline" />
      <div className="flex w-[85%] max-w-40 flex-col gap-y-1 overflow-hidden md:w-[75%] md:max-w-full">
        <div className="flex w-11/12">
          <Text className="w-full truncate">{file.name}</Text>
        </div>
        {isError ? (
          <Text styleAs="caption" className="text-danger-500">
            {error}
          </Text>
        ) : (
          <div
            role="progressbar"
            className="relative my-1.5 h-1 w-full overflow-hidden rounded bg-marble-300"
          >
            <div className="absolute inset-0 h-full w-1/4 animate-left-to-right rounded bg-primary-300" />
          </div>
        )}
      </div>
    </div>
  );
};
