'use client';

import React, { useMemo } from 'react';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

/**
 * @description Renders an error message if there is an error with the file upload
 */
export const FileError: React.FC<{ error?: string; file?: File; className?: string }> = ({
  error,
  file,
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
