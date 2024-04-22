import React from 'react';

import { UploadFile } from '@/cohere-client';
import { UploadedFile } from '@/components/UploadedFile';
import { UploadingFile } from '@/components/UploadingFile';
import { UploadingFile as UploadingFileType } from '@/stores/slices/filesSlice';

type Props = {
  uploadingFiles: UploadingFileType[];
  composerFiles: UploadFile[];
  deleteFile: (fileId: string) => void;
  deleteUploadingFile: (fileId: string) => void;
};

/**
 * @description Displays files that have been prepared to be uploaded along with the next chat request
 */
export const ComposerFiles: React.FC<Props> = ({
  uploadingFiles,
  composerFiles,
  deleteFile,
  deleteUploadingFile,
}) => {
  if (!composerFiles && !uploadingFiles) return null;

  return (
    <div className="flex flex-col flex-wrap gap-y-2 px-2 pb-2 md:flex-row md:gap-x-2">
      {uploadingFiles.map((file) => (
        <UploadingFile key={file.id} file={file} onDelete={() => deleteUploadingFile(file.id)} />
      ))}
      {composerFiles?.map((file) => (
        <UploadedFile key={file.id} file={file} onDelete={() => deleteFile(file.id)} />
      ))}
    </div>
  );
};
