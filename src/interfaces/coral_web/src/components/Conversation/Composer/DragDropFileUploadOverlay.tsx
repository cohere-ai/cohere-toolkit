'use client';

import React from 'react';

import { DragDropFileInput } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { STRINGS } from '@/constants/strings';
import { useFocusFileInput } from '@/hooks/actions';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

export const DragDropFileUploadOverlay: React.FC<{
  active: boolean;
  onUploadFile: (files: File[]) => void;
}> = ({ active, onUploadFile }) => {
  const { queueFocusFileInput, focusFileInput } = useFocusFileInput();
  const {
    settings: { isConfigDrawerOpen },
  } = useSettingsStore();

  const handleUploadFile = async (files: File[]) => {
    if (!isConfigDrawerOpen) {
      queueFocusFileInput();
    } else {
      focusFileInput();
    }
    onUploadFile(files);
  };

  return (
    <DragDropFileInput
      label={STRINGS.dropToUpload}
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
