import React from 'react';

import { File } from '@/cohere-client';
import { BasicButton, Icon, Text } from '@/components/Shared';
import { formatFileSize } from '@/utils';

/**
 * @description Renders a file that has been uploaded
 */
export const UploadedFile: React.FC<{
  file: File;
  onDelete?: VoidFunction;
}> = ({ file, onDelete }) => {
  const { file_name: name, file_size: size } = file;
  return (
    <div className="relative flex w-full items-center gap-2 rounded border px-2 py-2 md:w-file">
      {onDelete && (
        <BasicButton
          kind="minimal"
          size="sm"
          className="absolute right-2 top-2 px-0 py-0.5 text-volcanic-900"
          startIcon={<Icon name="close" />}
          onClick={onDelete}
        />
      )}
      <Icon name="file" kind="outline" />
      <div className="flex w-[80%] max-w-40 flex-col gap-y-1 overflow-hidden md:w-[70%] md:max-w-40">
        <Text className="w-full truncate">{name}</Text>
        <Text styleAs="caption" className="text-volcanic-700">
          {formatFileSize(size ?? 0)}
        </Text>
      </div>
    </div>
  );
};
