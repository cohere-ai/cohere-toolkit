'use client';

import { ReactNode, useState } from 'react';

import { useFocusFileInput } from '@/hooks';
import { cn } from '@/utils';

import { Text } from './Text';

// Hidden files that should not be uploaded
const IGNORED_FILES = ['.DS_Store'];
export type FileAccept =
  | 'text/csv'
  | 'text/plain'
  | 'text/html'
  | 'text/markdown'
  | 'text/tab-separated-values'
  | 'text/calendar'
  | 'application/msword'
  | 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  | 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  | 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
  | 'application/json'
  | 'application/ld+json'
  | 'application/pdf'
  | 'application/epub+zip'
  | 'application/vnd.apache.parquet';

type Props = {
  active: boolean;
  onUploadFile: (files: File[]) => void;
  label?: ReactNode;
  accept?: FileAccept[];
};

export const DragDropFileInput: React.FC<Props> = ({
  active,
  label = (
    <>
      Drag and drop files here or <u>browse files</u>
    </>
  ),
  accept = ['application/pdf', 'text/plain'],
  onUploadFile,
}) => {
  const { focusFileInput } = useFocusFileInput();
  const [dragActive, setDragActive] = useState(false);

  const handleUploadFile = async (files: File[]) => {
    focusFileInput();
    onUploadFile(files);
  };

  const handleDrop = async (e: React.DragEvent<HTMLInputElement>) => {
    const droppedFilesSystem = e.dataTransfer.items[0].webkitGetAsEntry();
    if (!droppedFilesSystem) return;
    const filesList: File[] = [];

    const traverseFolder = async (fileSystem: FileSystemDirectoryEntry): Promise<void> => {
      if (fileSystem.isDirectory) {
        const directoryReader = fileSystem.createReader();
        return new Promise((resolve) => {
          directoryReader.readEntries(async function (entries) {
            for (let i = 0; i < entries.length; i++) {
              const entry = entries[i];

              if (IGNORED_FILES.includes(entry.name)) {
                continue;
              }
              if (entry.isDirectory) {
                await traverseFolder(entry as FileSystemDirectoryEntry);
              } else if (entry.isFile) {
                const fileEntry = entry as FileSystemFileEntry;
                const readFile = () =>
                  new Promise((fileReadResolve) => {
                    fileEntry.file((f) => {
                      filesList.push(f);
                      fileReadResolve(f);
                    });
                  });
                await readFile();
              }
              if (i === entries.length - 1) {
                resolve();
              }
            }
          });
        });
      }
    };
    await traverseFolder(droppedFilesSystem.filesystem.root);
    handleUploadFile(filesList);

    setDragActive(false);
  };

  return (
    <div
      className={cn(
        'relative flex h-28 w-full flex-col items-center justify-center rounded-md border border-mushroom-800 px-3 py-6',
        'transition duration-200',
        'border-dashed bg-mushroom-950',
        'absolute inset-0 z-drag-drop-input-overlay hidden h-full w-full rounded border-none bg-mushroom-800',
        {
          flex: active,
          'border-solid bg-mushroom-800': dragActive,
        }
      )}
    >
      {dragActive ? (
        <Text className="max-w-[170px] text-center text-mushroom-300">Drop files to upload</Text>
      ) : (
        <>
          <Text className="max-w-[210px] text-center text-mushroom-300">{label}</Text>
          <Text className="text-center text-mushroom-400" styleAs="caption">
            .PDF or .TXT, Max 20MB
          </Text>
        </>
      )}
      <input
        className="absolute left-0 top-0 h-full w-full opacity-0"
        type="file"
        multiple
        accept={accept.toString()}
        onDragEnter={() => setDragActive(true)}
        onDragOver={() => setDragActive(true)}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      />
    </div>
  );
};
