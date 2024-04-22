import { Fragment, useEffect, useMemo } from 'react';

import { ListFile } from '@/cohere-client';
import { Text, Tooltip } from '@/components/Shared';
import { useFocusFileInput } from '@/hooks/actions';
import { useFilesInConversation } from '@/hooks/files';
import { useParamsStore } from '@/stores';
import { cn, formatFileSize, getWeeksAgo } from '@/utils';

export interface UploadedFile extends ListFile {
  checked: boolean;
}

/**
 * Contains the file uploader and a list of all files being uploaded + that have been uploaded
 */
const Files: React.FC = () => {
  const {
    params: { fileIds },
  } = useParamsStore();
  const { isFileInputQueuedToFocus, focusFileInput } = useFocusFileInput();
  const { files } = useFilesInConversation();

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

  return (
    <div className="flex w-full flex-col gap-y-6">
      {uploadedFiles.length > 0 && (
        <div className="flex flex-col gap-y-14 pb-2">
          <div className="flex flex-col gap-y-4">
            {Object.keys(dateGroupedUploadedFiles).map(
              (title) =>
                dateGroupedUploadedFiles[title].length > 0 && (
                  <Fragment key={title}>
                    <Text styleAs="label" className="text-volcanic-100">
                      {title}
                    </Text>
                    {dateGroupedUploadedFiles[title].map(
                      ({ file_name: name, file_size: size, id }) => (
                        <div key={id} className="group flex w-full flex-col gap-y-2">
                          <div className="flex w-full items-center justify-between gap-x-2">
                            <div className={cn('flex w-[60%] lg:w-[70%]')}>
                              <Text className="ml-0 w-full truncate">{name || ''}</Text>
                            </div>
                            <div className="flex h-5 w-32 grow items-center justify-end gap-x-1">
                              <Text styleAs="caption" className="text-volcanic-700">
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
    </div>
  );
};

export const FilesSection: React.FC = () => {
  return (
    <section className="relative flex flex-col gap-y-8 px-5">
      <div className="flex gap-x-2">
        <Text styleAs="label" className="font-medium">
          Files in conversation
        </Text>
        <Tooltip label="To use uploaded files, at least 1 File Upload tool must be enabled" />
      </div>
      <Files />
    </section>
  );
};
