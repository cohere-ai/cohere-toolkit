import React, { useRef } from 'react';

import { EnabledDataSources } from '@/components/Conversation/Composer/EnabledDataSources';
import { IconButton } from '@/components/IconButton';
import { IconName } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { cn } from '@/utils';

type Props = {
  onUploadFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export const ComposerToolbar: React.FC<Props> = ({ onUploadFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleOpenFileExplorer = () => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
  };

  return (
    <div className={cn('flex items-center gap-x-2', 'border-t border-marble-400', 'mx-2 py-2')}>
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join('')}
        className="hidden"
        onChange={onUploadFile}
      />
      <ToolbarActionButton
        tooltipLabel="Attach file (.PDF, .TXT Max 20 MB)"
        icon="clip"
        onClick={handleOpenFileExplorer}
      />
      <EnabledDataSources isStreaming={false} />
    </div>
  );
};

const ToolbarActionButton: React.FC<{
  tooltipLabel: string;
  icon: IconName;
  onClick: React.MouseEventHandler<HTMLButtonElement>;
}> = ({ tooltipLabel, icon, onClick }) => {
  return (
    <IconButton iconName={icon} tooltip={{ label: tooltipLabel }} onClick={onClick} size="sm" />
  );
};
