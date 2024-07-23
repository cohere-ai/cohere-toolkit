'use client';

import { ReactNode, useState } from 'react';

import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

// Hidden files that should not be uploaded
const IGNORED_FILES = ['.DS_Store'];

export type FileAccept =
  | 'text/csv'
  | 'text/plain'
  | 'text/html'
  | 'text/markdown'
  | 'text/tab-separated-values'
  | 'application/msword'
  | 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  | 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  | 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
  | 'application/json'
  | 'application/ld+json'
  | 'application/pdf'
  | 'application/epub+zip';

export type DragDropFileInputProps = {
  id?: string;
  name?: string;
  label?: ReactNode;
  subLabel?: string;
  dragActiveLabel?: string;
  dragActiveDefault?: boolean;
  required?: boolean;
  accept?: FileAccept[];
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  multiple?: boolean;
  onDrop?: (files: File[]) => void | Promise<void>;
};

/**
 * File input that allows for drag and drop
 */
export const DragDropFileInput: React.FC<DragDropFileInputProps> = ({
  id,
  label = (
    <>
      Drag and drop files here or <u>browse files</u>
    </>
  ),
  subLabel = '.PDF or .TXT, Max 20MB',
  dragActiveLabel = 'Drop files to upload',
  dragActiveDefault = false,
  name,
  required,
  accept = ['application/pdf', 'text/plain'],
  placeholder = '',
  disabled = false,
  readOnly = false,
  multiple = false,
  className,
  onDrop,
}) => {
  const [dragActive, setDragActive] = useState(dragActiveDefault);

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
    onDrop?.(filesList);

    setDragActive(false);
  };
  return (
    <div
      className={cn(
        'relative flex h-28 w-full flex-col items-center justify-center rounded-md border border-mushroom-800 px-3 py-6',
        'transition duration-200',
        'border-dashed bg-mushroom-950',
        {
          'border-solid bg-mushroom-800': dragActive,
        },
        className
      )}
    >
      {dragActive ? (
        <Text className="max-w-[170px] text-center text-mushroom-300">{dragActiveLabel}</Text>
      ) : (
        <>
          <Text className="max-w-[210px] text-center text-mushroom-300">{label}</Text>
          <Text className="text-center text-mushroom-400" styleAs="caption">
            {subLabel}
          </Text>
        </>
      )}
      <input
        id={id}
        className="absolute left-0 top-0 h-full w-full opacity-0"
        type="file"
        multiple={multiple}
        accept={accept.toString()}
        name={name}
        required={required}
        placeholder={placeholder}
        disabled={disabled}
        readOnly={readOnly}
        onDragEnter={() => setDragActive(true)}
        onDragOver={() => setDragActive(true)}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      />
    </div>
  );
};
