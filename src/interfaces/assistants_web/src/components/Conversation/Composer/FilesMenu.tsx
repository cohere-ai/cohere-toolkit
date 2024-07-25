import { useRef } from 'react';

import { Icon, Tooltip } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES } from '@/constants';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  onUploadFile: (files: File[]) => void;
};

export const FilesMenu: React.FC<Props> = ({ onUploadFile }) => {
  const { agentId } = useChatRoutes();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUploadFile([...(e.target.files ?? [])]);
  };

  const handleOpenFileExplorer = () => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join(',')}
        className="hidden"
        multiple
        onChange={handleFileInputChange}
      />

      <Tooltip
        label="Attach file (.PDF, .TXT, .MD, .JSON, .CSV, .XSLS, .XLS, .DOCX Max 20 MB)"
        size="sm"
        placement="top"
        hover
        hoverDelay={{ open: 250 }}
      >
        <button
          className={cn(
            'flex items-center justify-center rounded p-1 dark:text-marble-800',
            getCohereColor(agentId, { background: true, contrastText: true })
          )}
          onClick={handleOpenFileExplorer}
        >
          <Icon name="clip" />
        </button>
      </Tooltip>
    </>
  );
};
