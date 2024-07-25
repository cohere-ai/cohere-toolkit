'use client';

import React, { useRef } from 'react';

import {
  DataSourceMenu,
  Props as DataSourceMenuProps,
} from '@/components/Conversation/Composer/DataSourceMenu';
import { IconButton } from '@/components/IconButton';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { cn } from '@/utils';

type Props = {
  onUploadFile: (files: File[]) => void;
  onDataSourceMenuToggle: VoidFunction;
  menuProps: DataSourceMenuProps;
};

/**
 * @description Renders the bottom toolbar of the composer that shows available and selected data sources.
 */
export const ComposerToolbar: React.FC<Props> = ({ onUploadFile, menuProps }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleOpenFileExplorer = () => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUploadFile([...(e.target.files ?? [])]);
  };

  return (
    <div
      className={cn(
        'flex items-center gap-x-2',
        'border-t border-marble-950 dark:border-volcanic-300',
        'mx-2 py-2'
      )}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join(',')}
        className="hidden"
        multiple
        onChange={handleFileInputChange}
      />
      <IconButton
        iconName="clip"
        tooltip={{
          label: 'Attach file (.PDF, .TXT, .MD, .JSON, .CSV, .XSLS, .XLS, .DOCX Max 20 MB)',
          size: 'sm',
        }}
        size="sm"
        onClick={handleOpenFileExplorer}
      />
      <DataSourceMenu {...menuProps} />
    </div>
  );
};
