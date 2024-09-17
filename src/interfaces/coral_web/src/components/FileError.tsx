'use client';

import React, { useMemo } from 'react';

import { Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { cn } from '@/utils';

/**
 * @description Renders an error message if there is an error with the file upload
 */
export const FileError: React.FC<{ error?: string; file?: File; className?: string }> = ({
  error,
  className = '',
}) => {
  const errorText = useMemo<React.ReactNode>(() => {
    switch (error) {
      case 'fileSizeExceeded':
        return STRINGS.fileSizeExceededError;
      case 'incorrectFileType':
        return STRINGS.incorrectFileTypeError;
      case 'fileNameExists':
        // const fileName = file?.name;
        return STRINGS.fileNameExistsError;
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
