import React from 'react';

import { FileError } from '@/components/FileError';
import { useFilesStore } from '@/stores';
import { cn } from '@/utils';

/**
 * @description Renders an error message under the composer. Right now it is only for file upload
 * errors.
 */
export const ComposerError: React.FC<{ className?: string }> = ({ className = '' }) => {
  const {
    files: { uploadingFiles },
  } = useFilesStore();
  const latestFile = uploadingFiles[uploadingFiles.length - 1];

  return (
    <FileError
      error={latestFile?.error}
      file={latestFile?.file}
      className={cn('min-h-[14px]', className)}
    />
  );
};
