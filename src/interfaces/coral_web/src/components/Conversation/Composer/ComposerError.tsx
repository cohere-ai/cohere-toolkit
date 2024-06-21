import React from 'react';

import { FileError } from '@/components/FileError';
import { Text } from '@/components/Shared';
import { useFilesStore } from '@/stores';
import { cn } from '@/utils';

type Props = { isToolAuthRequired: boolean; className?: string };
/**
 * @description Renders an error message under the composer. Right now it is only for file upload
 * errors.
 */
export const ComposerError: React.FC<Props> = ({ isToolAuthRequired, className = '' }) => {
  const {
    files: { uploadingFiles },
  } = useFilesStore();
  const latestFile = uploadingFiles[uploadingFiles.length - 1];

  if (isToolAuthRequired) {
    return (
      <Text className="mt-2 text-danger-500">
        You need to connect your Google Drive before you can use this assistant. Authenticate here.
      </Text>
    );
  }
  return (
    <FileError
      error={latestFile?.error}
      file={latestFile?.file}
      className={cn('min-h-[14px]', className)}
    />
  );
};
