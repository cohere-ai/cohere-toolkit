'use client';

import React, { Fragment, useEffect, useMemo } from 'react';

import { ListFile } from '@/cohere-client';
import { Checkbox, Text, Tooltip } from '@/components/Shared';
import { useFocusFileInput } from '@/hooks/actions';
import { useDefaultFileLoaderTool, useFilesInConversation } from '@/hooks/files';
import { useFilesStore, useParamsStore } from '@/stores';
import { cn, formatFileSize, getWeeksAgo } from '@/utils';

interface UploadedFile extends ListFile {
  checked: boolean;
}

/**
 * @description Files tab content that shows a list of available files
 * File upload is not supported for conversations without an id
 */
export const FilesTab: React.FC<{ className?: string }> = ({ className = '' }) => {
  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();
  const {
    files: { composerFiles },
    deleteComposerFile,
  } = useFilesStore();
  const { isFileInputQueuedToFocus, focusFileInput } = useFocusFileInput();
  const { files } = useFilesInConversation();
  const { enableDefaultFileLoaderTool, disableDefaultFileLoaderTool } = useDefaultFileLoaderTool();

  useEffect(() => {
    if (isFileInputQueuedToFocus) {
      focusFileInput();
    }
  }, [isFileInputQueuedToFocus]);

  const uploadedFiles: UploadedFile[] = useMemo(() => {
    if (!files) return [];

    return files
      .map((document: ListFile) => ({
        ...document,
        checked: (fileIds ?? []).some((id) => id === document.id),
      }))
      .sort(
        (a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      );
  }, [files, fileIds]);

  const dateGroupedUploadedFiles = uploadedFiles.reduce<{
    [title: string]: UploadedFile[];
  }>((groupedFiles, file) => {
    const uploadDate = new Date(file.created_at);
    if (!file.created_at) return groupedFiles;
    const { weeksAgo, weeksAgoStr } = getWeeksAgo(uploadDate);
    const title = weeksAgo <= 1 ? 'Most recent' : weeksAgoStr;

    if (!groupedFiles[title]) {
      groupedFiles[title] = [];
    }
    groupedFiles[title].push(file);

    return groupedFiles;
  }, {});

  const handleToggle = (fileId?: string) => {
    if (!fileId) return;

    let newFileIds: string[] = [];
    if (fileIds?.some((id) => id === fileId)) {
      newFileIds = fileIds.filter((id) => id !== fileId);

      if (composerFiles.some((file) => file.id === fileId)) {
        deleteComposerFile(fileId);
      }
    } else {
      newFileIds = [...(fileIds ?? []), fileId];
    }

    if (newFileIds.length === 0) {
      disableDefaultFileLoaderTool();
    } else {
      enableDefaultFileLoaderTool();
    }

    setParams({ fileIds: newFileIds });
  };

  return (
    <article className={cn('flex flex-col pb-10', className)}>
      <section className="relative flex flex-col gap-y-8 px-5">
        <div className="flex gap-x-2">
          <Text styleAs="label" className="font-medium">
            Files in conversation
          </Text>
          <Tooltip label="To use uploaded files, at least 1 File Upload tool must be enabled" />
        </div>

        {uploadedFiles.length > 0 && (
          <div className="flex w-full flex-col gap-y-14 pb-2">
            <div className="flex flex-col gap-y-4">
              {Object.keys(dateGroupedUploadedFiles).map(
                (title) =>
                  dateGroupedUploadedFiles[title].length > 0 && (
                    <Fragment key={title}>
                      <Text styleAs="label" className="text-volcanic-900">
                        {title}
                      </Text>
                      {dateGroupedUploadedFiles[title].map(
                        ({ file_name: name, file_size: size, id, checked }) => (
                          <div key={id} className="group flex w-full flex-col gap-y-2">
                            <div className="flex w-full items-center justify-between gap-x-2">
                              <div className={cn('flex w-[60%] overflow-hidden lg:w-[70%]')}>
                                <Checkbox
                                  checked={checked}
                                  onChange={() => handleToggle(id)}
                                  label={name}
                                  name={name}
                                  theme="secondary"
                                  className="w-full"
                                  labelClassName="ml-0 truncate w-full"
                                  labelSubContainerClassName="w-full"
                                  labelContainerClassName="w-full"
                                />
                              </div>
                              <div className="flex h-5 w-32 grow items-center justify-end gap-x-1">
                                <Text styleAs="caption" className="text-volcanic-400">
                                  {formatFileSize(size ?? 0)}
                                </Text>
                              </div>
                            </div>
                          </div>
                        )
                      )}
                    </Fragment>
                  )
              )}
            </div>
          </div>
        )}
      </section>
    </article>
  );
};
