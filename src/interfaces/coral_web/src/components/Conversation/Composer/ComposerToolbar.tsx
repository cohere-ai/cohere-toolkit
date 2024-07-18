'use client';

import React, { useRef } from 'react';

import {
  DataSourceMenu,
  Props as DataSourceMenuProps,
} from '@/components/Conversation/Composer/DataSourceMenu';
import { EnabledDataSources } from '@/components/Conversation/Composer/EnabledDataSources';
import { IconButton } from '@/components/IconButton';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { cn } from '@/utils';

type Props = {
  isStreaming: boolean;
  onUploadFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDataSourceMenuToggle: VoidFunction;
  menuProps: DataSourceMenuProps;
};

/**
 * @description Renders the bottom toolbar of the composer that shows available and selected data sources.
 */
export const ComposerToolbar: React.FC<Props> = ({ isStreaming, onUploadFile, menuProps }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleOpenFileExplorer = () => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
  };

  return (
    <div className={cn('flex items-center gap-x-2', 'border-t border-marble-950', 'mx-2 py-2')}>
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join(',')}
        className="hidden"
        onChange={onUploadFile}
      />
      <IconButton
        iconName="clip"
        tooltip={{ label: 'Attach file (.PDF, .TXT Max 20 MB)', size: 'sm' }}
        size="sm"
        onClick={handleOpenFileExplorer}
      />
      <DataSourceMenu {...menuProps} />
      <div className="h-7 w-px bg-marble-950" />
      <EnabledDataSources isStreaming={isStreaming} />
    </div>
  );
};
