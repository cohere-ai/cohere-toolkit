'use client';

import React from 'react';

import { MessageFile } from '@/components/MessageFile';
import { useFilesStore, useParamsStore } from '@/stores';

/**
 * @description Displays files that have been prepared to be uploaded along with the next chat request
 */
export const ComposerFiles = () => {
  const {
    files: { composerFiles, uploadingFiles },
    deleteUploadingFile,
    deleteComposerFile,
  } = useFilesStore();

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();

  const handleComposerFileDelete = (fileId: string) => {
    deleteComposerFile(fileId);

    if (fileIds?.some((d) => d === fileId)) {
      setParams({ fileIds: fileIds.filter((d) => d !== fileId) });
    }
  };

  const noErrorUploadingFiles = uploadingFiles.filter((document) => !document.error);

  if (composerFiles.length === 0 && noErrorUploadingFiles.length === 0) return null;

  return (
    <div className="flex max-h-36 flex-wrap gap-2 overflow-scroll p-2">
      {composerFiles.map((file, index) => (
        <MessageFile
          key={index}
          hoverAnimation
          name={file.file_name ?? ''}
          size={file.file_size ?? 0}
          className="w-48 md:w-60"
          onDelete={() => handleComposerFileDelete(file.id ?? '')}
        />
      ))}
      {noErrorUploadingFiles.map((document, index) => (
        <MessageFile
          key={index}
          hoverAnimation
          name={document.file.name ?? ''}
          progress={document.progress}
          className="w-48 md:w-60"
          onDelete={() => deleteUploadingFile(document.id ?? '')}
        />
      ))}
    </div>
  );
};
