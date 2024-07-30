'use client';

import { ChangeEvent, MouseEvent, useRef, useState } from 'react';

import { InputLabel, Spinner, Text } from '@/components/Shared';
import { Icon } from '@/components/Shared/Icon';
import { cn } from '@/utils';

export type FileAccept =
  | '.csv'
  | '.txt'
  | '.html'
  | '.md'
  | '.tsv'
  | '.doc'
  | '.docx'
  | '.xlsx'
  | '.pptx'
  | '.json'
  | '.jsonl'
  | '.pdf'
  | '.epub';

type FileInputProps = {
  file?: File;
  label?: string;
  name?: string;
  required?: boolean;
  accept?: FileAccept[];
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  isLoading?: boolean;
  className?: string;
  children?: React.ReactNode;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveFile?: () => void;
};

export const FileInput: React.FC<FileInputProps> = ({
  file: initialFile,
  label,
  name,
  required,
  accept = ['.csv'],
  placeholder = '',
  disabled = false,
  readOnly = false,
  isLoading = false,
  className = '',
  children,
  onChange,
  onBlur,
  onRemoveFile,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | undefined>(initialFile);
  const [focused, setFocused] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }

    if (onChange) onChange(e);
  };

  const handleRemoveFile = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setFile(undefined);
    if (onRemoveFile) onRemoveFile();

    // Manually reset the value of the input element so we don't run into weird issues where you cannot re-upload after
    // removing a file since the input thinks it has the same value already.
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div
      className={cn(
        'flex flex-col',
        'rounded-lg border border-marble-800 bg-white',
        {
          'outline outline-1 outline-offset-4 outline-volcanic-400': focused,
          'text-volcanic-400': (placeholder && !file) || isLoading,
          'border-volcanic-100 text-volcanic-100': file && !isLoading,
          'cursor-not-allowed border-marble-800 bg-marble-950 text-volcanic-400': disabled,
        },
        className
      )}
    >
      <InputLabel
        label={label || children || ''}
        className={cn('px-3 pt-2.5', {
          'cursor-not-allowed text-volcanic-400': disabled,
          'cursor-pointer text-volcanic-100': !disabled,
        })}
        name="fileInput"
        onClick={(e) => {
          if (disabled) e.preventDefault();
        }}
      />

      <div className="relative px-3 pb-2.5">
        <div className="flex w-full items-center justify-between">
          <Text as="span" styleAs="p" className="truncate">
            {isLoading ? 'Uploading file...' : file ? file.name : placeholder}
          </Text>
          {isLoading ? (
            <Spinner className="my-0.5" />
          ) : file ? (
            <button
              className="z-10 ml-4 fill-volcanic-100 transition ease-in-out hover:fill-danger-350"
              type="button"
              onClick={handleRemoveFile}
            >
              <Icon name="trash" kind="outline" />
            </button>
          ) : (
            <span className="ml-4 h-[21px] fill-volcanic-100">
              <Icon name="upload" />
            </span>
          )}
        </div>

        <input
          id="fileInput"
          ref={inputRef}
          type="file"
          accept={accept.toString()}
          name={name}
          required={required}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          className={cn(
            'absolute left-0 top-0 h-full w-full opacity-0',
            'cursor-pointer disabled:cursor-not-allowed'
          )}
          onFocus={() => setFocused(true)}
          onBlur={(e) => {
            setFocused(false);
            onBlur?.(e);
          }}
          onChange={handleChange}
        />
      </div>
    </div>
  );
};
