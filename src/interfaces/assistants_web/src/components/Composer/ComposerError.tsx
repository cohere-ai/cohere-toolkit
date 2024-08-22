'use client';

import React, { useMemo } from 'react';

import { Text } from '@/components/UI';
import { useFilesStore } from '@/stores';
import { cn } from '@/utils';

type Props = { className?: string };
/**
 * @description Renders an error message under the composer. Right now it is only for file upload
 * errors.
 */
export const ComposerError: React.FC<Props> = ({ className = '' }) => {
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

const FileError: React.FC<{ error?: string; file?: File; className?: string }> = ({
  error,
  className = '',
}) => {
  const errorText = useMemo<React.ReactNode>(() => {
    switch (error) {
      case 'fileSizeExceeded':
        return 'Each file can only be 20 MB max';
      case 'incorrectFileType':
        return 'File type has to be .PDF or .TXT.';
      case 'fileNameExists':
        // const fileName = file?.name;
        return 'File with the same name already exists.';
      default:
        return error;
    }
  }, [error]);

  return (
    <Text styleAs="caption" className={cn('text-danger-350', className)}>
      {errorText}
    </Text>
  );
};
