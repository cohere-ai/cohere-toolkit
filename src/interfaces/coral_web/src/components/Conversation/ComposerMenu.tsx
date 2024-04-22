import React, { useRef } from 'react';

import IconButton from '@/components/IconButton';
import { ACCEPTED_FILE_TYPES } from '@/constants';

type Props = {
  onUploadFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

/**
 *
 * @description Displays a menu with actions for the composer.
 */
export const ComposerMenu: React.FC<Props> = ({ onUploadFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileButtonClick: React.MouseEventHandler<HTMLElement> = () => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
  };

  return (
    <div className="my-2 ml-1 h-8 w-8 overflow-hidden md:my-4">
      <IconButton iconName="clip" onClick={handleFileButtonClick} />
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join('')}
        className="hidden"
        onChange={onUploadFile}
      />
    </div>
  );
};
