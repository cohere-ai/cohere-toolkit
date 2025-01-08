'use client';

import { ComponentPropsWithoutRef, FC, useRef, useState } from 'react';
import { ExtraProps } from 'react-markdown';

import { Button, Icon, Text } from '@/components/UI';

export const Pre: FC<ComponentPropsWithoutRef<'pre'> & ExtraProps> = ({ children }) => {
  const [copied, setCopied] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const handleCopy = async () => {
    try {
      setCopied(true);
      const textToCopy = ref.current?.innerText || '';
      await window?.navigator?.clipboard.writeText(textToCopy);
    } catch (e) {
      console.error(e);
    }
    setTimeout(() => setCopied(false), 1000);
  };

  return (
    <pre className="group/copy relative">
      <Button
        kind="secondary"
        className="absolute right-3 top-3 hidden group-hover/copy:block"
        onClick={handleCopy}
        label={
          <div className="flex items-center gap-1">
            {copied && <Text className="text-mushroom-300 dark:text-marble-950">Copied!</Text>}
            <Icon
              name={copied ? 'checkmark' : 'copy'}
              size="md"
              className="fill-mushroom-300 dark:fill-marble-950"
            />
          </div>
        }
      />
      <div ref={ref}>{children}</div>
    </pre>
  );
};
