'use client';

import React from 'react';

import { DragDropFileInput } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { useFocusFileInput } from '@/hooks/actions';
import { cn } from '@/utils';

export const DragDropFileUploadOverlay: React.FC<{
  active: boolean;
  onUploadFile: (files: File[]) => void;
}> = ({ active, onUploadFile }) => {
  const { focusFileInput } = useFocusFileInput();

  const handleUploadFile = async (files: File[]) => {
    focusFileInput();
    onUploadFile(files);
  };

  return (
    <DragDropFileInput
      label="Drop to upload"
      subLabel=""
      onDrop={handleUploadFile}
      multiple
      accept={ACCEPTED_FILE_TYPES}
      dragActiveDefault={true}
      className={cn(
        'absolute inset-0 z-drag-drop-input-overlay hidden h-full w-full rounded border-none bg-mushroom-800',
        {
          flex: active,
        }
      )}
    />
  );
};
